from app.database.supabase import supabase_client
from app.schemas.admin import AdminLogin, AdminCreate
from loguru import logger
from typing import Dict, Any, Optional

class AdminModel:
    """Model for admin authentication operations"""
    
    @staticmethod
    async def login(admin_login: AdminLogin) -> Dict[str, Any]:
        """Login an admin user using Supabase authentication"""
        try:
            response = supabase_client.auth.sign_in_with_password({
                "email": admin_login.email,
                "password": admin_login.password
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "access_token": response.session.access_token,
                    "token_type": "bearer"
                }
            raise Exception("Invalid credentials")
        except Exception as e:
            logger.error(f"Error during admin login: {str(e)}")
            raise
    
    @staticmethod
    async def create_admin(admin_create: AdminCreate) -> Dict[str, Any]:
        """Create a new admin user using Supabase authentication"""
        try:
            # Create user in Supabase Auth
            auth_response = supabase_client.auth.sign_up({
                "email": admin_create.email,
                "password": admin_create.password,
                "options": {
                    "data": {
                        "full_name": admin_create.full_name,
                        "role": "admin"
                    }
                }
            })
            
            if auth_response.user:
                return {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "message": "Admin user created successfully"
                }
            raise Exception("Failed to create admin user")
        except Exception as e:
            logger.error(f"Error creating admin user: {str(e)}")
            raise
    
    @staticmethod
    async def get_current_admin(token: str) -> Optional[Dict[str, Any]]:
        """Get current admin user from token"""
        try:
            # Verify the token with Supabase
            user = supabase_client.auth.get_user(token)
            if user and user.user:
                # Check if user has admin role
                user_data = user.user.user_metadata
                if user_data.get("role") == "admin":
                    return {
                        "id": user.user.id,
                        "email": user.user.email,
                        "full_name": user_data.get("full_name")
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting current admin: {str(e)}")
            return None 