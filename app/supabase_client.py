from supabase import create_client, Client
from app.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SupabaseClient:
    _instance: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the Supabase client"""
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("Supabase URL and Key must be configured")
                
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            # Test connection
            self.client.table("users").select("*").limit(1).execute()
            
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Supabase initialization failed: {str(e)}")
            raise

    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        return self.client

# Singleton instance
supabase = SupabaseClient().get_client()