# Simple Auth Server with Docker (Oi! Get Yer Login Sorted!)

Alright, lad? This here’s a server fer sortin’ out who’s who an’ keepin’ tabs on ‘em, Docker-style, with a bit o' Nginx thrown in.

It’s runnin’ on Flask, with Gunicorn takin’ care o' the heavy liftin’.

---

## The Craic

- **Keepin’ Track of the Lot**:
  - When ya log in proper, ye get a cookie. A proper one, not from yer gran’s tin.
  - These cookies last 10 minutes, and we’ll keep ‘em fresh as long as ye behave.
  - Cock up yer login? Back to signin’ ye go, sharpish.

- **Nginx Watchdog**:
  - Handles yer “are ya who ya say ya are” through `auth_request`.
  - No creds? Back to signin’, mate.

- **Redis Stash**:
  - Yer details are stashed in Redis, nice an’ secure.
  - The setup’s baked right into `compose.yaml`, so no faffin’ about.

- **Custom Bits**:
  - Tweak yer session times, extensions, and the like with a few env variables.
  - Static or dynamic paths? We got yer back.

---

## Gettin’ It Goin’

### What Ya Need

- Docker
- Docker Compose
- Nginx

### Fire It Up

1. **Grab the Goods**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Sort Yer Configs (`./dsas.env`)**:

   ```env
   FLASK_ENV=production         # Flask mode (development or production)
   STYLE_FOLDER=dsas_static     # Where yer styles live
   APP_LANGUAGE=irish_gang      # Default lingo
   STYLE_THEME=light            # Pick yer look (light/dark/imperial/soviet/cyberpunk/glass)
   SESSION_LIFETIME=600         # How long we let ya sit (seconds)
   SESSION_EXTENSION=300        # Extra time fer good behavior (seconds)
   SESSION_MAX_LIFETIME=86400   # Max sit-in time (seconds)
   ```

3. **Spin It Up**:

   ```bash
   docker-compose up -d
   ```

4. **Sort Out Nginx**:

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

5. **_(Optional)_ Tell Yer Machine About It**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## How It Works, Lads

1. **Signin’ and Token Handouts**:
   - Ye signin’ at `/dsas_login`.
   - Get it right, and ye get a cookie fer yer trouble.

2. **Session Checkin’**:
   - Every ask goes through `/dsas_auth`.
   - Pass the check? Yer time gets topped up. Mess it up? Back to signin’, ya muppet.

3. **Keepin’ Yer Stuff**:
   - Redis holds yer session ID, yer name, and when ya showed up.

---

## Wranglin’ Yer Crew

Use the `manage.py` script in the project folder to keep yer lot in line.

### What Ya Can Do

1. **Add New Faces**:
   ```bash
   ./manage.sh add <name> <password>
   ```

2. **Boot Someone Out**:
   ```bash
   ./manage.sh delete <name>
   ```

3. **Change a Lad’s Secret**:
   ```bash
   ./manage.sh update <name> <new_password>
   ```

4. **See Who’s About**:
   ```bash
   ./manage.sh list
   ```

---

## Tweak the Setup

Got yer own Redis stash? Update this in `app.py`:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="your_redis_host", port=6379, decode_responses=True)
```

---

## Heads-Up

- Crew info’s kept in `data/.htpasswd`.
- Secrets are hashed nice and proper with `scrypt`.
- Mount yer data to `/app/data` so it don’t vanish after a reboot.