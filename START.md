# Website starten - Schnellanleitung

## Option 1: Einfacher Start (Empfohlen)

```bash
# 1. In das Projektverzeichnis wechseln
cd "c:\Users\mikew\Agiles Projektmanagement"

# 2. Virtuelle Umgebung aktivieren (falls noch nicht geschehen)
python -m venv venv
venv\Scripts\activate

# 3. Dependencies installieren (nur beim ersten Mal)
cd recipe_platform
pip install -r requirements.txt

# 4. Datenbank initialisieren (nur beim ersten Mal)
python init_db.py

# 5. Server starten
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
```

## Option 2: Mit Root main.py

```bash
# 1. In das Projektverzeichnis wechseln
cd "c:\Users\mikew\Agiles Projektmanagement"

# 2. Virtuelle Umgebung aktivieren
venv\Scripts\activate

# 3. Server starten
python main.py
```

## Option 3: Mit start.bat (Windows)

```bash
# Doppelklick auf:
recipe_platform\start.bat
```

## Website öffnen

Nach dem Start öffne im Browser:
- **Frontend**: http://localhost:8888
- **API Docs**: http://localhost:8888/api/v1/docs
- **Health Check**: http://localhost:8888/health

## Troubleshooting

### Fehler: "No module named 'fastapi'"
```bash
cd recipe_platform
pip install -r requirements.txt
```

### Fehler: "Database not found"
```bash
cd recipe_platform
python init_db.py
```

### Fehler: "Port 8888 already in use"
```bash
# Anderen Port verwenden
python -m uvicorn app.main:app --reload --port 8889
```

### Fehler: ".env file not found"
```bash
# .env existiert bereits, sollte kein Problem sein
# Falls doch: Kopiere .env.example zu .env
```

## Stoppen

Drücke `CTRL + C` im Terminal
