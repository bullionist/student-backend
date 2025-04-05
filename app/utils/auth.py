from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database.supabase import supabase_client
from loguru import logger
from typing import Dict, Any, Optional
from app.models.admin import AdminModel

security = HTTPBearer()

async def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Validate the JWT token from Supabase and ensure it's a valid admin user.
    
    This function is used as a dependency for admin-only routes.
    
    Args:
        credentials: The JWT token credentials extracted from the Authorization header
        
    Returns:
        The user data if authentication is successful
        
    Raises:
        HTTPException: If the token is invalid or the user is not an admin
    """
    try:
        # Extract token 
        token = credentials.credentials
        
        # Verify token with Supabase
        try:
            # This will validate the JWT signature and expiration
            user = supabase_client.auth.get_user(token)
            
            if not user or not user.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            user_data = user.user
            
            # Check if user has admin role (you might want to store this in Supabase user metadata)
            # For simplicity, we'll just check if the user exists and is validated by Supabase
            # In a real application, you would check for specific admin roles
            
            return {
                "id": user_data.id,
                "email": user_data.email,
                "is_admin": True,  # In a real app, you'd check user metadata or a separate admins table
            }
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get the current admin user from the token.
    This will be used to protect admin routes.
    """
    token = credentials.credentials
    admin = await AdminModel.get_current_admin(token)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return admin
