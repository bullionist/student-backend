from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, List, Any, Union

class ExamScores(BaseModel):
    """Schema for exam scores"""
    exam_name: str
    score: Union[str, float, int]
    date: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AdditionalPreferences(BaseModel):
    """Schema for additional preferences"""
    study_mode: Optional[str] = None  # e.g., "Full-time", "Part-time"
    budget: Optional[Union[str, float, int]] = None
    start_date: Optional[str] = None
    specific_interests: Optional[List[str]] = Field(default_factory=list)
    other: Optional[Dict[str, Any]] = None

class ConversationMessage(BaseModel):
    """Schema for a single conversation message"""
    role: str  # "system", "user", or "assistant"
    content: str
    timestamp: str

class ConversationHistory(BaseModel):
    """Schema for conversation history"""
    messages: List[ConversationMessage] = Field(default_factory=list)

class StudentBase(BaseModel):
    """Base schema for student data"""
    name: str
    email: Optional[str] = None
    academic_background: Optional[str] = None
    preferred_location: Optional[str] = None
    field_of_study: Optional[str] = None
    exam_scores: Optional[List[ExamScores]] = Field(default_factory=list)
    additional_preferences: Optional[AdditionalPreferences] = None
    conversation_history: ConversationHistory = Field(default_factory=ConversationHistory)

class StudentCreate(StudentBase):
    """Schema for creating a new student session"""
    pass

class StudentResponse(StudentBase):
    """Schema for student response data"""
    id: str

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    """Schema for updating student data"""
    name: Optional[str] = None
    email: Optional[str] = None
    academic_background: Optional[str] = None
    preferred_location: Optional[str] = None
    field_of_study: Optional[str] = None
    exam_scores: Optional[List[ExamScores]] = None
    additional_preferences: Optional[AdditionalPreferences] = None

class AnalyzeInput(BaseModel):
    """Schema for text input to be analyzed"""
    text: str
