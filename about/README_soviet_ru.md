# Простой сервер аутентификации на Docker'е 
(Товарищи, к бою готовьтесь!)

Дорогие товарищи! Этот сервер аутентификации был создан, чтобы обеспечить прозрачное управление пользователями и сессиями в обстановке товарищеского равенства и Docker'а, с помощью прогрессивного Nginx.

Сердце системы — Flask, а трудяга Gunicorn обеспечивает равномерное распределение нагрузок среди всех.

---

## Основные достижения коммунизма

- **Управление сессиями**:
  - Каждый товарищ получает сессионный токен (cookie) после успешного входа в систему.
  - Сессии действуют 10 минут, но мы продлим их, если вы докажете свою преданность (обновите страницу).
  - Если аутентификация неудачна — не переживайте, товарищи, вы сможете вернуться на страницу входа и попробовать снова.

- **Интеграция с Nginx**:
  - Проверяет идентификацию каждого товарища через `auth_request`.
  - Отказывает буржуазным элементам в доступе, перенаправляя их на страницу входа.

- **Хранение данных в Redis**:
  - Данные каждого товарища надежно хранятся в хранилище Redis, защищенном от буржуазной контрреволюции.
  - Конфигурация встроена в наш славный `compose.yaml`.

- **Индивидуальная настройка**:
  - Продолжительность сессий, их продление и другие параметры могут быть легко изменены через переменные окружения.
  - Поддерживаются статические и динамические пути для входа в систему и доступа к файлам.

---

## Как развернуть этот инструмент коммунизма

### Необходимые ресурсы

- Docker — это наш красный трактор для сборки контейнеров.
- Docker Compose — это орудие объединения контейнеров.
- Nginx — это наш крепкий забойщик запросов.

### План действий

1. **Клонировать наш великий репозиторий**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Настроить файл конфигурации (`./dsas.env`)**:

   ```env
   FLASK_ENV=production         # Режим Flask (развитие или производство)
   STYLE_FOLDER=dsas_static     # Путь к товарищеским стилям
   APP_LANGUAGE=soviet_ru       # Язык системы по умолчанию
   STYLE_THEME=soviet           # Тема (soviet — как Ленин завещал)
   SESSION_LIFETIME=600         # Время сессии (в секундах)
   SESSION_EXTENSION=300        # Продление сессии после успешного подтверждения
   SESSION_MAX_LIFETIME=86400   # Максимальное время сессии
   ```

3. **Запустить контейнеры**:

   ```bash
   docker-compose up -d
   ```

4. **Настроить Nginx**:
   
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

5. **_(Опционально)_ Обновить файл `/etc/hosts`**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## Как это работает

1. **Получение токена**:
   - Товарищ заходит на `/dsas_login`.
   - После успешного входа система выдаёт ему токен.

2. **Проверка сессий**:
   - Все запросы проверяются через `/dsas_auth`.
   - Если всё в порядке, время продляется, если нет — перенаправляем на страницу входа.

3. **Где хранятся данные**:
   - Redis надёжно хранит информацию о пользователях, их сессиях и времени начала работы.

---

## Управление пользователями

Для управления товарищами используйте `manage.py`.

### Команды

1. **Добавить нового товарища**:
   ```bash
   ./manage.sh add <имя_пользователя> <пароль>
   ```

2. **Удалить товарища**:
   ```bash
   ./manage.sh delete <имя_пользователя>
   ```

3. **Обновить пароль товарища**:
   ```bash
   ./manage.sh update <имя_пользователя> <новый_пароль>
   ```

4. **Список пользователей**:
   ```bash
   ./manage.sh list
   ```

---

## Замечания

- Данные пользователей находятся в `data/.htpasswd`.
- Все пароли хэшируются с использованием `scrypt`, надёжного, как КГБ.
- Подключите данные к `/app/data`, чтобы защитить их от буржуазных манипуляций.