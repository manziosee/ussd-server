from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "300"))  # 5 minutes
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()