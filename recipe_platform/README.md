# 🍳 FreshCook Recipe Platform

Moderne Rezeptplattform mit FastAPI Backend und Vanilla JavaScript Frontend.

## ✨ Features

- 🔍 Erweiterte Rezeptsuche mit Filtern
- 👤 Benutzer-Authentifizierung (JWT)
- ⭐ Rezept-Bewertungen & Favoriten
- 📄 PDF-Export
- 🔒 DSGVO-konform (Datenexport & Löschung)
- 🌙 Dark Mode
- 📱 Responsive Design

## 🚀 Schnellstart

### Windows

**Einfachste Methode:**
```
Doppelklick auf: start.bat
```

Das war's! Die Website öffnet sich automatisch.

### Manuell

```bash
cd recipe_platform
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --reload --port 8888
```

Öffne: http://localhost:8888

## 📚 Tech Stack

- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: Vanilla JavaScript
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT Tokens
- **Server**: Uvicorn (ASGI)

## 📖 API Dokumentation

Nach dem Start verfügbar unter:
- **Swagger UI**: http://localhost:8888/api/v1/docs
- **ReDoc**: http://localhost:8888/api/v1/redoc

## 🧪 Tests

```bash
pytest
```

## 📦 Deployment

Siehe [DEPLOYMENT.md](DEPLOYMENT.md) für:
- Docker Setup
- Nginx Konfiguration
- PostgreSQL Migration
- Produktions-Deployment

## 🔒 Sicherheit

- ✅ JWT Authentifizierung
- ✅ Passwort-Hashing (bcrypt)
- ✅ Rate Limiting
- ✅ CORS-Schutz
- ✅ Security Headers
- ✅ Input-Sanitization
- ✅ SQL Injection Schutz

## 📝 Lizenz

MIT

## 👨‍💻 Entwicklung

```bash
# Server mit Auto-Reload
python -m uvicorn app.main:app --reload --port 8888

# Tests ausführen
pytest -v

# Code-Coverage
pytest --cov=app
```

## 🌐 Endpoints

### Öffentlich
- `GET /` - Frontend
- `GET /health` - Health Check
- `GET /api/v1/recipes/search` - Rezepte suchen
- `GET /api/v1/recipes/{id}` - Rezept abrufen
- `GET /api/v1/recipes/filters` - Filter-Optionen

### Authentifiziert
- `POST /api/v1/auth/register` - Registrierung
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/recipes` - Rezept erstellen
- `POST /api/v1/recipes/{id}/rate` - Rezept bewerten
- `POST /api/v1/recipes/{id}/favorite` - Favorit toggle
- `GET /api/v1/recipes/favorites/me` - Meine Favoriten

### DSGVO
- `POST /api/v1/gdpr/export` - Daten exportieren
- `POST /api/v1/gdpr/delete` - Account löschen

## 🛠️ Konfiguration

Siehe `.env` Datei:
```env
SECRET_KEY=<generiert>
DATABASE_URL=sqlite:///./data/recipes.db
ALLOWED_ORIGINS=http://localhost:8888
```

## 📊 Projekt-Struktur

```
recipe_platform/
├── app/
│   ├── api/          # API Endpoints
│   ├── core/         # Config & Security
│   ├── models/       # Database Models
│   ├── schemas/      # Pydantic Schemas
│   ├── services/     # Business Logic
│   └── middleware/   # Custom Middleware
├── static/           # CSS & JavaScript
├── tests/            # Unit Tests
├── data/             # SQLite Database
├── start.bat         # Windows Start Script
└── requirements.txt  # Dependencies
```

## 🤝 Contributing

Pull Requests sind willkommen!

## 📞 Support

Bei Fragen oder Problemen siehe:
- [START.md](START.md) - Detaillierte Startanleitung
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment Guide
- [README_FIXES.md](README_FIXES.md) - Behobene Fehler
