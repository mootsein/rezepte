from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, distinct
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipe import RecipeCreate
from typing import List, Optional, Dict, Tuple, Deque
from fastapi import HTTPException
import json
from io import BytesIO
from collections import deque
import logging

logger = logging.getLogger(__name__)

try:
    from app.models.rating import Rating, Favorite
except ImportError:
    Rating = None
    Favorite = None

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
except ImportError:
    canvas = None
    A4 = None

RECENT_RANDOM_CACHE: Deque[int] = deque(maxlen=5)


class RecipeService:
    @staticmethod
    def search_recipes(
        db: Session,
        user_id: Optional[int] = None,
        query: Optional[str] = None,
        kuche: Optional[str] = None,
        ernahrung: Optional[str] = None,
        kategorie: Optional[str] = None,
        max_zeit: Optional[int] = None,
        min_zeit: Optional[int] = None,
        min_portionen: Optional[int] = None,
        max_portionen: Optional[int] = None,
        allergene_exclude: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Recipe], int]:

        base_query = db.query(Recipe)
        filters = []

        if query:
            filters.append(or_(
                Recipe.titel.ilike(f"%{query}%"),
                Recipe.beschreibung.ilike(f"%{query}%"),
                Recipe.zutaten_json.ilike(f"%{query}%")
            ))
        if kuche:
            filters.append(Recipe.kuche.ilike(f"%{kuche}%"))
        if ernahrung:
            filters.append(Recipe.ernahrung.ilike(f"%{ernahrung}%"))
        if kategorie:
            filters.append(Recipe.kategorie.ilike(f"%{kategorie}%"))
        if max_zeit is not None:
            filters.append(Recipe.gesamtzeit_min <= max_zeit)
        if min_zeit is not None:
            filters.append(Recipe.gesamtzeit_min >= min_zeit)
        if min_portionen is not None:
            filters.append(Recipe.portionen >= min_portionen)
        if max_portionen is not None:
            filters.append(Recipe.portionen <= max_portionen)
        if allergene_exclude:
            filters.append(or_(
                Recipe.allergene.is_(None),
                ~Recipe.allergene.ilike(f"%{allergene_exclude}%")
            ))

        if filters:
            base_query = base_query.filter(and_(*filters))

        total = base_query.count()

        # Füge die is_favorite-Markierung hinzu und führe die Abfrage aus
        if user_id and Favorite:
            favorite_subquery = db.query(Favorite.recipe_id).filter(
                Favorite.user_id == user_id).subquery()
            final_query = base_query.add_column(
                Recipe.id.in_(favorite_subquery).label('is_favorite')
            ).offset(offset).limit(limit)

            results = final_query.all()
            recipes = []
            for recipe, is_favorite in results:
                recipe.is_favorite = is_favorite
                recipes.append(recipe)
        else:
            results = base_query.offset(offset).limit(limit).all()
            recipes = []
            for recipe in results:
                recipe.is_favorite = False
                recipes.append(recipe)

        return recipes, total

    @staticmethod
    def get_recipe_by_id(db: Session, recipe_id: int, user_id: Optional[int] = None) -> Optional[Recipe]:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe and user_id and Favorite:
            recipe.is_favorite = db.query(Favorite).filter(
                Favorite.user_id == user_id, Favorite.recipe_id == recipe_id
            ).first() is not None
        elif recipe:
            recipe.is_favorite = False
        return recipe

    @staticmethod
    def get_random_recipe(db: Session, user_id: Optional[int] = None) -> Optional[Recipe]:
        excluded_ids = list(RECENT_RANDOM_CACHE)
        query = db.query(Recipe)
        if excluded_ids:
            query = query.filter(~Recipe.id.in_(excluded_ids))
        recipe = query.order_by(func.random()).first()

        if not recipe:
            recipe = db.query(Recipe).order_by(func.random()).first()

        if recipe:
            RECENT_RANDOM_CACHE.append(recipe.id)
            if user_id and Favorite:
                recipe.is_favorite = db.query(Favorite).filter(
                    Favorite.user_id == user_id, Favorite.recipe_id == recipe.id
                ).first() is not None
            else:
                recipe.is_favorite = False
        return recipe

    @staticmethod
    def get_filter_options(db: Session) -> Dict:
        kategorien = [r[0] for r in db.query(distinct(Recipe.kategorie)).filter(
            Recipe.kategorie.isnot(None)).all() if r[0]]
        kuchen = [r[0] for r in db.query(distinct(Recipe.kuche)).filter(
            Recipe.kuche.isnot(None)).all() if r[0]]
        ernaehrungen = [r[0] for r in db.query(distinct(Recipe.ernahrung)).filter(
            Recipe.ernahrung.isnot(None)).all() if r[0]]
        return {"kategorien": kategorien, "kuchen": kuchen, "ernaehrungen": ernaehrungen}

    @staticmethod
    def rate_recipe(db: Session, user_id: int, recipe_id: int, stars: int):
        if not Rating:
            raise ImportError("Rating model not available")

        rating = db.query(Rating).filter(Rating.user_id ==
                                         user_id, Rating.recipe_id == recipe_id).first()
        if rating:
            rating.stars = stars
        else:
            rating = Rating(user_id=user_id, recipe_id=recipe_id, stars=stars)
            db.add(rating)

        db.commit()
        RecipeService._update_recipe_rating(db, recipe_id)
        db.refresh(rating)
        return rating

    @staticmethod
    def _update_recipe_rating(db: Session, recipe_id: int):
        if not Rating:
            return

        # Atomare Transaktion mit Row-Level-Lock
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).with_for_update().first()
        if not recipe:
            return
        
        result = db.query(func.avg(Rating.stars), func.count(
            Rating.stars)).filter(Rating.recipe_id == recipe_id).one()
        avg_rating, ratings_count = result[0] or 0, result[1] or 0

        recipe.avg_rating = round(avg_rating, 1)
        recipe.ratings_count = ratings_count
        db.commit()

    @staticmethod
    def toggle_favorite(db: Session, user_id: int, recipe_id: int) -> bool:
        if not Favorite:
            raise ImportError("Favorite model not available")

        favorite = db.query(Favorite).filter(
            Favorite.user_id == user_id, Favorite.recipe_id == recipe_id).first()

        if favorite:
            db.delete(favorite)
            db.commit()
            return False
        else:
            favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
            db.add(favorite)
            db.commit()
            return True

    @staticmethod
    def get_user_favorites(db: Session, user_id: int) -> Tuple[List[Recipe], int]:
        if not Favorite:
            return [], 0

        query = db.query(Recipe).join(Favorite).filter(
            Favorite.user_id == user_id)
        total = query.count()
        recipes = query.all()
        for recipe in recipes:
            recipe.is_favorite = True  # They are all favorites
        return recipes, total

    @staticmethod
    def create_recipe(db: Session, recipe_data: RecipeCreate, user: User) -> Recipe:
        if not user:
            raise HTTPException(status_code=401, detail="Authentifizierung erforderlich")
        
        try:
            zutaten_json = json.dumps(recipe_data.zutaten, ensure_ascii=False)
            schritte_json = json.dumps(recipe_data.schritte, ensure_ascii=False)
            recipe = Recipe(
                titel=recipe_data.titel,
                beschreibung=recipe_data.beschreibung,
                kategorie=recipe_data.kategorie,
                kuche=recipe_data.kuche,
                ernahrung=recipe_data.ernahrung,
                portionen=recipe_data.portionen,
                gesamtzeit_min=recipe_data.gesamtzeit_min,
                zutaten_json=zutaten_json,
                schritte_json=schritte_json,
                autor=user.username,
                avg_rating=0,
                ratings_count=0
            )
            db.add(recipe)
            db.commit()
            db.refresh(recipe)
            recipe.is_favorite = False
            return recipe
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Erstellen des Rezepts: {e}")
            raise HTTPException(status_code=500, detail="Rezept konnte nicht erstellt werden")

    @staticmethod
    def generate_pdf(db: Session, recipe_id: int) -> Optional[bytes]:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe or not canvas:
            return None

        try:
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4

            p.setFont("Helvetica-Bold", 20)
            # Begrenze Titel-Länge
            titel = recipe.titel[:80] if recipe.titel else "Unbekannt"
            p.drawString(50, height - 50, titel)

            y = height - 100
            p.setFont("Helvetica", 12)

            details = [f"Kategorie: {recipe.kategorie or '-'}",
                       f"Küche: {recipe.kuche or '-'}", f"Zeit: {recipe.gesamtzeit_min or '?'} Min"]
            for detail in details:
                p.drawString(50, y, detail)
                y -= 20

            y -= 20
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Zutaten:")
            y -= 20

            p.setFont("Helvetica", 10)
            try:
                zutaten = json.loads(recipe.zutaten_json or '[]')
                for zutat in zutaten:
                    if y < 50:  # Neue Seite bei Bedarf
                        p.showPage()
                        y = height - 50
                        p.setFont("Helvetica", 10)
                    p.drawString(70, y, f"- {zutat[:100]}")
                    y -= 15
            except json.JSONDecodeError:
                logger.error(f"Fehler beim Parsen der Zutaten für Rezept {recipe_id}")

            y -= 20
            if y < 50:
                p.showPage()
                y = height - 50
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Zubereitung:")
            y -= 20

            p.setFont("Helvetica", 10)
            try:
                schritte = json.loads(recipe.schritte_json or '[]')
                for i, schritt in enumerate(schritte, 1):
                    if y < 50:
                        p.showPage()
                        y = height - 50
                        p.setFont("Helvetica", 10)
                    p.drawString(70, y, f"{i}. {schritt[:100]}")
                    y -= 15
            except json.JSONDecodeError:
                logger.error(f"Fehler beim Parsen der Schritte für Rezept {recipe_id}")

            p.save()
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Fehler bei PDF-Generierung: {e}")
            return None
