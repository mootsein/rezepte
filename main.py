"""
Haupteinstiegspunkt für die Rezeptplattform.
Startet die FastAPI-Anwendung aus dem recipe_platform Verzeichnis.
"""
import sys
from pathlib import Path

# Füge das recipe_platform Verzeichnis zum Python-Pfad hinzu
recipe_platform_path = Path(__file__).parent / "recipe_platform"
sys.path.insert(0, str(recipe_platform_path))

# Importiere die eigentliche App
from app.main import app  # type: ignore # pylint: disable=wrong-import-position,import-error

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, reload=True)
