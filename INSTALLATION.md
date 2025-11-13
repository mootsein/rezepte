# Installation & Start

## Voraussetzungen
- Python 3.8+
- Git

## Schnellstart

### 1. Repository klonen
```bash
git clone https://github.com/mootsein/rezepte.git
cd rezepte
```

### 2. Virtual Environment erstellen
```bash
python -m venv venv
```

### 3. Virtual Environment aktivieren
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Dependencies installieren
```bash
cd recipe_platform
pip install -r requirements.txt
```

### 5. Datenbank initialisieren
```bash
python init_db.py
```

### 6. Anwendung starten
```bash
uvicorn app.main:app --reload --port 8888
```

### 7. Im Browser öffnen
```
http://localhost:8888
```

## Alternativ: Einfacher Start (Windows)
```bash
cd recipe_platform
start.bat
```

## Alternativ: Einfacher Start (Linux/Mac)
```bash
cd recipe_platform
chmod +x start.sh
./start.sh
```
