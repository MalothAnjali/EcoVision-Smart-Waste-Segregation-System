"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Model Configuration
    MODEL_PATH: str = "models/waste_classifier_v2.tflite"
    MODEL_INPUT_SIZE: int = 224
    CONFIDENCE_THRESHOLD: float = 0.5
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://0.0.0.0:5173",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Upload Configuration
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # Class Configuration
    CLASS_NAMES: List[str] = ["Recyclable", "Non-Recyclable", "Hazardous", "Organic"]
    CLASS_COLORS: List[str] = ["#22c55e", "#ef4444", "#eab308", "#3b82f6"]  # green, red, yellow, blue
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    MODEL_DIR: Path = BASE_DIR / "models"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # Gemini API Configuration
    GEMINI_API_KEY: str = "Enter your Api Key"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create necessary directories
settings.MODEL_DIR.mkdir(exist_ok=True)
settings.UPLOAD_DIR.mkdir(exist_ok=True)