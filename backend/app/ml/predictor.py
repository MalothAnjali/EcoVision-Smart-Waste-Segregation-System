"""
Waste Classification Model Predictor
"""
import numpy as np
from PIL import Image
import tensorflow as tf
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings


class WasteClassifier:
    """Waste classification using TensorFlow Lite model"""
    
    def __init__(self):
        """Initialize the classifier"""
        self.model_path = settings.BASE_DIR / settings.MODEL_PATH
        self.input_size = settings.MODEL_INPUT_SIZE
        self.class_names = settings.CLASS_NAMES
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        
        self._load_model()
    
    def _load_model(self):
        """Load the TensorFlow Lite model"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                f"Please train the model first using backend/scripts/train_model.py"
            )
        
        # Load TFLite model
        self.interpreter = tf.lite.Interpreter(model_path=str(self.model_path))
        self.interpreter.allocate_tensors()
        
        # Get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        print(f"✅ Model loaded from {self.model_path}")
        print(f"   Input shape: {self.input_details[0]['shape']}")
        print(f"   Output shape: {self.output_details[0]['shape']}")
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess image for model input
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed numpy array
        """
        # Resize image
        image = image.resize((self.input_size, self.input_size), Image.LANCZOS)
        
        # Convert to array
        img_array = np.array(image, dtype=np.float32)
        
        # Normalize to [0, 1]
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predict waste class for an image
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with prediction results
        """
        # Preprocess image
        input_data = self.preprocess_image(image)
        
        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        
        # Run inference
        self.interpreter.invoke()
        
        # Get output tensor
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        predictions = output_data[0]  # Remove batch dimension
        
        # Get top prediction
        class_id = np.argmax(predictions)
        confidence = predictions[class_id]
        class_name = self.class_names[class_id]
        
        return {
            "class_id": int(class_id),
            "class_name": class_name,
            "confidence": float(confidence),
            "all_confidences": predictions.tolist()
        }
    
    def predict_batch(self, images: list) -> list:
        """
        Predict waste class for multiple images
        
        Args:
            images: List of PIL Images
            
        Returns:
            List of prediction results
        """
        return [self.predict(img) for img in images]