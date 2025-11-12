#!/bin/bash

echo "========================================"
echo "FreshCook Rezeptplattform - Start"
echo "========================================"
echo ""

DB_PATH="data/recipes.db"

# Prüfe ob Datenbank existiert
if [ -f "$DB_PATH" ]; then
    echo "Datenbank gefunden: $DB_PATH"
else
    echo "Keine Datenbank gefunden, initialisiere..."
    python init_db.py
    if [ $? -ne 0 ]; then
        echo "Fehler bei der Datenbankinitialisierung!"
        exit 1
    fi
fi

# Prüfe Dependencies
echo "Prüfe Dependencies..."
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Dependencies fehlen! Installiere..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Fehler bei der Installation!"
        exit 1
    fi
fi

echo ""
echo "Starte Server..."
echo ""
echo "========================================"
echo " FreshCook läuft!"
echo "========================================"
echo ""
echo "Frontend: http://localhost:8888"
echo "API Docs: http://localhost:8888/api/v1/docs"
echo "Health:   http://localhost:8888/health"
echo ""
echo "Drücke CTRL+C zum Beenden"
echo ""

# Starte Server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
