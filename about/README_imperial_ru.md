# Простѣйшій серверъ аутентификаціи на Docker'ѣ

Сей репозиторій предоставляетъ серверъ для управления аутентификаціей пользователей и сессіями въ окруженіи контейнеровъ, основанномъ на Docker'ѣ и Nginx'ѣ.

Приложеніе работаетъ на Flask'ѣ, а распределеніе нагрузки внутри контейнера осуществляется черезъ Gunicorn.

---

## Главныя особенности

- **Управленіе сессіями**:
  - Пользователи получаютъ сессіонный токенъ (cookie) послѣ удачнаго входа.
  - По умолчанію, сессія дѣйствительна 10 минутъ, и продлевается автоматическїй съ каждою успѣшною запросомъ.
  - При неудачной аутентификаціи пользователи перенаправляются на страницу входа.

- **Интеграція съ Nginx**:
  - Обрабатываетъ запросы аутентификаціи черезъ `auth_request`.
  - Неаутентифицированные пользователи перенаправляются на страницу входа.

- **Храненіе данныхъ въ Redis**:
  - Redis используется для сохраненія данныхъ сессій.
  - Конфигурація Redis встроена въ `compose.yaml`.

- **Настраиваемость**:
  - Продолжительность сессій, время ихъ продленія и иные параметры можно настроить черезъ перемѣнныя окруженія.
  - Поддерживаются статическіе и динамическіе пути для страницы входа и статическихъ файловъ.

---

## Развёртываніе

### Требованія

- Docker
- Docker Compose
- Nginx

### Какъ запустить

1. **Клонируйте репозиторій**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Настройте окруженіе (`./dsas.env`)**:

   ```env
   FLASK_ENV=production         # Режимъ Flask (development/production)
   STYLE_FOLDER=dsas_static     # Путь къ статическимъ стилямъ
   APP_LANGUAGE=imperial_ru     # Языкъ приложенія по умолчанію
   STYLE_THEME=imperial         # Тема (light/dark/imperial/soviet/cyberpunk/glass)
   SESSION_LIFETIME=600         # Продолжительность сессіи (въ секундахъ)
   SESSION_EXTENSION=300        # Время продленія послѣ аутентификаціи (въ секундахъ)
   SESSION_MAX_LIFETIME=86400   # Максимальная продолжительность сессіи (въ секундахъ)
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

        ## Здесь ваш код ##
        proxy_pass http://127.0.0.1:8080; # <- Пример
    }

    # "dsas_login" может быть любым, но должен совпадать с @login
    location /dsas_login {
        proxy_pass http://127.0.0.1:5000/login;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Локация для статического контента, определена в dsas.env
    location /dsas_static/ {
        proxy_pass http://127.0.0.1:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # "dsas_auth" должно совпадать с директивой auth_request
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

5. **_(опціонально)_ Обновите файл `/etc/hosts`**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## Какъ это работаетъ

1. **Входъ и выдача токеновъ**:
   - Пользователи входятъ черезъ `/dsas_login`.
   - Послѣ успѣшнаго входа они получаютъ сессіонный токенъ.

2. **Провѣрка сессій**:
   - Всѣ запросы проходятъ черезъ `/dsas_auth`.
   - Успѣшно? Продляемъ время. Ошибка? Возвращаемъ на страницу входа.

3. **Гдѣ хранятся данные?**:
   - Redis хранитъ ID сессіи, данные пользователя и время начала.

---

## Управленіе пользователями

Используйте скриптъ `manage.py`, расположенный въ корневой папкѣ проекта, для управленія пользователями.

### Доступныя команды

1. **Добавить нового пользователя**:
   ```bash
   ./manage.sh add <имя_пользователя> <пароль>
   ```

2. **Удалить существующаго пользователя**:
   ```bash
   ./manage.sh delete <имя_пользователя>
   ```

3. **Обновить пароль пользователя**:
   ```bash
   ./manage.sh update <имя_пользователя> <новый_пароль>
   ```

4. **Списокъ всѣхъ пользователей**:
   ```bash
   ./manage.sh list
   ```

---

## Настройки

Для исползованія собстеннаго Redis-сервера обновите слѣдующую строку въ `app.py`:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="ваш_redis_host", port=6379, decode_responses=True)
```

---

## Замътки

- Данные о пользователяхъ хранятся въ `data/.htpasswd`.
- Пароли защищены черезъ хэшированіе съ использованиемъ `scrypt`.
- Подключите свои данные къ `/app/data`, дабы не потерять ихъ при перезапускѣ контейнеровъ.