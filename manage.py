import hashlib
import sys
import os
from lang_dict import get_language

HTPASSWD_FILE = "data/.htpasswd"

def load_users():
    users = {}
    if os.path.exists(HTPASSWD_FILE):
        with open(HTPASSWD_FILE, "r") as f:
            for line in f:
                username, hashed_pw, salt = line.strip().split(":")
                users[username] = {"hashed_pw": hashed_pw, "salt": salt}
    return users

def save_users(users):
    with open(HTPASSWD_FILE, "w") as f:
        for username, data in users.items():
            f.write(f"{username}:{data['hashed_pw']}:{data['salt']}\n")

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16) 
    else:
        salt = bytes.fromhex(salt)
    hashed_pw = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1
    )
    return hashed_pw.hex(), salt.hex() 

def add_user(username, password, lang):
    users = load_users()
    if username in users:
        print(f"{lang['user_exists']} {username}")
    else:
        hashed_pw, salt = hash_password(password)
        users[username] = {"hashed_pw": hashed_pw, "salt": salt}
        save_users(users)
        print(f"{lang['user_added']} {username}")

def delete_user(username, lang):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        print(f"{lang['user_deleted']} {username}")
    else:
        print(f"{lang['user_not_found']} {username}")

def update_user(username, password, lang):
    users = load_users()
    if username in users:
        hashed_pw, salt = hash_password(password)
        users[username] = {"hashed_pw": hashed_pw, "salt": salt}
        save_users(users)
        print(f"{lang['password_updated']} {username}")
    else:
        print(f"{lang['user_not_found']} {username}")

def list_users(lang):
    users = load_users()
    if users:
        print(lang['user_list'])
        for username in users.keys():
            print(f"- {username}")
    else:
        print(lang['no_users'])

def main():
    # Определяем текущий язык из переменной окружения
    lang_code = os.getenv('APP_LANGUAGE', 'en')
    lang = get_language(lang_code)

    if len(sys.argv) < 2:
        print(lang['usage'])
        sys.exit(1)

    command = sys.argv[1]

    if command == "add" and len(sys.argv) == 4:
        username = sys.argv[2]
        password = sys.argv[3]
        add_user(username, password, lang)
    elif command == "delete" and len(sys.argv) == 3:
        username = sys.argv[2]
        delete_user(username, lang)
    elif command == "update" and len(sys.argv) == 4:
        username = sys.argv[2]
        password = sys.argv[3]
        update_user(username, password, lang)
    elif command == "list":
        list_users(lang)
    else:
        print(lang['invalid_args'])
        sys.exit(1)

if __name__ == "__main__":
    main()
