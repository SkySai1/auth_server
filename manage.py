import hashlib
import sys
import os

HTPASSWD_FILE = "data/.htpasswd"

def load_users():
    """Загружает пользователей из файла .htpasswd и возвращает словарь."""
    users = {}
    if os.path.exists(HTPASSWD_FILE):
        with open(HTPASSWD_FILE, "r") as f:
            for line in f:
                username, hashed_pw, salt = line.strip().split(":")
                users[username] = {"hashed_pw": hashed_pw, "salt": salt}
    return users

def save_users(users):
    """Сохраняет пользователей в файл .htpasswd."""
    with open(HTPASSWD_FILE, "w") as f:
        for username, data in users.items():
            f.write(f"{username}:{data['hashed_pw']}:{data['salt']}\n")

def hash_password(password, salt=None):
    """Хэширует пароль с использованием scrypt. Если соль не передана, генерируется новая."""
    if salt is None:
        salt = os.urandom(16)  # Генерация случайной соли размером 16 байт
    else:
        salt = bytes.fromhex(salt)
    hashed_pw = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1
    )
    return hashed_pw.hex(), salt.hex()  # Возвращаем хэш и соль в виде строки

def add_user(username, password):
    users = load_users()
    if username in users:
        print(f"Пользователь {username} уже существует.")
    else:
        hashed_pw, salt = hash_password(password)
        users[username] = {"hashed_pw": hashed_pw, "salt": salt}
        save_users(users)
        print(f"Пользователь {username} добавлен.")

def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        print(f"Пользователь {username} удален.")
    else:
        print(f"Пользователь {username} не найден.")

def update_user(username, password):
    users = load_users()
    if username in users:
        hashed_pw, salt = hash_password(password)
        users[username] = {"hashed_pw": hashed_pw, "salt": salt}
        save_users(users)
        print(f"Пароль пользователя {username} обновлен.")
    else:
        print(f"Пользователь {username} не найден.")

def list_users():
    users = load_users()
    if users:
        print("Список пользователей:")
        for username in users.keys():
            print(f"- {username}")
    else:
        print("Список пользователей пуст.")

def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  Добавить пользователя: python manage.py add <username> <password>")
        print("  Удалить пользователя: python manage.py delete <username>")
        print("  Обновить пароль: python manage.py update <username> <new_password>")
        print("  Список пользователей: python manage.py list")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add" and len(sys.argv) == 4:
        username = sys.argv[2]
        password = sys.argv[3]
        add_user(username, password)
    elif command == "delete" and len(sys.argv) == 3:
        username = sys.argv[2]
        delete_user(username)
    elif command == "update" and len(sys.argv) == 4:
        username = sys.argv[2]
        password = sys.argv[3]
        update_user(username, password)
    elif command == "list":
        list_users()
    else:
        print("Неверные аргументы.")
        sys.exit(1)

if __name__ == "__main__":
    main()
