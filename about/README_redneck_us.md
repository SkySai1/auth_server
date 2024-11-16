# Simple Login Server with Docker (Y’all Get in Here!)

Howdy, partner! This here’s a server for handlin’ user logins and sittin’ folks down in their sessions, all wrapped up in Docker and Nginx.

It runs on Flask, and that fancy Gunicorn thing helps balance the load so y’all ain’t crashin’ it.

---

## What’s Cookin’?

- **Session Wranglin’**:
  - Folks get a cookie token when they log in nice and proper.
  - Them cookies last 10 minutes, and we keep 'em fresh every time y’all make a request.
  - Mess up your login? Well, bless your heart – we’ll send ya back to the signin’ page.

- **Hookin’ Up with Nginx**:
  - Handles the checkin’ of who’s who with `auth_request`.
  - Ain’t got no proper ID? Back to signin’ you go!

- **Stashin’ with Redis**:
  - All your session info gets stashed in that there Redis.
  - The setup’s already in the `compose.yaml`, so you’re good to go.

- **Custom Fixins’**:
  - Change how long folks can sit around or tweak other settings with environment variables.
  - Static or dynamic, we got paths covered for signin’ and style files.

---

## Git ‘Er Done

### What You’ll Need

- Docker
- Docker Compose
- Nginx

### How to Get This Thing Rollin’

1. **Clone This Darn Repo**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Set Up Your Goodies (`./dsas.env`)**:

   ```env
   FLASK_ENV=production         # Flask mode (development or production)
   STYLE_FOLDER=dsas_static     # Where ya keep them style files
   APP_LANGUAGE=redneck_us      # Default tongue
   STYLE_THEME=light            # Choose yer theme (light/dark/imperial/soviet/cyberpunk/glass)
   SESSION_LIFETIME=600         # How long folks can hang out (in seconds)
   SESSION_EXTENSION=300        # Extra time for good behavior (in seconds)
   SESSION_MAX_LIFETIME=86400   # Max hangout time (in seconds)
   ```

3. **Fire Up Them Containers**:

   ```bash
   docker-compose up -d
   ```

4. **Hook Up Nginx**:

``nginx
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

5. **_(Optional)_ Tell Your Machine Where to Look**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## How It Works, Bubba

1. **Login and Cookie Handouts**:
   - Folks login at `/dsas_login`.
   - If ya do it right, you’ll get a cookie token.

2. **Keepin’ Tabs**:
   - Every request gets checked over `/dsas_auth`.
   - Pass the check? We’ll reset your timer. Fail? Back to signin’, sugar.

3. **Where’s My Stuff?**:
   - Redis keeps yer session ID, user info, and when ya sat down.

---

## Manage Yer Users

Use the `manage.py` script in the main folder to wrangle users.

### What You Can Do

1. **Add New Folks**:
   ```bash
   ./manage.sh add <username> <password>
   ```

2. **Kick Someone Out**:
   ```bash
   ./manage.sh delete <username>
   ```

3. **Change Someone’s Secret**:
   ```bash
   ./manage.sh update <username> <new_password>
   ```

4. **See Who’s Around**:
   ```bash
   ./manage.sh list
   ```

---

## Tweak the Setup

Wanna use yer own Redis? Change this in `app.py`:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="your_redis_host", port=6379, decode_responses=True)
```

---

## Heads Up

- User info goes in `data/.htpasswd`.
- Passwords are hashed all fancy-like with `scrypt`.
- Hook up your data to `/app/data` so it don’t go missin’.