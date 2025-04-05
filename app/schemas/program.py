from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, List, Any, Union

class EligibilityCriteria(BaseModel):
    """Schema for eligibility criteria"""
    qualifications: Optional[List[str]] = Field(default_factory=list)
    experience: Optional[str] = None
    age_limit: Optional[str] = None
    other_requirements: Optional[List[str]] = Field(default_factory=list)

class CurriculumModule(BaseModel):
    """Schema for a curriculum module"""
    name: str
    description: Optional[str] = None
    credits: Optional[int] = None

class Curriculum(BaseModel):
    """Schema for program curriculum"""
    core_modules: List[CurriculumModule] = Field(default_factory=list)
    elective_modules: Optional[List[CurriculumModule]] = Field(default_factory=list)

class ProgramBase(BaseModel):
    """Base schema for program data"""
    program_title: str
    institution: str
    program_overview: str
    eligibility_criteria: EligibilityCriteria
    duration: str
    fees: Union[str, float, int]
    curriculum: Curriculum
    mode_of_delivery: str
    application_details: str
    location: str
    additional_notes: Optional[str] = None

class ProgramCreate(ProgramBase):
    """Schema for creating a new program"""
    pass

class ProgramResponse(ProgramBase):
    """Schema for program response data"""
    id: str

    class Config:
        from_attributes = True

class ProgramUpdate(BaseModel):
    """Schema for updating a program"""
    program_title: Optional[str] = None
    institution: Optional[str] = None
    program_overview: Optional[str] = None
    eligibility_criteria: Optional[EligibilityCriteria] = None
    duration: Optional[str] = None
    fees: Optional[Union[str, float, int]] = None
    curriculum: Optional[Curriculum] = None
    mode_of_delivery: Optional[str] = None
    application_details: Optional[str] = None
    location: Optional[str] = None
    additional_notes: Optional[str] = None
