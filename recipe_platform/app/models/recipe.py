from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index
from sqlalchemy.sql import func
from app.models.database import Base

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String, index=True, nullable=False)
    kategorie = Column(String, index=True)
    beschreibung = Column(Text)
    zielgruppe = Column(String, index=True)
    kuche = Column(String, index=True)
    ernahrung = Column(String, index=True)
    schwierigkeitsgrad = Column(String)
    portionen = Column(Integer)
    vorbereitungszeit_min = Column(Integer, index=True)
    kochzeit_min = Column(Integer)
    gesamtzeit_min = Column(Integer, index=True)
    kalorien_kcal = Column(Integer)
    protein_g = Column(Integer)
    kohlenhydrate_g = Column(Integer)
    fett_g = Column(Integer)
    allergene = Column(String)
    tags = Column(String, index=True)
    bewertung = Column(Float)
    avg_rating = Column(Float, default=0)
    ratings_count = Column(Integer, default=0)
    autor = Column(String)
    zutaten_json = Column(Text)
    schritte_json = Column(Text)
    sprache = Column(String, default="de")
    seo_slug = Column(String, unique=True, index=True)
    erstellt_am = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_recipe_search', 'titel', 'beschreibung'),
        Index('idx_recipe_filters', 'kategorie', 'kuche', 'ernahrung'),
        Index('idx_recipe_time_portions', 'gesamtzeit_min', 'portionen'),
    )
