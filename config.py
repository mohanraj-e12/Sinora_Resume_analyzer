import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "sinora_ai_super_secret_key_2026_x89a3")
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///sinora_ai.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload & File Storage
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads")
    REPORTS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "reports")
    CHARTS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "charts")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file upload size
    
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "zip"}
    
    # Gemini AI API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
