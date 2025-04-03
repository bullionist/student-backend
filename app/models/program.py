from app.database.supabase import supabase_client
from app.schemas.program import ProgramCreate, ProgramUpdate
from loguru import logger
from typing import List, Optional, Dict, Any

class ProgramModel:
    """Model for program data operations"""
    
    TABLE_NAME = "programs"
    
    @staticmethod
    async def create(program: ProgramCreate) -> Dict[str, Any]:
        """Create a new program"""
        try:
            response = supabase_client.table(ProgramModel.TABLE_NAME).insert(program.dict()).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating program: {str(e)}")
            raise
    
    @staticmethod
    async def get_all() -> List[Dict[str, Any]]:
        """Get all programs"""
        try:
            response = supabase_client.table(ProgramModel.TABLE_NAME).select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting all programs: {str(e)}")
            raise
    
    @staticmethod
    async def get_by_id(program_id: str) -> Optional[Dict[str, Any]]:
        """Get a program by ID"""
        try:
            response = supabase_client.table(ProgramModel.TABLE_NAME).select("*").eq("id", program_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting program by ID: {str(e)}")
            raise
    
    @staticmethod
    async def update(program_id: str, program_update: ProgramUpdate) -> Optional[Dict[str, Any]]:
        """Update a program"""
        try:
            # Only include non-None fields in the update
            update_data = {k: v for k, v in program_update.dict().items() if v is not None}
            if not update_data:
                # Nothing to update
                return await ProgramModel.get_by_id(program_id)
                
            response = supabase_client.table(ProgramModel.TABLE_NAME).update(update_data).eq("id", program_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating program: {str(e)}")
            raise
    
    @staticmethod
    async def delete(program_id: str) -> bool:
        """Delete a program"""
        try:
            response = supabase_client.table(ProgramModel.TABLE_NAME).delete().eq("id", program_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error deleting program: {str(e)}")
            raise
