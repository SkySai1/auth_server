
# Простой докер-сервер аутентификации

Этот репозиторий предоставляет сервер аутентификации, предназначенный для управления аутентификацией пользователей и сессиями в контейнерной среде с использованием Docker и Nginx.

Приложение работает на базе Flask с балансировкой нагрузки через Gunicorn внутри контейнера.

---

## Основные возможности

- **Управление сессиями**:
  - Пользователи получают токен сессии (cookie) после успешной аутентификации.
  - Сессии имеют стандартное время жизни в 10 минут, которое автоматически продлевается при каждом успешном запросе.
  - При неуспешной аутентификации пользователи перенаправляются на страницу входа.

- **Интеграция с Nginx**:
  - Аутентификация запросов через `auth_request`.
  - Перенаправление неаутентифицированных пользователей на страницу входа.

- **Хранение сессий в Redis**:
  - Redis используется для хранения данных сессий.
  - Встроенная конфигурация Redis включена в `compose.yaml`.

- **Настраиваемость**:
  - Время жизни сессии, её продление и другие параметры задаются через переменные окружения.
  - Поддерживаются статические и динамические пути для страницы входа и статических файлов.

---

## Развертывание

### Требования

- Docker
- Docker Compose
- Nginx

### Запуск приложения

1. **Клонируйте репозиторий**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Настройте переменные окружения (файл `./dsas.env`)**:

   ```env
   # Режим работы Flask (development/production)
   FLASK_ENV=production

   # Путь к статическим стилям
   STYLE_FOLDER=dsas_static

   # Язык по умолчанию (en/ru/fr/de/es/it/zh)
   # Специальные языки: "redneck_us, irish_gang, imperial_ru, soviet_ru"
   APP_LANGUAGE=ru

   # Тема оформления (light/dark/imperial/soviet/cyberpunk/glass)
   STYLE_THEME=light

   # Время жизни сессий
   SESSION_LIFETIME=600        # Время жизни по умолчанию
   SESSION_EXTENSION=300       # Продление сессии после успешной аутентификации
   SESSION_MAX_LIFETIME=86400  # Максимальное время жизни
   ```

3. **Запустите контейнеры**:

   ```bash
   docker-compose up -d
   ```

4. **Настройте Nginx**:

   ```nginx
   server {
       server_name authtest.local;

       location @login {
           return 302 /dsas_login?next=$request_uri;
       }

       location / {
           auth_request /dsas_auth;
           error_page 401 500 = @login;

           # Ваш код начинается здесь
           proxy_pass http://127.0.0.1:8080; # <- Пример
           # Ваш код заканчивается здесь
       }

       location /dsas_login {
           proxy_pass http://127.0.0.1:5000/login;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /dsas_static/ {
           proxy_pass http://127.0.0.1:5000/static/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location = /dsas_auth {
           internal;
           proxy_pass http://127.0.0.1:5000/check_token;
           proxy_set_header X-Original-URI $request_uri;
           proxy_set_header Cookie $http_cookie;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **_(опционально)_ Обновите файл `/etc/hosts`**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## Как это работает

1. **Вход и выдача токена**:
    - Пользователи входят через `/dsas_login`.
    - При успешном входе они получают токен сессии, который сохраняется в cookie.

2. **Проверка сессии**:
    - Все запросы проходят проверку на конечной точке `/dsas_auth`.
    - При успешной проверке время жизни сессии продлевается.
    - При неуспешной проверке пользователи перенаправляются на страницу входа.

3. **Хранение данных сессии**:
    - Данные сессий хранятся в Redis.
    - Redis хранит идентификатор сессии, данные пользователя и время начала сессии.

---

## Управление пользователями с помощью `manage.py`

Для управления пользователями используйте скрипт `manage.py`, расположенный в корневой папке проекта.

### Доступные команды

1. **Добавить нового пользователя**:
   ```bash
   ./manage.sh add <username> <password>
   ```

2. **Удалить существующего пользователя**:
   ```bash
   ./manage.sh delete <username>
   ```

3. **Обновить пароль пользователя**:
   ```bash
   ./manage.sh update <username> <new_password>
   ```

4. **Вывести список пользователей**:
   ```bash
   ./manage.sh list
   ```

### Примечания

- **Данные пользователей**:
  - Данные о пользователях хранятся в `data/.htpasswd`.
  - Пароли надёжно хэшируются с использованием алгоритма `scrypt`.
  - Убедитесь, что для сохранения данных после пересоздания контейнера вы используете тома, подключённые к `/app/data`.

- **Работа скрипта**:
  - Скрипт работает только при имени контейнера `auth_server`. 
  - Если имя контейнера другое, используйте:
    ```bash
    docker exec -it <имя_вашего_контейнера> python manage.py
    ```

---

## Настройки

Чтобы использовать собственный сервер Redis, обновите следующую строку в `app.py`:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="your_redis_host", port=6379, decode_responses=True)
```
