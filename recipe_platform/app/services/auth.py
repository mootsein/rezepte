from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
import re

class AuthService:
    @staticmethod
    def register_user(db: Session, username: str, email: str, first_name: str, last_name: str, password: str, **consents) -> User:
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=400, detail="E-Mail bereits registriert")
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(status_code=400, detail="Benutzername bereits vergeben")
        
        # Backend-Passwort-Validierung
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Passwort muss mindestens 8 Zeichen lang sein")
        if not re.search(r'[A-Z]', password):
            raise HTTPException(status_code=400, detail="Passwort muss mindestens einen Großbuchstaben enthalten")
        if not re.search(r'[a-z]', password):
            raise HTTPException(status_code=400, detail="Passwort muss mindestens einen Kleinbuchstaben enthalten")
        if not re.search(r'\d', password):
            raise HTTPException(status_code=400, detail="Passwort muss mindestens eine Ziffer enthalten")
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=get_password_hash(password),
            **consents
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, identifier: str, password: str) -> User:
        user = db.query(User).filter(User.username == identifier).first()
        if not user:
            user = db.query(User).filter(User.email == identifier).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
        
        # Check account lock
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(status_code=403, detail="Account temporär gesperrt")
        
        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOGIN_ATTEMPT_WINDOW_MINUTES)
            db.commit()
            raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
        
        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        return user
    
    @staticmethod
    def create_token(user: User) -> str:
        return create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
