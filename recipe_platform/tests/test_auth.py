"""
Unit Tests für Authentication
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPass123",
        "data_processing_consent": True
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_register_weak_password():
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "weak",
        "data_processing_consent": True
    })
    assert response.status_code == 400

def test_login_success():
    client.post("/api/v1/auth/register", json={
        "username": "logintest",
        "email": "login@example.com",
        "first_name": "Login",
        "last_name": "Test",
        "password": "TestPass123",
        "data_processing_consent": True
    })
    response = client.post("/api/v1/auth/login", json={
        "username": "logintest",
        "password": "TestPass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    client.post("/api/v1/auth/register", json={
        "username": "wrongpass",
        "email": "wrong@example.com",
        "first_name": "Wrong",
        "last_name": "Pass",
        "password": "TestPass123",
        "data_processing_consent": True
    })
    response = client.post("/api/v1/auth/login", json={
        "username": "wrongpass",
        "password": "WrongPass123"
    })
    assert response.status_code == 401
