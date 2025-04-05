from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

class ExamScores(BaseModel):
    """Model for student exam scores."""
    exam_name: str
    score: str
    date_taken: Optional[datetime] = None
    validity_period: Optional[int] = None  # in months

class AdditionalPreferences(BaseModel):
    """Model for student's additional preferences."""
    study_mode: Optional[str] = None  # online, offline, hybrid
    budget_range: Optional[str] = None
    duration_preference: Optional[str] = None  # short-term, long-term
    start_date_preference: Optional[datetime] = None
    special_requirements: Optional[List[str]] = None
    career_goals: Optional[List[str]] = None
    preferred_languages: Optional[List[str]] = None

class ConversationMessage(BaseModel):
    """Model for a single conversation message."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ConversationHistory(BaseModel):
    """Model for student's conversation history."""
    messages: List[ConversationMessage] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class AcademicBackground(BaseModel):
    """Model for student's academic background."""
    current_education: str
    subjects: List[str]
    grades: str
    institution: Optional[str] = None
    year_of_completion: Optional[int] = None
    achievements: Optional[List[str]] = None

class StudentBase(BaseModel):
    """Base model for student data."""
    name: str
    email: Optional[str] = None
    academic_background: AcademicBackground
    preferred_location: str
    field_of_study: str
    exam_scores: List[ExamScores] = Field(default_factory=list)
    additional_preferences: AdditionalPreferences = Field(default_factory=AdditionalPreferences)
    conversation_history: Optional[ConversationHistory] = Field(default_factory=ConversationHistory)

class StudentCreate(StudentBase):
    """Model for creating a new student."""
    pass

class StudentResponse(StudentBase):
    """Model for student response data."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    """Model for updating student information."""
    name: Optional[str] = None
    email: Optional[str] = None
    academic_background: Optional[AcademicBackground] = None
    preferred_location: Optional[str] = None
    field_of_study: Optional[str] = None
    exam_scores: Optional[List[ExamScores]] = None
    additional_preferences: Optional[AdditionalPreferences] = None

class AnalyzeInput(BaseModel):
    """Model for student input analysis."""
    text: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Model for chat response."""
    success: bool
    response: str
    error: Optional[str] = None
