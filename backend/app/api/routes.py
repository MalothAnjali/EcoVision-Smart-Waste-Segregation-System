"""
API routes for waste classification
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from PIL import Image
import io
import numpy as np
from typing import Dict, Any

from app.core.config import settings

router = APIRouter()

@router.post("/classify")
async def classify_waste(
    request: Request,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Classify uploaded waste image
    
    Args:
        file: Uploaded image file
        
    Returns:
        Classification results with predictions and visualization data
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check if classifier is loaded
    if not hasattr(request.app.state, "classifier") or request.app.state.classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first using backend/scripts/train_model.py"
        )
    
    try:
        # Read and validate image
        contents = await file.read()
        
        # Check file size
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        # Open image
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get predictions
        classifier = request.app.state.classifier
        predictions = classifier.predict(image)
        
        # Get top prediction
        top_class_idx = predictions['class_id']
        top_class = predictions['class_name']
        confidence = predictions['confidence']
        
        # Get color for the class
        class_color = settings.CLASS_COLORS[top_class_idx]
        
        # Prepare response
        response = {
            "success": True,
            "prediction": {
                "class": top_class,
                "confidence": float(confidence),
                "color": class_color,
                "class_id": int(top_class_idx)
            },
            "all_predictions": [
                {
                    "class": settings.CLASS_NAMES[i],
                    "confidence": float(predictions['all_confidences'][i]),
                    "color": settings.CLASS_COLORS[i]
                }
                for i in range(len(settings.CLASS_NAMES))
            ],
            "metadata": {
                "image_size": f"{image.width}x{image.height}",
                "model": "MobileNetV2 (TFLite)"
            }
        }
        
        return response
        
    except Image.UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.get("/classes")
async def get_classes() -> Dict[str, Any]:
    """
    Get available waste classes and their colors
    
    Returns:
        List of classes with their colors
    """
    return {
        "classes": [
            {
                "id": i,
                "name": name,
                "color": color,
                "description": get_class_description(name)
            }
            for i, (name, color) in enumerate(zip(settings.CLASS_NAMES, settings.CLASS_COLORS))
        ]
    }

@router.get("/model/info")
async def get_model_info(request: Request) -> Dict[str, Any]:
    """
    Get information about the loaded model
    
    Returns:
        Model configuration and status
    """
    if not hasattr(request.app.state, "classifier") or request.app.state.classifier is None:
        return {
            "loaded": False,
            "message": "Model not loaded. Please train the model first."
        }
    
    classifier = request.app.state.classifier
    
    return {
        "loaded": True,
        "model_type": "TensorFlow Lite",
        "input_size": settings.MODEL_INPUT_SIZE,
        "num_classes": len(settings.CLASS_NAMES),
        "classes": settings.CLASS_NAMES,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD
    }

def get_class_description(class_name: str) -> str:
    """Get description for each waste class"""
    descriptions = {
        "Recyclable": "Materials that can be recycled: plastic bottles, paper, cardboard, metal cans",
        "Non-Recyclable": "Items that cannot be recycled: mixed waste, contaminated materials",
        "Hazardous": "Dangerous waste requiring special handling: batteries, chemicals, paints, pesticides",
        "Organic": "Biodegradable waste: food scraps, yard waste, compostable materials"
    }
    return descriptions.get(class_name, "No description available")