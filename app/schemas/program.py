from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, List, Any, Union

class Curriculum(BaseModel):
    """Schema for program curriculum"""
    description: str
    modules: List[str] = Field(default_factory=list)

class Requirements(BaseModel):
    """Schema for program requirements"""
    academic_requirements: List[str] = Field(default_factory=list)
    other_requirements: List[str] = Field(default_factory=list)

class ProgramBase(BaseModel):
    """Base schema for program data"""
    program_title: str
    institution: str
    program_overview: str
    location: str
    program_type: str  # undergraduate/postgraduate
    field_of_study: str
    budget: int
    duration: str
    curriculum: Curriculum
    requirements: Requirements

class ProgramCreate(ProgramBase):
    """Schema for creating a new program"""
    pass

class ProgramResponse(ProgramBase):
    """Schema for program response data"""
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class ProgramUpdate(BaseModel):
    """Schema for updating a program"""
    program_title: Optional[str] = None
    institution: Optional[str] = None
    program_overview: Optional[str] = None
    location: Optional[str] = None
    program_type: Optional[str] = None
    field_of_study: Optional[str] = None
    budget: Optional[int] = None
    duration: Optional[str] = None
    curriculum: Optional[Curriculum] = None
    requirements: Optional[Requirements] = None
