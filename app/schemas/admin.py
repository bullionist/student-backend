from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class AdminLogin(BaseModel):
    """Schema for admin login"""
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    """Schema for admin response data"""
    id: str
    email: EmailStr
    access_token: str
    token_type: str = "bearer"

class AdminCreate(BaseModel):
    """Schema for creating a new admin"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None 