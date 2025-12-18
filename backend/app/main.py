"""
FastAPI backend for EcoVision Waste Classification System
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.ml.predictor import WasteClassifier
from app.api import routes
from app.api import chatbot_routes

# Initialize FastAPI app
app = FastAPI(
    title="EcoVision API",
    description="Smart Waste Segregation System API",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML model on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the ML model when server starts"""
    try:
        app.state.classifier = WasteClassifier()
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("⚠️  Server will run but predictions will fail until model is trained")
        app.state.classifier = None

# Include API routes
app.include_router(routes.router, prefix="/api")
app.include_router(chatbot_routes.router, prefix="/api/chatbot", tags=["chatbot"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to EcoVision API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "model_loaded": app.state.classifier is not None if hasattr(app.state, "classifier") else False
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_status": "loaded" if hasattr(app.state, "classifier") and app.state.classifier is not None else "not_loaded"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )