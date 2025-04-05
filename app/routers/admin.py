from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.admin import AdminLogin, AdminResponse, AdminCreate
from app.models.admin import AdminModel
from app.utils.auth import get_current_admin
from typing import Dict, Any

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)

@router.post("/login", response_model=AdminResponse)
async def login(admin_login: AdminLogin):
    """Login an admin user"""
    try:
        result = await AdminModel.login(admin_login)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/register", response_model=Dict[str, Any])
async def register(admin_create: AdminCreate, current_admin: Dict[str, Any] = Depends(get_current_admin)):
    """
    Register a new admin user.
    Only existing admins can create new admin users.
    """
    try:
        result = await AdminModel.create_admin(admin_create)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_admin_profile(current_admin: Dict[str, Any] = Depends(get_current_admin)):
    """Get the current admin user's profile"""
    return current_admin 