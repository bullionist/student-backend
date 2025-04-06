from app.database.supabase import supabase_client
from app.schemas.student import StudentCreate, StudentUpdate
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

class StudentModel:
    """Model for student data operations"""
    
    TABLE_NAME = "students"
    
    @staticmethod
    async def create(student: StudentCreate) -> Dict[str, Any]:
        """Create a new student"""
        try:
            # Convert the student model to dict
            student_data = student.dict()
            
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
            logger.info(f"Attempting to fetch student with ID: {student_id}")
            logger.info(f"Using table name: {StudentModel.TABLE_NAME}")
            
            # First, let's try to get all students to verify table access
            all_students = await StudentModel.get_all()
            logger.info(f"Total students in table: {len(all_students)}")
            
            # Now try to get the specific student
            response = supabase_client.table(StudentModel.TABLE_NAME).select("*").eq("id", student_id).execute()
            
            logger.info(f"Supabase response data: {response.data}")
            
            if response.data and len(response.data) > 0:
                logger.info(f"Student found: {response.data[0]}")
                return response.data[0]
            
            # If no data found, let's try a case-insensitive search
            logger.info("No exact match found, trying case-insensitive search...")
            all_matching_ids = [s for s in all_students if str(s.get('id', '')).lower() == student_id.lower()]
            if all_matching_ids:
                logger.info(f"Found student with case-insensitive match: {all_matching_ids[0]}")
                return all_matching_ids[0]
            
            logger.warning(f"No student found with ID: {student_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching student by ID: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {str(e)}")
            raise

    @staticmethod
    async def get_all() -> List[Dict[str, Any]]:
        """Get all students"""
        try:
            logger.info("Attempting to fetch all students")
            
            # First verify if the table exists
            try:
                # Try to get table info
                response = supabase_client.table(StudentModel.TABLE_NAME).select("id").limit(1).execute()
                logger.info("Table exists and is accessible")
            except Exception as table_error:
                logger.error(f"Error accessing table: {str(table_error)}")
                raise Exception(f"Could not access table '{StudentModel.TABLE_NAME}'. Please verify table name and permissions.")
            
            # Now get all students
            response = supabase_client.table(StudentModel.TABLE_NAME).select("*").execute()
            logger.info(f"Found {len(response.data) if response.data else 0} students")
            
            if not response.data:
                logger.warning("No students found in the table")
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching all students: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {str(e)}")
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
            raise
