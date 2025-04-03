from fastapi import APIRouter, HTTPException, status
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate, AnalyzeInput
from app.models.student import StudentModel
from app.services.groq_service import GroqService
from typing import Dict, Any
from loguru import logger

router = APIRouter(
    prefix="/api/students",
    tags=["students"]
)

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student_session(student: StudentCreate):
    """Create a new student session."""
    try:
        result = await StudentModel.create(student)
        return result
    except Exception as e:
        logger.error(f"Error creating student session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create student session"
        )

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str):
    """Get a specific student by ID."""
    try:
        result = await StudentModel.get_by_id(student_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve student"
        )

@router.post("/{student_id}/analyze", response_model=Dict[str, Any])
async def analyze_student_input(student_id: str, input_data: AnalyzeInput):
    """
    Process student input using Groq API to extract structured data.
    
    Returns the extracted information and updates the student profile.
    """
    try:
        # Check if student exists
        existing_student = await StudentModel.get_by_id(student_id)
        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )
            
        # Add the user message to conversation history
        await StudentModel.add_conversation_message(
            student_id=student_id,
            role="user",
            content=input_data.text
        )
            
        # Process the input using Groq API
        extracted_data = await GroqService.extract_student_details(input_data.text)
        
        # Check if extraction was successful
        if "error" in extracted_data:
            # Still record the response but include error
            await StudentModel.add_conversation_message(
                student_id=student_id,
                role="system",
                content=f"Error processing input: {extracted_data.get('error')}"
            )
            return {
                "success": False,
                "error": extracted_data.get("error"),
                "message": "Failed to extract structured data from input"
            }
            
        # Update student profile with extracted data
        update_data = StudentUpdate()
        
        # Conditionally update fields if they exist in the extracted data
        if "academic_background" in extracted_data:
            update_data.academic_background = extracted_data["academic_background"]
            
        if "preferred_location" in extracted_data:
            update_data.preferred_location = extracted_data["preferred_location"]
            
        if "field_of_study" in extracted_data:
            update_data.field_of_study = extracted_data["field_of_study"]
            
        if "exam_scores" in extracted_data:
            update_data.exam_scores = extracted_data["exam_scores"]
            
        if "additional_preferences" in extracted_data:
            update_data.additional_preferences = extracted_data["additional_preferences"]
            
        # Update the student record if we have data
        if any(getattr(update_data, field) is not None for field in update_data.__fields__):
            await StudentModel.update(student_id, update_data)
            
        # Add a confirmation message to the conversation
        confirmation = "Thank you for providing this information. I've updated your profile with these details."
        await StudentModel.add_conversation_message(
            student_id=student_id,
            role="assistant",
            content=confirmation
        )
            
        # Return the extracted data with a success flag
        return {
            "success": True,
            "message": "Successfully extracted and updated student data",
            "extracted_data": extracted_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing student input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze student input"
        )
