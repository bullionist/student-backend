from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.program import ProgramCreate, ProgramResponse, ProgramUpdate
from app.models.program import ProgramModel
from typing import List
from loguru import logger
import supabase
from app.utils.auth import get_current_admin_user

router = APIRouter(
    prefix="/api/programs",
    tags=["programs"]
)

@router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(program: ProgramCreate, _: dict = Depends(get_current_admin_user)):
    """
    Create a new program.
    
    Requires admin authentication.
    """
    try:
        result = await ProgramModel.create(program)
        return result
    except Exception as e:
        logger.error(f"Error creating program: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create program"
        )

@router.get("", response_model=List[ProgramResponse])
async def get_all_programs(_: dict = Depends(get_current_admin_user)):
    """
    Get all programs.
    
    Requires admin authentication.
    """
    try:
        result = await ProgramModel.get_all()
        return result
    except Exception as e:
        logger.error(f"Error getting all programs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve programs"
        )

@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program(program_id: str, _: dict = Depends(get_current_admin_user)):
    """
    Get a specific program by ID.
    
    Requires admin authentication.
    """
    try:
        result = await ProgramModel.get_by_id(program_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting program by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve program"
        )

@router.put("/{program_id}", response_model=ProgramResponse)
async def update_program(program_id: str, program_update: ProgramUpdate, _: dict = Depends(get_current_admin_user)):
    """
    Update a program.
    
    Requires admin authentication.
    """
    try:
        # Check if program exists
        existing_program = await ProgramModel.get_by_id(program_id)
        if not existing_program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )
            
        result = await ProgramModel.update(program_id, program_update)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating program: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update program"
        )

@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(program_id: str, _: dict = Depends(get_current_admin_user)):
    """
    Delete a program.
    
    Requires admin authentication.
    """
    try:
        # Check if program exists
        existing_program = await ProgramModel.get_by_id(program_id)
        if not existing_program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )
            
        success = await ProgramModel.delete(program_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete program"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting program: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete program"
        )
