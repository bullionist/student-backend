from app.database.supabase import supabase_client
from app.schemas.student import StudentCreate, StudentUpdate, ConversationMessage, ConversationHistory
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

class StudentModel:
    """Model for student data operations"""
    
    TABLE_NAME = "students"
    
    @staticmethod
    async def create(student: StudentCreate) -> Dict[str, Any]:
        """Create a new student session"""
        try:
            # Convert the student model to dict
            student_data = student.dict()
            
            # Initialize conversation history if not present
            if "conversation_history" not in student_data or student_data["conversation_history"] is None:
                student_data["conversation_history"] = {
                    "messages": [],
                    "last_updated": datetime.utcnow().isoformat()
                }
            else:
                # Convert last_updated to ISO string if it's a datetime object
                if isinstance(student_data["conversation_history"].get("last_updated"), datetime):
                    student_data["conversation_history"]["last_updated"] = student_data["conversation_history"]["last_updated"].isoformat()
            
            # Convert datetime objects to ISO format strings
            if "exam_scores" in student_data:
                for exam in student_data["exam_scores"]:
                    if "date_taken" in exam and exam["date_taken"]:
                        exam["date_taken"] = exam["date_taken"].isoformat()
            
            if "additional_preferences" in student_data:
                prefs = student_data["additional_preferences"]
                if "start_date_preference" in prefs and prefs["start_date_preference"]:
                    prefs["start_date_preference"] = prefs["start_date_preference"].isoformat()
            
            # Insert into database
            try:
                response = supabase_client.table(StudentModel.TABLE_NAME).insert(student_data).execute()
                if not response.data:
                    raise Exception("Database insert failed - no data returned")
                return response.data[0]
            except Exception as db_error:
                # Check if table exists
                try:
                    # Try to select from the table to check if it exists
                    supabase_client.table(StudentModel.TABLE_NAME).select("id").limit(1).execute()
                except Exception as table_error:
                    raise Exception("Database table 'students' does not exist. Please create the table first.")
                raise db_error
                
        except Exception as e:
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
            raise
    
    @staticmethod
    async def update(student_id: str, student_update: StudentUpdate) -> Optional[Dict[str, Any]]:
        """Update a student"""
        try:
            # Only include non-None fields in the update
            update_data = {k: v for k, v in student_update.dict().items() if v is not None}
            
            # Convert datetime objects to ISO format strings
            if "exam_scores" in update_data:
                for exam in update_data["exam_scores"]:
                    if "date_taken" in exam and exam["date_taken"]:
                        exam["date_taken"] = exam["date_taken"].isoformat()
            
            if "additional_preferences" in update_data:
                prefs = update_data["additional_preferences"]
                if "start_date_preference" in prefs and prefs["start_date_preference"]:
                    prefs["start_date_preference"] = prefs["start_date_preference"].isoformat()
            
            if not update_data:
                # Nothing to update
                return await StudentModel.get_by_id(student_id)
                
            response = supabase_client.table(StudentModel.TABLE_NAME).update(update_data).eq("id", student_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
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
            raise
