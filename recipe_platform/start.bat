@echo off
chcp 65001 >nul
echo ========================================
echo   FreshCook Rezeptplattform
echo ========================================
echo.

set VENV_PATH=..\venv
set DB_PATH=data\recipes.db

REM [1] Virtuelle Umgebung pruefen/erstellen
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [1/5] Erstelle virtuelle Umgebung...
    cd ..
    python -m venv venv
    if errorlevel 1 (
        echo FEHLER: Konnte venv nicht erstellen!
        pause
        exit /b 1
    )
    cd recipe_platform
    echo.
) else (
    echo [1/5] Virtuelle Umgebung gefunden.
    echo.
)

REM [2] Aktiviere venv
echo [2/5] Aktiviere virtuelle Umgebung...
call %VENV_PATH%\Scripts\activate.bat
echo.

REM [3] Dependencies pruefen/installieren
echo [3/5] Pruefe Dependencies...
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo Dependencies fehlen! Installiere...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo FEHLER: Installation fehlgeschlagen!
        pause
        exit /b 1
    )
    echo.
) else (
    echo Dependencies OK.
    echo.
)

REM [4] Datenbank pruefen/initialisieren
if not exist "%DB_PATH%" (
    echo [4/5] Initialisiere Datenbank...
    python init_db.py
    if errorlevel 1 (
        echo FEHLER: Datenbankinitialisierung fehlgeschlagen!
        pause
        exit /b 1
    )
    echo.
) else (
    echo [4/5] Datenbank gefunden.
    echo.
)

REM [5] Server starten
echo [5/5] Starte Server...
echo.
echo ========================================
echo   FreshCook laeuft!
echo ========================================
echo.
echo Frontend: http://localhost:8888
echo API Docs: http://localhost:8888/api/v1/docs
echo Health:   http://localhost:8888/health
echo.
echo Druecke CTRL+C zum Beenden
echo.

REM Browser oeffnen nach 2 Sekunden
start /B timeout /t 2 /nobreak >nul && start "" "http://localhost:8888"

REM Server starten (blockierend)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
echo.
echo Druecke eine Taste zum Beenden...
pause > nul
