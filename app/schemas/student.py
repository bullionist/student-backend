from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class EducationalQualification(BaseModel):
    """Model for student's educational qualification."""
    qualification: str
    grade: str
    year_of_completion: int

class StudentBase(BaseModel):
    """Base model for student data."""
    name: str
    email: EmailStr
    educational_qualifications: List[EducationalQualification]
    preferred_location: List[str] = Field(default_factory=list)
    preferred_program: str  # undergraduate/postgraduate
    preferred_field_of_study: List[str] = Field(default_factory=list)
    budget: int
    special_requirements: Optional[List[str]] = Field(default_factory=list)

class StudentCreate(StudentBase):
    """Model for creating a new student."""
    pass

class StudentResponse(StudentBase):
    """Model for student response data."""
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    """Model for updating student information."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    educational_qualifications: Optional[List[EducationalQualification]] = None
    preferred_location: Optional[List[str]] = None
    preferred_program: Optional[str] = None
    preferred_field_of_study: Optional[List[str]] = None
    budget: Optional[int] = None
    special_requirements: Optional[List[str]] = None

class AnalyzeInput(BaseModel):
    """Model for student input analysis."""
    text: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    """Model for chat response."""
    success: bool
    response: str
    error: Optional[str] = None
