from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

class Settings:
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE: str = os.getenv("SUPABASE_SERVICE_ROLE", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "300"))  # 5 minutes
    PIN_ATTEMPTS_LIMIT: int = int(os.getenv("PIN_ATTEMPTS_LIMIT", "3"))
    
    # Security
    API_KEY: Optional[str] = os.getenv("API_KEY")
    
    def validate(self):
        """Validate required configuration"""
        if not self.SUPABASE_URL or not self.SUPABASE_KEY:
            raise ValueError("Supabase URL and Key must be configured")
        if not self.SUPABASE_SERVICE_ROLE or not self.SUPABASE_JWT_SECRET:
            raise ValueError("Supabase service role and JWT secret must be configured")

settings = Settings()
settings.validate()