from app.database.supabase import supabase_client
from app.schemas.student import StudentCreate, StudentUpdate, ConversationMessage
from loguru import logger
from typing import List, Optional, Dict, Any
from datetime import datetime

class StudentModel:
    """Model for student data operations"""
    
    TABLE_NAME = "students"
    
    @staticmethod
    async def create(student: StudentCreate) -> Dict[str, Any]:
        """Create a new student session"""
        try:
            student_data = student.dict()
            response = supabase_client.table(StudentModel.TABLE_NAME).insert(student_data).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating student: {str(e)}")
            raise
    
    @staticmethod
    async def get_by_id(student_id: str) -> Optional[Dict[str, Any]]:
        """Get a student by ID"""
        try:
            response = supabase_client.table(StudentModel.TABLE_NAME).select("*").eq("id", student_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting student by ID: {str(e)}")
            raise
    
    @staticmethod
    async def update(student_id: str, student_update: StudentUpdate) -> Optional[Dict[str, Any]]:
        """Update a student"""
        try:
            # Only include non-None fields in the update
            update_data = {k: v for k, v in student_update.dict().items() if v is not None}
            if not update_data:
                # Nothing to update
                return await StudentModel.get_by_id(student_id)
                
            response = supabase_client.table(StudentModel.TABLE_NAME).update(update_data).eq("id", student_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            raise
    
    @staticmethod
    async def add_conversation_message(student_id: str, role: str, content: str) -> Optional[Dict[str, Any]]:
        """Add a message to the conversation history"""
        try:
            # First get the current student data
            student_data = await StudentModel.get_by_id(student_id)
            if not student_data:
                return None
                
            # Create new message
            new_message = ConversationMessage(
                role=role,
                content=content,
                timestamp=datetime.now().isoformat()
            )
            
            # Get current conversation history or create a new one
            conversation_history = student_data.get("conversation_history", {"messages": []})
            
            # Add the new message
            conversation_history["messages"].append(new_message.dict())
            
            # Update the student record
            response = supabase_client.table(StudentModel.TABLE_NAME).update(
                {"conversation_history": conversation_history}
            ).eq("id", student_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error adding conversation message: {str(e)}")
            raise
