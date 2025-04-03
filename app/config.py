from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Supabase configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Groq API configuration
    GROQ_API_KEY: str
    GROQ_API_URL: str = "https://api.groq.com/v1"
    
    # Application settings
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @validator('APP_ENV')
    def validate_app_env(cls, v):
        if v not in ['development', 'production', 'testing']:
            raise ValueError('APP_ENV must be one of: development, production, testing')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
