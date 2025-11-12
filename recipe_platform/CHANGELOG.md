# Changelog

## [1.2.0] - 2024 - Design & Mobile First Update

### Neue Features
- **Hero-Sektion**: Attraktive Bildergalerie mit Logo und 3 Rezeptbildern
- **Mobile First Design**: Vollständig optimiert für Touch-Geräte
- **Filter-Labels**: Beschriftete Filterfelder für bessere Usability
- **Responsive Bilder**: 4-Spalten-Layout (Desktop) → 2 Spalten (Tablet) → 1 Spalte (Mobile)

### Design-Verbesserungen
- **Touch-Optimierung**: Mindestens 44px Touch-Targets für alle interaktiven Elemente
- **Responsive Typography**: Angepasste Schriftgrößen für Mobile/Desktop
- **Vollbild-Modals**: Auf Mobile Vollbild, auf Desktop zentriert
- **Gradient-Hintergrund**: Subtiler Gradient in Hero-Sektion
- **Hover-Effekte**: Nur auf Desktop (hover: hover Media Query)

### Usability
- **Größere Buttons**: 44px Mindesthöhe für Touch-Geräte
- **Bessere Lesbarkeit**: 16px Basis-Schriftgröße
- **Optimierte Abstände**: Mobile-freundliche Gaps und Paddings
- **Flexible Layouts**: Container mit Padding statt fester Breite

### Projekt-Bereinigung
- Entfernung aller unnötigen Backup-Ordner (beta2/, final/)
- Löschung nicht benötigter PDF- und Konvertierungs-Dateien
- Bereinigung doppelter Dateien (app.js, styles.css)
- Aktualisierte .gitignore zum Schutz sensibler Daten

## [1.1.0] - 2024 - Sicherheits- und Stabilitäts-Update

### Kritische Fixes
- **Sicherheit**: SECRET_KEY jetzt aus .env geladen statt hardcoded
- **Sicherheit**: CORS auf konfigurierbare Origins beschränkt (statt allow_all)
- **Struktur**: Root main.py korrigiert - verweist jetzt auf korrekte App
- **Datenbank**: Auto-Initialisierung beim Start mit Error-Handling

### Neue Features
- **Rate Limiting**: 60 Requests/Minute pro IP-Adresse
- **Logging**: Strukturiertes Logging mit File + Console Output
- **Tests**: Unit-Tests für Auth und Recipe Services
- **Health-Check**: Erweitert mit DB-Verbindungsprüfung
- **GDPR**: Vollständiger Daten-Export inkl. Ratings, Favorites, Rezepte
- **GDPR**: CASCADE-Löschung für alle User-Daten

### Verbesserungen
- **Performance**: Datenbank-Indizes für häufige Queries hinzugefügt
- **Sicherheit**: Backend-Passwort-Validierung implementiert
- **Stabilität**: Race Condition in Rating-Updates behoben (Row-Level-Lock)
- **Stabilität**: PDF-Generierung mit Error-Handling und Seitenumbrüchen
- **Code-Qualität**: datetime.utcnow() durch timezone-aware Alternative ersetzt
- **Frontend**: Besseres Error-Handling mit Status-Code-spezifischen Meldungen
- **Validierung**: Rezept-Autor-Validierung (User darf nicht None sein)

### Dokumentation
- README_FIXES.md: Übersicht aller behobenen Fehler
- DEPLOYMENT.md: Produktions-Deployment-Anleitung
- .gitignore: Umfassende Ignore-Regeln
- pytest.ini: Test-Konfiguration

### Dependencies
- pytest==7.4.3
- pytest-asyncio==0.21.1
- httpx==0.25.2
- python-dotenv==1.0.0

### Breaking Changes
- ALLOWED_ORIGINS muss in .env konfiguriert werden
- SECRET_KEY muss in .env gesetzt werden (nicht mehr optional)

### Migration Guide
1. Kopiere .env.example zu .env
2. Generiere neuen SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
3. Setze ALLOWED_ORIGINS auf deine Domain(s)
4. Starte App neu - Datenbank wird automatisch initialisiert

## [1.0.0] - Initial Release

### Features
- Rezept-Suche mit Filtern
- User-Authentifizierung (JWT)
- Rezept-Bewertungen
- Favoriten-System
- PDF-Export
- DSGVO-Funktionen (Export/Löschung)
- Responsive Frontend
- Dark Mode
