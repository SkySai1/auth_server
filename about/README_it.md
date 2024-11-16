# Server di autenticazione semplice con Docker

Questo repository fornisce un server di autenticazione progettato per gestire l'autenticazione degli utenti e la gestione delle sessioni in un ambiente containerizzato utilizzando Docker e Nginx.

L'applicazione si basa sul modulo Flask e il bilanciamento del carico viene effettuato all'interno del container tramite Gunicorn.

---

## Funzionalità principali

- **Gestione delle sessioni**:
  - Gli utenti ricevono un token di sessione (cookie) dopo un'autenticazione riuscita.
  - Le sessioni hanno una durata predefinita di 10 minuti, che viene automaticamente rinnovata dopo ogni richiesta riuscita.
  - In caso di autenticazione non riuscita, gli utenti vengono reindirizzati alla pagina di accesso.

- **Integrazione con Nginx**:
  - Gestisce le richieste di autenticazione tramite `auth_request`.
  - Reindirizza gli utenti non autenticati alla pagina di accesso.

- **Archiviazione in Redis**:
  - Redis viene utilizzato per archiviare i dati delle sessioni.
  - Una configurazione Redis integrata è inclusa in `compose.yaml`.

- **Personalizzabile**:
  - La durata delle sessioni, il tempo di estensione e altri parametri possono essere configurati tramite variabili di ambiente.
  - Supporta percorsi statici e dinamici per la pagina di accesso e i file statici.

---

## Implementazione

### Prerequisiti

- Docker
- Docker Compose
- Nginx

### Avvio dell'applicazione

1. **Clonare il repository**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Configurare le variabili di ambiente (file `./dsas.env`)**:

   ```env
   FLASK_ENV=production         # Modalità Flask (development/production)
   STYLE_FOLDER=dsas_static     # Percorso ai file statici
   APP_LANGUAGE=it              # Lingua predefinita dell'applicazione
   STYLE_THEME=light            # Tema predefinito (light/dark/imperial/soviet/cyberpunk/glass)
   SESSION_LIFETIME=600         # Durata predefinita delle sessioni (in secondi)
   SESSION_EXTENSION=300        # Estensione della sessione dopo autenticazione riuscita
   SESSION_MAX_LIFETIME=86400   # Durata massima delle sessioni (in secondi)
   ```

3. **Avviare i container**:

   ```bash
   docker-compose up -d
   ```

4. **Configurare Nginx**:

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

5. **_(opzionale)_ Aggiornare il file `/etc/hosts`**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## Come funziona

1. **Accesso e emissione del token**:
   - Gli utenti accedono tramite `/dsas_login`.
   - Dopo un accesso riuscito, ricevono un token di sessione memorizzato in un cookie.

2. **Validazione della sessione**:
   - Tutte le richieste sono autenticate tramite `/dsas_auth`.
   - In caso di validazione riuscita, la durata della sessione viene estesa.
   - In caso di errore, gli utenti vengono reindirizzati alla pagina di accesso.

3. **Archiviazione delle sessioni**:
   - I dati delle sessioni sono archiviati in Redis.
   - Redis memorizza l'ID della sessione, i dati dell'utente e l'orario di inizio della sessione.

---

## Gestione degli utenti con `manage.py`

Per gestire gli utenti, utilizzare lo script `manage.py` situato nella directory principale del progetto.

### Comandi disponibili

1. **Aggiungere un nuovo utente**:
   ```bash
   ./manage.sh add <nome_utente> <password>
   ```

2. **Eliminare un utente esistente**:
   ```bash
   ./manage.sh delete <nome_utente>
   ```

3. **Aggiornare la password di un utente**:
   ```bash
   ./manage.sh update <nome_utente> <nuova_password>
   ```

4. **Elencare tutti gli utenti**:
   ```bash
   ./manage.sh list
   ```

---

## Configurazione

Per utilizzare un server Redis personalizzato, modificare la seguente riga in `app.py`:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="tuo_host_redis", port=6379, decode_responses=True)
```

---

## Note

- I dati degli utenti sono archiviati in `data/.htpasswd`.
- Le password sono memorizzate in modo sicuro utilizzando l'algoritmo `scrypt`.
- Assicurarsi che i volumi siano collegati a `/app/data` per preservare i dati dopo la ricreazione dei container.