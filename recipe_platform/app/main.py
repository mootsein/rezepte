from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.models.database import engine, Base, SessionLocal
from app.api import auth, gdpr, recipes
from app.middleware.rate_limit import RateLimitMiddleware
from pathlib import Path
import logging
import sys

# Logging-Konfiguration
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent  # recipe_platform/
STATIC_DIR = BASE_DIR / "static"
PICS_DIR = BASE_DIR / "app" / "pics"
INDEX_HTML = BASE_DIR / "index.html"

# Validiere Verzeichnisse
for directory in [STATIC_DIR, PICS_DIR]:
    if not directory.exists():
        logger.warning(f"Verzeichnis nicht gefunden: {directory}")
        directory.mkdir(parents=True, exist_ok=True)

if not INDEX_HTML.exists():
    logger.error(f"index.html nicht gefunden: {INDEX_HTML}")

# Auto-Initialisierung der Datenbank
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Datenbank-Tabellen erfolgreich erstellt/validiert")
except Exception as e:
    logger.error(f"Fehler bei Datenbank-Initialisierung: {e}")
    raise

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# API Router Setup
api_router = APIRouter()
api_router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(gdpr.router, prefix="/gdpr", tags=["gdpr"])

app.include_router(api_router, prefix=settings.API_V1_STR)


# CORS Middleware mit sicherer Konfiguration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Request-Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"{request.method} {request.url.path}")
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/pics", StaticFiles(directory=PICS_DIR), name="pics")


@app.get("/health")
def health_check():
    """Erweiterter Health-Check mit DB-Verbindungsprüfung"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"DB Health-Check fehlgeschlagen: {e}")
        db_status = "unhealthy"
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.VERSION
    }


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(request: Request, full_path: str):
    """Serves the index.html for any path not caught by the API."""
    if not INDEX_HTML.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(INDEX_HTML)
