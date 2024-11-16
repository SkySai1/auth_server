# Servidor de autenticación simple con Docker

Este repositorio proporciona un servidor de autenticación diseñado para gestionar la autenticación de usuarios y la administración de sesiones en un entorno de contenedores utilizando Docker y Nginx.

La aplicación está basada en el módulo Flask, y el balanceo de carga se realiza dentro del contenedor utilizando Gunicorn.

---

## Funciones principales

- **Gestión de sesiones**:
  - Los usuarios reciben un token de sesión (cookie) después de autenticarse con éxito.
  - Las sesiones tienen una duración predeterminada de 10 minutos, que se renueva automáticamente después de cada solicitud exitosa.
  - Si la autenticación falla, los usuarios son redirigidos a la página de inicio de sesión.

- **Integración con Nginx**:
  - Gestiona las solicitudes de autenticación a través de `auth_request`.
  - Redirige a los usuarios no autenticados a la página de inicio de sesión.

- **Almacenamiento en Redis**:
  - Redis se utiliza para almacenar los datos de las sesiones.
  - Una configuración integrada de Redis está incluida en `compose.yaml`.

- **Personalizable**:
  - La duración de las sesiones, el tiempo de extensión y otros parámetros se pueden configurar a través de variables de entorno.
  - Admite rutas estáticas y dinámicas para la página de inicio de sesión y los archivos estáticos.

---

## Despliegue

### Requisitos previos

- Docker
- Docker Compose
- Nginx

### Inicio de la aplicación

1. **Clonar el repositorio**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Configurar variables de entorno (archivo `./dsas.env`)**:

   ```env
   FLASK_ENV=production         # Modo de Flask (desarrollo/producción)
   STYLE_FOLDER=dsas_static     # Ruta a los archivos estáticos
   APP_LANGUAGE=es              # Idioma predeterminado de la aplicación
   STYLE_THEME=light            # Tema predeterminado (light/dark/imperial/soviet/cyberpunk/glass)
   SESSION_LIFETIME=600         # Duración predeterminada de las sesiones (en segundos)
   SESSION_EXTENSION=300        # Extensión de la sesión tras autenticación exitosa
   SESSION_MAX_LIFETIME=86400   # Duración máxima de las sesiones (en segundos)
   ```

3. **Iniciar los contenedores**:

   ```bash
   docker-compose up -d
   ```

4. **Configurar Nginx**:

```nginx
server {
      server_name authtest.local;

      location @login {
        return 302 /dsas_login?next=$request_uri;
      }

      location / {
        auth_request /dsas_auth;
        error_page 401 500 = @login;

        ## Su código está aquí ##
        proxy_pass http://127.0.0.1:8080; # <- Ejemplo
    }

    # "dsas_login" puede tener cualquier nombre, pero debe coincidir con @login
    location /dsas_login {
        proxy_pass http://127.0.0.1:5000/login;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Ubicación del contenido estático definido en dsas.env
    location /dsas_static/ {
        proxy_pass http://127.0.0.1:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # "dsas_auth" debe coincidir con la directiva auth_request
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

5. **_(opcional)_ Actualizar el archivo `/etc/hosts`**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## Cómo funciona

1. **Inicio de sesión y emisión de token**:
   - Los usuarios inician sesión a través de `/dsas_login`.
   - Después de un inicio de sesión exitoso, reciben un token de sesión almacenado en una cookie.

2. **Validación de sesiones**:
   - Todas las solicitudes son autenticadas a través de `/dsas_auth`.
   - Si la validación es exitosa, se extiende la duración de la sesión.
   - En caso de fallo, los usuarios son redirigidos a la página de inicio de sesión.

3. **Almacenamiento de sesiones**:
   - Los datos de las sesiones se almacenan en Redis.
   - Redis guarda el ID de la sesión, los datos del usuario y la hora de inicio de la sesión.

---

## Gestión de usuarios con `manage.py`

Para gestionar usuarios, utilice el script `manage.py` ubicado en la raíz del proyecto.

### Comandos disponibles

1. **Agregar un nuevo usuario**:
   ```bash
   ./manage.sh add <nombre_usuario> <contraseña>
   ```

2. **Eliminar un usuario existente**:
   ```bash
   ./manage.sh delete <nombre_usuario>
   ```

3. **Actualizar la contraseña de un usuario**:
   ```bash
   ./manage.sh update <nombre_usuario> <nueva_contraseña>
   ```

4. **Listar todos los usuarios**:
   ```bash
   ./manage.sh list
   ```

---

## Configuración

Para usar un servidor Redis personalizado, modifique la siguiente línea en `app.py`:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="tu_host_redis", port=6379, decode_responses=True)
```

---

## Notas

- Los datos de los usuarios se almacenan en `data/.htpasswd`.
- Las contraseñas se almacenan de forma segura utilizando el algoritmo `scrypt`.
- Asegúrese de que los volúmenes estén adjuntos a `/app/data` para conservar los datos después de recrear los contenedores.