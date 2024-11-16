from flask import Flask, request, redirect, url_for, make_response, render_template, jsonify
import os
import redis
import uuid
import hashlib
from datetime import datetime, timedelta
from lang_dict import get_language

app = Flask(__name__, static_folder='static') 
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.StrictRedis(host="redis", port=6379, decode_responses=True)
app.config["SESSION_COOKIE_NAME"] = "x-auth-token"

# Настройки времени сессии
SESSION_LIFETIME = int(os.getenv('SESSION_LIFETIME', 3600))  # 1h by default
SESSION_EXTENSION = int(os.getenv('SESSION_EXTENSION', 600))  # 10m by default
SESSION_MAX_LIFETIME = int(os.getenv('SESSION_MAX_LIFETIME', 86400))  # 24h by default

HTPASSWD_FILE = "data/.htpasswd"

def check_credentials(username, password):
    if not os.path.exists(HTPASSWD_FILE):
        raise FileNotFoundError(f"Файл {HTPASSWD_FILE} не найден.")

    with open(HTPASSWD_FILE, 'r') as f:
        for line in f:
            stored_username, stored_hash, stored_salt = line.strip().split(":")
            if stored_username == username:
                salt = bytes.fromhex(stored_salt)
                computed_hash = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1).hex()
                if computed_hash == stored_hash:
                    return True
    return False

def get_current_language():
    lang_code = os.getenv('APP_LANGUAGE', 'en')
    return get_language(lang_code)

@app.route('/login', methods=['GET', 'POST'])
def login():
    style_theme = os.getenv('STYLE_THEME', 'light') 
    style_folder = os.getenv('STYLE_FOLDER', '/dsas_static')
    style_path = f"{style_folder}/styles/{style_theme}.css"

    lang = get_current_language()
    next_url = request.args.get('next', '/') 
    error_message = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if check_credentials(username, password):
            session_id = str(uuid.uuid4())
            session_start_time = datetime.utcnow()
            redis_conn = app.config["SESSION_REDIS"]
            redis_conn.set(session_id, username, ex=SESSION_LIFETIME)
            redis_conn.set(f"{session_id}_start", session_start_time.isoformat())

            response = make_response(redirect(next_url))
            response.set_cookie(app.config["SESSION_COOKIE_NAME"], session_id)
            return response
        else:
            error_message = lang['error_message']

    return render_template(
        'login.html', 
        error_message=error_message, 
        style_path=style_path,
        lang=lang
    )

@app.route('/check_token')
def check_token():
    session_cookie = request.cookies.get(app.config["SESSION_COOKIE_NAME"])

    if not session_cookie:
        return jsonify({"error": "No session cookie found"}), 401

    redis_conn = app.config["SESSION_REDIS"]
    username = redis_conn.get(session_cookie)
    session_start_time = redis_conn.get(f"{session_cookie}_start")

    if not username or not session_start_time:
        return jsonify({"error": "Session not found or expired"}), 401

    session_start_time = datetime.fromisoformat(session_start_time)
    session_age = (datetime.utcnow() - session_start_time).total_seconds()

    if session_age > SESSION_MAX_LIFETIME:
        redis_conn.delete(session_cookie)
        redis_conn.delete(f"{session_cookie}_start")
        return jsonify({"error": "Session has exceeded its maximum lifetime"}), 401

    redis_conn.expire(session_cookie, SESSION_EXTENSION)
    redis_conn.expire(f"{session_cookie}_start", SESSION_EXTENSION)

    return jsonify({"status": "success", "username": username}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
