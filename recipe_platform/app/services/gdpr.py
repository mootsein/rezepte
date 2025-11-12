from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.rating import Rating, Favorite
from app.models.recipe import Recipe
import json

class GDPRService:
    @staticmethod
    def export_user_data(db: Session, email: str) -> dict:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        user.export_requested_at = datetime.now(timezone.utc)
        db.commit()
        
        # Exportiere Ratings
        ratings = db.query(Rating).filter(Rating.user_id == user.id).all()
        ratings_data = [{
            "recipe_id": r.recipe_id,
            "stars": r.stars,
            "created_at": r.created_at.isoformat() if r.created_at else None
        } for r in ratings]
        
        # Exportiere Favorites
        favorites = db.query(Favorite).filter(Favorite.user_id == user.id).all()
        favorites_data = [{
            "recipe_id": f.recipe_id,
            "created_at": f.created_at.isoformat() if f.created_at else None
        } for f in favorites]
        
        # Exportiere eigene Rezepte
        own_recipes = db.query(Recipe).filter(Recipe.autor == user.username).all()
        recipes_data = [{
            "id": r.id,
            "titel": r.titel,
            "created_at": r.erstellt_am.isoformat() if r.erstellt_am else None
        } for r in own_recipes]
        
        return {
            "personal_data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "consents": {
                "marketing": user.consent_marketing,
                "analytics": user.consent_analytics,
                "data_processing": user.data_processing_consent,
            },
            "activity_data": {
                "ratings": ratings_data,
                "favorites": favorites_data,
                "recipes_created": recipes_data,
            },
            "export_date": datetime.now(timezone.utc).isoformat(),
            "format": "JSON",
        }
    
    @staticmethod
    def request_deletion(db: Session, email: str) -> bool:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        
        user.deletion_requested_at = datetime.now(timezone.utc)
        user.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def execute_deletion(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.deletion_requested_at:
            # Lösche alle verknüpften Daten (CASCADE)
            db.query(Rating).filter(Rating.user_id == user_id).delete()
            db.query(Favorite).filter(Favorite.user_id == user_id).delete()
            
            # Optional: Anonymisiere Rezepte statt sie zu löschen
            db.query(Recipe).filter(Recipe.autor == user.username).update(
                {"autor": "[Gelöschter Benutzer]"}
            )
            
            db.delete(user)
            db.commit()
