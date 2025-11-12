"""
Unit Tests für Recipe Service
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models.recipe import Recipe
from app.models.user import User
from app.services.recipe import RecipeService
from app.core.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_recipes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("TestPass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_recipe(db_session):
    recipe = Recipe(
        titel="Test Rezept",
        beschreibung="Test Beschreibung",
        kategorie="Hauptgericht",
        kuche="Italienisch",
        portionen=4,
        gesamtzeit_min=30,
        zutaten_json='["Zutat 1", "Zutat 2"]',
        schritte_json='["Schritt 1", "Schritt 2"]',
        autor="testuser"
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe

def test_search_recipes(db_session, test_recipe):
    recipes, total = RecipeService.search_recipes(db_session, query="Test")
    assert total == 1
    assert recipes[0].titel == "Test Rezept"

def test_get_recipe_by_id(db_session, test_recipe):
    recipe = RecipeService.get_recipe_by_id(db_session, test_recipe.id)
    assert recipe is not None
    assert recipe.titel == "Test Rezept"

def test_get_filter_options(db_session, test_recipe):
    options = RecipeService.get_filter_options(db_session)
    assert "kategorien" in options
    assert "Hauptgericht" in options["kategorien"]
