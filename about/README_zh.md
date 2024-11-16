# 基于 Docker 的简单认证服务器

本存储库提供了一个认证服务器，用于在使用 Docker 和 Nginx 的容器化环境中管理用户认证和会话管理。

该应用程序基于 Flask 模块运行，并通过容器内的 Gunicorn 进行负载均衡。

---

## 主要功能

- **会话管理**:
  - 用户在成功登录后会收到会话令牌 (cookie)。
  - 默认情况下，会话持续时间为 10 分钟，每次成功请求后会自动续期。
  - 如果认证失败，用户将被重定向到登录页面。

- **与 Nginx 集成**:
  - 通过 `auth_request` 处理认证请求。
  - 将未认证的用户重定向到登录页面。

- **基于 Redis 的存储**:
  - Redis 用于存储会话数据。
  - `compose.yaml` 中包含了内置的 Redis 配置。

- **可定制**:
  - 可以通过环境变量配置会话的持续时间、延长时间等其他设置。
  - 支持登录页面和静态文件的静态和动态路径。

---

## 部署

### 先决条件

- Docker
- Docker Compose
- Nginx

### 启动应用程序

1. **克隆存储库**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **配置环境变量 (`./dsas.env` 文件)**:

   ```env
   FLASK_ENV=production         # Flask 模式 (development/production)
   STYLE_FOLDER=dsas_static     # 静态文件路径
   APP_LANGUAGE=zh              # 应用程序默认语言
   STYLE_THEME=light            # 默认主题 (light/dark/imperial/soviet/cyberpunk/glass)
   SESSION_LIFETIME=600         # 默认会话持续时间 (秒)
   SESSION_EXTENSION=300        # 成功认证后会话延长时间 (秒)
   SESSION_MAX_LIFETIME=86400   # 会话最大持续时间 (秒)
   ```

3. **启动容器**:

   ```bash
   docker-compose up -d
   ```

4. **配置 Nginx**:

```nginx
server {
      server_name authtest.local;

      location @login {
        return 302 /dsas_login?next=$request_uri;
      }

      location / {
        auth_request /dsas_auth;
        error_page 401 500 = @login;

        ## 你的代码在这里 ##
        proxy_pass http://127.0.0.1:8080; # <- 示例
    }

    # "dsas_login" 可以是任意名称，但必须与 @login 一致
    location /dsas_login {
        proxy_pass http://127.0.0.1:5000/login;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # dsas.env 中定义的静态内容位置
    location /dsas_static/ {
        proxy_pass http://127.0.0.1:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # "dsas_auth" 必须与 auth_request 指令一致
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

5. **_(可选)_ 更新 `/etc/hosts` 文件**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## 工作原理

1. **登录和令牌发放**:
   - 用户通过 `/dsas_login` 登录。
   - 登录成功后，他们会收到存储在 cookie 中的会话令牌。

2. **会话验证**:
   - 所有请求都通过 `/dsas_auth` 进行认证。
   - 如果验证成功，会话的持续时间将被延长。
   - 如果失败，用户将被重定向到登录页面。

3. **会话数据存储**:
   - 会话数据存储在 Redis 中。
   - Redis 存储会话 ID、用户数据和会话开始时间。

---

## 使用 `manage.py` 管理用户

要管理用户，请使用位于项目根目录的 `manage.py` 脚本。

### 可用命令

1. **添加新用户**:
   ```bash
   ./manage.sh add <用户名> <密码>
   ```

2. **删除现有用户**:
   ```bash
   ./manage.sh delete <用户名>
   ```

3. **更新用户密码**:
   ```bash
   ./manage.sh update <用户名> <新密码>
   ```

4. **列出所有用户**:
   ```bash
   ./manage.sh list
   ```

---

## 配置

要使用自定义 Redis 服务器，请修改 `app.py` 中的以下行:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="你的_redis_host", port=6379, decode_responses=True)
```

---

## 注意事项

- 用户数据存储在 `data/.htpasswd` 中。
- 密码通过 `scrypt` 算法安全地哈希存储。
- 请确保将数据卷挂载到 `/app/data`，以在容器重新创建后保留数据。