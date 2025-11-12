# 🍳 FreshCook Recipe Platform

Moderne Rezeptplattform mit FastAPI Backend und Vanilla JavaScript Frontend.

## 🚀 Schnellstart

```bash
cd recipe_platform
Doppelklick auf: start.bat
```

Die Website öffnet sich automatisch auf: http://localhost:8888

## 📁 Projekt-Struktur

```
Agiles Projektmanagement/
├── recipe_platform/          # Hauptanwendung
│   ├── app/                  # Backend (FastAPI)
│   ├── static/               # Frontend (CSS/JS)
│   ├── tests/                # Unit Tests
│   ├── data/                 # SQLite Datenbank
│   ├── .env                  # Umgebungsvariablen
│   ├── requirements.txt      # Python Dependencies
│   ├── start.bat            # Windows Start-Script
│   └── README.md            # Detaillierte Dokumentation
├── main.py                   # Alternative Einstiegspunkt
├── rezepte_100.csv          # Beispiel-Rezeptdaten
└── jira_*.csv/md            # Projekt-Dokumentation
```

## 📚 Dokumentation

Siehe `recipe_platform/` für:
- `README.md` - Vollständige Dokumentation
- `DEPLOYMENT.md` - Produktions-Deployment
- `CHANGELOG.md` - Versions-Historie
- `README_FIXES.md` - Behobene Fehler

## 🔧 Technologie-Stack

- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: Vanilla JavaScript
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT Tokens
- **Server**: Uvicorn (ASGI)

## ✨ Features

- Rezeptsuche mit Filtern
- User-Authentifizierung
- Bewertungen & Favoriten
- PDF-Export
- DSGVO-konform
- Dark Mode
- Mobile First Design

## 📞 Support

Bei Fragen siehe die Dokumentation in `recipe_platform/`
