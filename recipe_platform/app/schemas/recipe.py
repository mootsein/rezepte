from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import bleach

class RecipeSearch(BaseModel):
    query: Optional[str] = Field(None, max_length=200)
    kuche: Optional[str] = None
    ernahrung: Optional[str] = None
    kategorie: Optional[str] = None  # vegetarisch, vegan, omnivor, etc.
    max_zeit: Optional[int] = Field(None, ge=0, le=300)
    min_zeit: Optional[int] = Field(None, ge=0, le=300)
    min_portionen: Optional[int] = Field(None, ge=1, le=20)
    max_portionen: Optional[int] = Field(None, ge=1, le=20)
    allergene_exclude: Optional[str] = None
    
    @field_validator('query', 'kuche', 'ernahrung', 'kategorie', 'allergene_exclude')
    @classmethod
    def sanitize_input(cls, v):
        if v:
            return bleach.clean(v.strip(), tags=[], strip=True)
        return v

class RecipeCreate(BaseModel):
    titel: str = Field(..., min_length=3, max_length=120)
    beschreibung: str = Field(..., min_length=10, max_length=500)
    kategorie: Optional[str] = Field(None, max_length=80)
    kuche: Optional[str] = Field(None, max_length=80)
    ernahrung: Optional[str] = Field(None, max_length=80)
    portionen: int = Field(..., ge=1, le=20)
    gesamtzeit_min: int = Field(..., ge=1, le=600)
    zutaten: List[str] = Field(..., min_length=1)
    schritte: List[str] = Field(..., min_length=1)
    
    @field_validator('titel', 'beschreibung', 'kategorie', 'kuche', 'ernahrung')
    @classmethod
    def sanitize_text(cls, v):
        if v is None:
            return v
        return bleach.clean(v.strip(), tags=[], strip=True)
    
    @field_validator('zutaten', 'schritte')
    @classmethod
    def sanitize_lists(cls, v):
        cleaned = [bleach.clean(item.strip(), tags=[], strip=True) for item in v if item.strip()]
        if not cleaned:
            raise ValueError("Liste darf nicht leer sein")
        return cleaned

class RecipeResponse(BaseModel):
    id: int
    titel: str
    kategorie: Optional[str]
    beschreibung: Optional[str]
    zielgruppe: Optional[str]
    kuche: Optional[str]
    ernahrung: Optional[str]
    schwierigkeitsgrad: Optional[str]
    portionen: Optional[int]
    vorbereitungszeit_min: Optional[int]
    kochzeit_min: Optional[int]
    gesamtzeit_min: Optional[int]
    kalorien_kcal: Optional[int]
    allergene: Optional[str]
    tags: Optional[str]
    bewertung: Optional[float]
    avg_rating: Optional[float]
    ratings_count: Optional[int]
    is_favorite: Optional[bool] = False
    autor: Optional[str]
    zutaten_json: Optional[str]
    schritte_json: Optional[str]
    seo_slug: Optional[str]
    
    class Config:
        from_attributes = True

class RecipeListResponse(BaseModel):
    total: int
    recipes: List[RecipeResponse]

class RatingRequest(BaseModel):
    stars: int = Field(..., ge=1, le=5)
