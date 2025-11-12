from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User
from app.schemas.recipe import RecipeSearch, RecipeResponse, RecipeListResponse, RatingRequest, RecipeCreate
from app.services.recipe import RecipeService
from app.api.auth import get_current_user, get_optional_current_user

router = APIRouter(tags=["Rezepte"])

@router.get("/search", response_model=RecipeListResponse)
def search_recipes(
    query: str = Query(None, max_length=200),
    kuche: str = Query(None),
    ernahrung: str = Query(None),
    kategorie: str = Query(None),
    max_zeit: int = Query(None, ge=0, le=300),
    min_portionen: int = Query(None, ge=1, le=20),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Erweiterte Rezeptsuche. Für angemeldete Benutzer wird der Favoritenstatus angezeigt.
    """
    search_params = RecipeSearch(
        query=query, kuche=kuche, ernahrung=ernahrung, kategorie=kategorie,
        max_zeit=max_zeit, min_portionen=min_portionen
    )
    user_id = current_user.id if current_user else None
    
    recipes, total = RecipeService.search_recipes(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        **search_params.model_dump(exclude_none=True)
    )
    
    return {"total": total, "recipes": recipes}

@router.get("/random", response_model=RecipeResponse)
def get_random_recipe(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    """Zufälliges Rezept abrufen."""
    user_id = current_user.id if current_user else None
    recipe = RecipeService.get_random_recipe(db, user_id=user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Kein Rezept gefunden")
    return recipe

@router.get("/filters", response_model=dict)
def get_filter_options(db: Session = Depends(get_db)):
    """Alle verfügbaren Filteroptionen abrufen."""
    return RecipeService.get_filter_options(db)

@router.post("", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe_data: RecipeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Neues Rezept anlegen."""
    recipe = RecipeService.create_recipe(db, recipe_data, current_user)
    return recipe

@router.post("/{recipe_id}/rate", status_code=201)
def rate_recipe(recipe_id: int, rating_request: RatingRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Ein Rezept bewerten (nur für angemeldete Benutzer)."""
    rating = RecipeService.rate_recipe(db, current_user.id, recipe_id, rating_request.stars)
    return {"message": "Bewertung erfolgreich gespeichert", "rating": rating}

@router.post("/{recipe_id}/favorite", status_code=201)
def toggle_favorite(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Ein Rezept als Favorit markieren/entfernen (nur für angemeldete Benutzer)."""
    is_favorite = RecipeService.toggle_favorite(db, current_user.id, recipe_id)
    return {"is_favorite": is_favorite}

@router.get("/favorites/me", response_model=RecipeListResponse)
def get_user_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Die Favoriten des aktuellen Benutzers abrufen."""
    favorites, total = RecipeService.get_user_favorites(db, current_user.id)
    return {"total": total, "recipes": favorites}

@router.get("/{recipe_id}/pdf")
def export_recipe_pdf(recipe_id: int, db: Session = Depends(get_db)):
    """Rezept als PDF exportieren."""
    from fastapi.responses import Response
    pdf_content = RecipeService.generate_pdf(db, recipe_id)
    if not pdf_content:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rezept_{recipe_id}.pdf"}
    )

@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_current_user)):
    """
    Einzelnes Rezept abrufen. Für angemeldete Benutzer wird der Favoritenstatus angezeigt.
    """
    user_id = current_user.id if current_user else None
    recipe = RecipeService.get_recipe_by_id(db, recipe_id, user_id=user_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")
    return recipe
