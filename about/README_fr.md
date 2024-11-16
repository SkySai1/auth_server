# Serveur d'authentification simple sur Docker


Ce dépôt fournit un serveur d'authentification conçu pour gérer l'authentification des utilisateurs et la gestion des sessions dans un environnement conteneurisé utilisant Docker et Nginx.

L'application est basée sur le module Flask, et l'équilibrage de charge est assuré par Gunicorn à l'intérieur du conteneur.

---

## Fonctionnalités principales

- **Gestion des sessions** :
  - Les utilisateurs reçoivent un jeton de session (cookie) après une authentification réussie.
  - Les sessions ont une durée de vie par défaut de 10 minutes et sont automatiquement renouvelées après chaque requête réussie.
  - En cas d'échec de l'authentification, les utilisateurs sont redirigés vers la page de connexion.

- **Intégration avec Nginx** :
  - Gère les requêtes d'authentification via `auth_request`.
  - Redirige les utilisateurs non authentifiés vers la page de connexion.

- **Stockage basé sur Redis** :
  - Redis est utilisé pour stocker les données des sessions.
  - Une configuration Redis intégrée est incluse dans `compose.yaml`.

- **Personnalisation** :
  - La durée de vie des sessions, le temps d'extension et d'autres paramètres peuvent être configurés via des variables d'environnement.
  - Prend en charge des chemins statiques et dynamiques pour la page de connexion et les fichiers statiques.

---

## Déploiement

### Prérequis

- Docker
- Docker Compose
- Nginx

### Lancement de l'application

1. **Cloner le dépôt** :

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Configurer les variables d'environnement (fichier `./dsas.env`)** :

   ```env
   FLASK_ENV=production         # Mode de fonctionnement de Flask (développement/production)
   STYLE_FOLDER=dsas_static     # Chemin vers les fichiers statiques
   APP_LANGUAGE=fr              # Langue par défaut de l'application
   STYLE_THEME=light            # Thème par défaut (light/dark/imperial/soviet/cyberpunk/glass)
   SESSION_LIFETIME=600         # Durée de vie par défaut des sessions (en secondes)
   SESSION_EXTENSION=300        # Temps d'extension des sessions après authentification réussie
   SESSION_MAX_LIFETIME=86400   # Durée maximale des sessions (en secondes)
   ```

3. **Démarrer les conteneurs** :

   ```bash
   docker-compose up -d
   ```

4. **Configurer Nginx** :

   ```nginx
   server {
       server_name authtest.local;

       location @login {
           return 302 /dsas_login?next=$request_uri;
       }

       location / {
           auth_request /dsas_auth;
           error_page 401 500 = @login;
           proxy_pass http://127.0.0.1:8080;
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

5. **_(optionnel)_ Mettre à jour le fichier `/etc/hosts`** :

   ```bash
   127.0.0.1 authtest.local
   ```

---

## Fonctionnement

1. **Connexion et émission de jetons** :
   - Les utilisateurs se connectent via `/dsas_login`.
   - Après une connexion réussie, ils reçoivent un jeton de session stocké dans un cookie.

2. **Validation des sessions** :
   - Toutes les requêtes sont authentifiées via `/dsas_auth`.
   - En cas de validation réussie, la durée de vie de la session est prolongée.
   - En cas d'échec, les utilisateurs sont redirigés vers la page de connexion.

3. **Stockage des sessions** :
   - Les données des sessions sont stockées dans Redis.
   - Redis enregistre l'ID de session, les données utilisateur et l'heure de début de session.

---

## Gestion des utilisateurs avec `manage.py`

Pour gérer les utilisateurs, utilisez le script `manage.py` situé à la racine du projet.

### Commandes disponibles

1. **Ajouter un utilisateur** :
   ```bash
   ./manage.sh add <nom_utilisateur> <mot_de_passe>
   ```

2. **Supprimer un utilisateur existant** :
   ```bash
   ./manage.sh delete <nom_utilisateur>
   ```

3. **Mettre à jour le mot de passe d'un utilisateur** :
   ```bash
   ./manage.sh update <nom_utilisateur> <nouveau_mot_de_passe>
   ```

4. **Lister tous les utilisateurs** :
   ```bash
   ./manage.sh list
   ```

---

## Configuration

Pour utiliser un serveur Redis personnalisé, modifiez la ligne suivante dans `app.py` :

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="votre_hôte_redis", port=6379, decode_responses=True)
```

---

## Remarques

- Les données des utilisateurs sont stockées dans `data/.htpasswd`.
- Les mots de passe sont sécurisés et hachés à l'aide de l'algorithme `scrypt`.
- Assurez-vous que les volumes sont attachés à `/app/data` pour préserver les données après la recréation des conteneurs.