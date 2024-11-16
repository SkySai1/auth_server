# Docker Simple Authentication Server

This repository provides an authentication server designed to handle user authentication and session management in a containerized environment using Docker and Nginx.

The applications works on flask module, and load balancing by gunicorn inside container.

---

## Features

- **Session Management**: 
  - Users receive a session token (cookie) upon successful login.
  - Sessions have a default lifetime of 10 minutes, with automatic renewal on every successful request.
  - Failed authentication redirects users to the login page.

- **Nginx Integration**:
  - Handles authentication requests via `auth_request`.
  - Redirects unauthenticated users to the login page.

- **Redis Backed**:
  - Redis is used to store session data.
  - Built-in Redis setup included in the `docker-compose.yaml`.

- **Customizable**:
  - Session lifetime, extension time, and other settings are configurable via environment variables.
  - Supports static and dynamic paths for login and static files.

---

## Deployment

### Prerequisites

- Docker
- Docker Compose
- Nginx

### Running the Application

1. **Clone the Repository**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```
2. **Set Up Environment Variables ./dsas.env:**:

```python
# Flask environment mode (development/production)
FLASK_ENV=production

# Path to static styles
STYLE_FOLDER=dsas_static

# Default application language (en/ru/fr/de/es/it/zh)
# Special languages: "redneck_us, irish_gang, imperial_ru, soviet_ru"
APP_LANGUAGE=en

# Default style theme (light/dark/imperial/soviet/cyberpunk/glass)
STYLE_THEME=light

#SESSION TIMES
SESSION_LIFETIME=600        # Time to live by default
SESSION_EXTENSION=300       # Session exetnsion after successfull authentication
SESSION_MAX_LIFETIME=86400  # Max time to live
```

3. **Start the Containers:**:

```bash
docker-compose up -d
```

4. **Configure Nginx:**:

```nginx
server {
      server_name authtest.local;

      location @login {
        return 302 /dsas_login?next=$request_uri;
      }

      location / {
        auth_request /dsas_auth;
        error_page 401 500 = @login;

        ## Your code is here ##
        proxy_pass http://127.0.0.1:8080; # <- Example
    }

    # "dsas_login" can be named anything, but it must match @login
    location /dsas_login {
        proxy_pass http://127.0.0.1:5000/login;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static content location defined in dsas.env
    location /dsas_static/ {
        proxy_pass http://127.0.0.1:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # "dsas_auth" must match the auth_request directive
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

5. **_(optional)_ Update Your /etc/hosts File:**:

```bash
127.0.0.1 authtest.local
```
## How It Works

1. **Login and Token Issuance:**
    - Users log in at /dsas_login.
    - On successful login, they receive a session token stored in cookies.
2. **Session Validation:**
    - All requests are authenticated via the /dsas_auth endpoint.
    - If a session is valid, its lifetime is extended.
    - If a session is invalid, users are redirected to the login page.

3. **Session Storage:**
    - Session data is stored in Redis.
    - Redis stores the session ID, associated user data, and session start time.


## Managing Users with manage.py

To manage users in the authentication system, use the manage.py script located in the root of the project `./manage.sh`.

**Available Commands:**

1. Add new user: `./manage.sh add <username> <password>`

2. Delete an existing user: `./manage.sh delete <username>`

3. Update a user's password: `./manage.sh update <username> <new_password>`

4. List all users: `./manage.sh manage.py list`


**Notes**

Script only works when container's name is 'auth_server' if it's not then manage via command: `docker exec -it <your_container's_name> python manage.py`


User data is stored in `data/.htpasswd`. Passwords are securely hashed using the `scrypt` algorithm. For keeping data after container's recreate make sure that you are using volumes attached to `/app/data`

## Configuration Options

To use a custom Redis server, update the following line in app.py:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="your_redis_host", port=6379, decode_responses=True)
```

