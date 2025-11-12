from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8)
    consent_marketing: bool = False
    consent_analytics: bool = False
    data_processing_consent: bool = True
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Passwort muss mindestens einen Großbuchstaben enthalten')
        if not re.search(r'[a-z]', v):
            raise ValueError('Passwort muss mindestens einen Kleinbuchstaben enthalten')
        if not re.search(r'\d', v):
            raise ValueError('Passwort muss mindestens eine Ziffer enthalten')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GDPRExportRequest(BaseModel):
    email: EmailStr

class GDPRDeleteRequest(BaseModel):
    email: EmailStr
    password: str
