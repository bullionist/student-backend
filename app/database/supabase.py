from supabase import create_client
from app.config import settings
from loguru import logger

class SupabaseClient:
    """Singleton class to manage Supabase client connections"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            try:
                cls._instance.client = create_client(
                    settings.SUPABASE_URL, 
                    settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise e
        return cls._instance
    
    def get_client(self):
        """Returns the Supabase client instance"""
        return self.client

# Initialize client singleton
supabase_client = SupabaseClient().get_client()
