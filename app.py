from flask import Flask, request, redirect, url_for, make_response, render_template, jsonify
import os
import redis
import uuid
import hashlib
from lang_dict import get_language

app = Flask(__name__, static_folder='static') 
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.StrictRedis(host="redis", port=6379, decode_responses=True)
app.config["SESSION_COOKIE_NAME"] = "x-auth-token"

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
    style_folder = os.getenv('STYLE_FOLDER', '/dsas_static')
    lang = get_current_language()
    next_url = request.args.get('next', '/') 
    error_message = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if check_credentials(username, password):

            session_id = str(uuid.uuid4())
            redis_conn = app.config["SESSION_REDIS"]
            redis_conn.set(session_id, username, ex=3600)

            response = make_response(redirect(next_url))
            response.set_cookie(app.config["SESSION_COOKIE_NAME"], session_id)
            return response
        else:
            error_message = lang['error_message']

    return render_template(
        'login.html', 
        error_message=error_message, 
        style_folder=style_folder,
        lang=lang
    )

@app.route('/check_token')
def check_token():
    session_cookie = request.cookies.get(app.config["SESSION_COOKIE_NAME"])

    if not session_cookie:
        return jsonify({"error": "No session cookie found"}), 401

    redis_conn = app.config["SESSION_REDIS"]
    username = redis_conn.get(session_cookie)

    if username:
        redis_conn.expire(session_cookie, 600) 
        return jsonify({"status": "success", "username": username}), 200
    else:
        return jsonify({"error": "Session not found or expired"}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
