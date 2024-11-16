# Einfacher Authentifizierungsserver mit Docker

Dieses Repository bietet einen Authentifizierungsserver, der für die Benutzer-Authentifizierung und Sitzungsverwaltung in einer containerisierten Umgebung mit Docker und Nginx entwickelt wurde.

Die Anwendung basiert auf dem Flask-Modul, und das Load-Balancing wird innerhalb des Containers von Gunicorn durchgeführt.

---

## Hauptfunktionen

- **Sitzungsverwaltung**:
  - Benutzer erhalten nach erfolgreicher Anmeldung ein Sitzungstoken (Cookie).
  - Sitzungen haben standardmäßig eine Lebensdauer von 10 Minuten, die nach jeder erfolgreichen Anfrage automatisch verlängert wird.
  - Bei fehlgeschlagener Authentifizierung werden Benutzer auf die Anmeldeseite weitergeleitet.

- **Nginx-Integration**:
  - Verarbeitet Authentifizierungsanfragen über `auth_request`.
  - Leitet nicht authentifizierte Benutzer auf die Anmeldeseite um.

- **Redis-basiertes Speichern**:
  - Redis wird zur Speicherung von Sitzungsdaten verwendet.
  - Eine integrierte Redis-Konfiguration ist in `compose.yaml` enthalten.

- **Anpassbar**:
  - Sitzungsdauer, Verlängerungszeit und andere Einstellungen können über Umgebungsvariablen konfiguriert werden.
  - Unterstützt statische und dynamische Pfade für die Anmeldeseite und statische Dateien.

---

## Bereitstellung

### Voraussetzungen

- Docker
- Docker Compose
- Nginx

### Anwendung starten

1. **Repository klonen**:

   ```bash
   git clone <repository_url>
   cd <repository_folder>
   docker buildx build -t auth_server .
   ```

2. **Umgebungsvariablen konfigurieren (Datei `./dsas.env`)**:

   ```env
   FLASK_ENV=production         # Flask-Modus (development/production)
   STYLE_FOLDER=dsas_static     # Pfad zu statischen Dateien
   APP_LANGUAGE=de              # Standardsprache der Anwendung
   STYLE_THEME=light            # Standarddesign (light/dark/imperial/soviet/cyberpunk/glass)
   SESSION_LIFETIME=600         # Standardmäßige Sitzungsdauer (in Sekunden)
   SESSION_EXTENSION=300        # Sitzungsverlängerung nach erfolgreicher Authentifizierung
   SESSION_MAX_LIFETIME=86400   # Maximale Sitzungsdauer (in Sekunden)
   ```

3. **Container starten**:

   ```bash
   docker-compose up -d
   ```

4. **Nginx konfigurieren**:

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

5. **_(optional)_ Aktualisieren Sie die Datei `/etc/hosts`**:

   ```bash
   127.0.0.1 authtest.local
   ```

---

## Funktionsweise

1. **Anmeldung und Token-Ausgabe**:
   - Benutzer melden sich über `/dsas_login` an.
   - Nach erfolgreicher Anmeldung erhalten sie ein Sitzungstoken, das in einem Cookie gespeichert wird.

2. **Sitzungsvalidierung**:
   - Alle Anfragen werden über `/dsas_auth` authentifiziert.
   - Bei erfolgreicher Validierung wird die Sitzungsdauer verlängert.
   - Bei einem Fehler werden Benutzer auf die Anmeldeseite umgeleitet.

3. **Speicherung der Sitzungsdaten**:
   - Sitzungsdaten werden in Redis gespeichert.
   - Redis speichert die Sitzungs-ID, Benutzerdaten und den Startzeitpunkt der Sitzung.

---

## Benutzerverwaltung mit `manage.py`

Verwenden Sie das Skript `manage.py` im Stammverzeichnis des Projekts, um Benutzer zu verwalten.

### Verfügbare Befehle

1. **Neuen Benutzer hinzufügen**:
   ```bash
   ./manage.sh add <benutzername> <passwort>
   ```

2. **Bestehenden Benutzer löschen**:
   ```bash
   ./manage.sh delete <benutzername>
   ```

3. **Passwort eines Benutzers aktualisieren**:
   ```bash
   ./manage.sh update <benutzername> <neues_passwort>
   ```

4. **Alle Benutzer auflisten**:
   ```bash
   ./manage.sh list
   ```

---

## Konfiguration

Um einen benutzerdefinierten Redis-Server zu verwenden, ändern Sie die folgende Zeile in `app.py`:

```python
app.config["SESSION_REDIS"] = redis.StrictRedis(host="ihr_redis_host", port=6379, decode_responses=True)
```

---

## Hinweise

- Benutzerdaten werden in `data/.htpasswd` gespeichert.
- Passwörter werden sicher mit dem `scrypt`-Algorithmus gehasht.
- Stellen Sie sicher, dass Volumes an `/app/data` angehängt sind, um Daten nach dem Neustart von Containern zu speichern.