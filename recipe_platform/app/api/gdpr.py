from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.schemas.user import GDPRExportRequest, GDPRDeleteRequest
from app.services.gdpr import GDPRService
from app.services.auth import AuthService

router = APIRouter(tags=["DSGVO"])


@router.post("/export")
def export_data(request: GDPRExportRequest, db: Session = Depends(get_db)):
    """
    DSGVO Art. 15 - Recht auf Datenauskunft.
    Exportiert alle gespeicherten Nutzerdaten als JSON.
    """
    data = GDPRService.export_user_data(db, request.email)
    if not data:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    return JSONResponse(content=data)


@router.post("/delete")
def request_deletion(request: GDPRDeleteRequest, db: Session = Depends(get_db)):
    """
    DSGVO Art. 17 - Recht auf Löschung.
    Markiert Account zur Löschung (7 Tage Wartezeit).
    """
    try:
        AuthService.authenticate_user(db, request.email, request.password)
    except HTTPException as exc:
        if exc.status_code == 401:
            raise HTTPException(status_code=401, detail="Authentifizierung fehlgeschlagen")
        raise

    success = GDPRService.request_deletion(db, request.email)
    if success:
        return {"message": "Löschung beantragt. Account wird in 7 Tagen gelöscht."}
    raise HTTPException(status_code=400, detail="Löschung fehlgeschlagen")
