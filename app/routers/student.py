from fastapi import APIRouter, HTTPException, status, Body, Request
from app.schemas.student import (
    StudentCreate, StudentResponse, StudentUpdate, AnalyzeInput,
    ChatResponse
)
from app.models.student import StudentModel
from app.services.openai_agent_service import OpenAIAgentService
from typing import Dict, Any, List
from loguru import logger

router = APIRouter(
    prefix="/api/students",
    tags=["students"]
)

# Initialize OpenAI service
openai_service = OpenAIAgentService()

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate):
    """Create a new student."""
    try:
        result = await StudentModel.create(student)
        return result
    except Exception as e:
        logger.error(f"Error creating student: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create student"
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

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: str, student_update: StudentUpdate):
    """Update a student's information."""
    try:
        # Check if student exists
        existing_student = await StudentModel.get_by_id(student_id)
        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )
            
        result = await StudentModel.update(student_id, student_update)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating student: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update student"
        )

@router.post("/{student_id}/conversation", response_model=ChatResponse)
async def handle_student_conversation(student_id: str, input_data: AnalyzeInput):
    """
    Main conversation endpoint for student interactions.
    This endpoint uses a multi-agent architecture to:
    1. Chat with the student using the counselor agent
    2. Extract relevant information from the conversation
    3. Use the program matcher agent to find suitable programs when needed
    
    Request:
    {
        "text": "Your message here"
    }
    
    Response:
    {
        "success": true,
        "response": "AI response"
    }
    """
    try:
        # Check if student exists
        existing_student = await StudentModel.get_by_id(student_id)
        if not existing_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found"
            )
            
        # Ensure preferred_location is a list for backward compatibility
        if "preferred_location" in existing_student and isinstance(existing_student["preferred_location"], str):
            existing_student["preferred_location"] = [existing_student["preferred_location"]]
        
        # Generate chat response using OpenAI Agents
        chat_response = await openai_service.chat_with_student(
            student_data=existing_student,
            message=input_data.text,
            conversation_history=[]  # Empty list since we no longer store history
        )
        
        return chat_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling student conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process conversation"
        )
