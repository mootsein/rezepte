# Deployment-Anleitung

## Produktions-Deployment

### 1. Umgebungsvariablen

Erstelle eine `.env` Datei mit Produktionswerten:

```bash
# Sicherheit - WICHTIG: Neuen SECRET_KEY generieren!
SECRET_KEY=<generiere-mit-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Datenbank - PostgreSQL empfohlen
DATABASE_URL=postgresql://user:password@localhost/recipedb

# CORS - Nur deine Domain(s)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# DSGVO
DATA_RETENTION_DAYS=365
GDPR_EXPORT_ENABLED=true

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_WINDOW_MINUTES=15

# Logging
LOG_LEVEL=WARNING
```

### 2. PostgreSQL Setup

```bash
# PostgreSQL installieren
sudo apt-get install postgresql postgresql-contrib

# Datenbank erstellen
sudo -u postgres psql
CREATE DATABASE recipedb;
CREATE USER recipeuser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE recipedb TO recipeuser;
\q

# In .env anpassen
DATABASE_URL=postgresql://recipeuser:secure_password@localhost/recipedb
```

### 3. Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/recipe_platform/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4. Systemd Service

Erstelle `/etc/systemd/system/recipeapp.service`:

```ini
[Unit]
Description=Recipe Platform API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/recipe_platform
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable recipeapp
sudo systemctl start recipeapp
sudo systemctl status recipeapp
```

### 5. SSL mit Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 6. Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Docker Deployment (Alternative)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://recipeuser:password@db:5432/recipedb
    depends_on:
      - db
    volumes:
      - ./data:/app/data
      - ./app.log:/app/app.log
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=recipedb
      - POSTGRES_USER=recipeuser
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

Start:
```bash
docker-compose up -d
```

## Monitoring

### Log-Rotation

Erstelle `/etc/logrotate.d/recipeapp`:

```
/path/to/recipe_platform/app.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload recipeapp
    endscript
}
```

### Health-Check Monitoring

```bash
# Cron-Job für Health-Check
*/5 * * * * curl -f https://yourdomain.com/health || echo "Health check failed" | mail -s "Recipe App Down" admin@yourdomain.com
```

## Backup

### Datenbank-Backup

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/recipedb"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -U recipeuser recipedb > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

Cron:
```bash
0 2 * * * /path/to/backup.sh
```

## Performance-Tuning

### Gunicorn statt Uvicorn (optional)

```bash
pip install gunicorn

# Start
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Redis für Caching (optional)

```bash
sudo apt-get install redis-server
pip install redis

# In Code integrieren für Filter-Caching
```

## Sicherheits-Checkliste

- [ ] SECRET_KEY geändert und sicher gespeichert
- [ ] CORS auf spezifische Domains beschränkt
- [ ] HTTPS aktiviert (SSL-Zertifikat)
- [ ] Firewall konfiguriert
- [ ] Datenbank-Passwörter sicher
- [ ] Log-Rotation aktiviert
- [ ] Backups eingerichtet
- [ ] Health-Check Monitoring aktiv
- [ ] Security Headers gesetzt (Nginx)
- [ ] Rate Limiting aktiviert
- [ ] Regelmäßige Updates geplant
