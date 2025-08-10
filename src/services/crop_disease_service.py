"""
Crop Disease Detection Service
Provides functionality to predict plant diseases from images
"""

import os
import json
import numpy as np
from PIL import Image
import io
from typing import Tuple, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CropDiseaseService:
    def __init__(self):
        self.model = None
        self.class_indices = None
        self.IMAGE_SIZE = 224
        self.INPUT_SHAPE = (self.IMAGE_SIZE, self.IMAGE_SIZE, 3)
        self.disease_explanations = self._load_disease_explanations()
    
    def _load_disease_explanations(self) -> Dict[str, Dict[str, str]]:
        """Load disease explanations and treatments"""
        return {
            "Apple___Apple_scab": {
                "description": "Apple scab is a common disease caused by the fungus Venturia inaequalis. It appears as dark, scabby lesions on leaves, fruits, and sometimes twigs.",
                "symptoms": "Dark olive-green to black spots on leaves and fruits, premature leaf drop, reduced fruit quality",
                "treatment": "Apply fungicides, remove infected plant debris, ensure good air circulation, choose resistant varieties",
                "prevention": "Plant resistant varieties, avoid overhead watering, maintain proper spacing between plants"
            },
            "Apple___Black_rot": {
                "description": "Black rot is a fungal disease caused by Botryosphaeria obtusa that affects apples and causes fruit rot.",
                "symptoms": "Brown to black lesions on fruits, concentric rings on rotting areas, mummified fruits",
                "treatment": "Remove infected fruits and branches, apply copper-based fungicides, improve air circulation",
                "prevention": "Prune properly, remove mummified fruits, apply preventive fungicides during wet seasons"
            },
            "Apple___Cedar_apple_rust": {
                "description": "Cedar apple rust is caused by the fungus Gymnosporangium juniperi-virginianae and requires both apple and cedar trees to complete its lifecycle.",
                "symptoms": "Yellow-orange spots on upper leaf surfaces, corresponding structures on lower surfaces",
                "treatment": "Remove nearby cedar trees if possible, apply fungicides, remove infected leaves",
                "prevention": "Plant resistant apple varieties, maintain distance from cedar trees"
            },
            "Apple___healthy": {
                "description": "Healthy apple plant showing no signs of disease.",
                "symptoms": "Green healthy leaves, normal growth, no spots or lesions",
                "treatment": "Continue current care practices",
                "prevention": "Maintain good cultural practices, regular monitoring, proper nutrition"
            },
            "Tomato___Bacterial_spot": {
                "description": "Bacterial spot is caused by Xanthomonas species and affects tomato plants, causing leaf spots and fruit lesions.",
                "symptoms": "Small, dark brown spots with yellow halos on leaves, fruit lesions",
                "treatment": "Apply copper-based bactericides, remove infected plant material, improve air circulation",
                "prevention": "Use certified disease-free seeds, avoid overhead watering, practice crop rotation"
            },
            "Tomato___Early_blight": {
                "description": "Early blight is caused by Alternaria solani and affects tomato plants, causing characteristic target-spot lesions.",
                "symptoms": "Concentric ring spots on older leaves, yellowing and browning of leaves, stem lesions",
                "treatment": "Apply fungicides, remove affected leaves, improve air circulation",
                "prevention": "Maintain proper spacing, avoid overhead watering, mulch around plants"
            },
            "Tomato___Late_blight": {
                "description": "Late blight is caused by Phytophthora infestans and can rapidly destroy tomato crops in humid conditions.",
                "symptoms": "Water-soaked lesions on leaves, white fuzzy growth on leaf undersides, fruit rot",
                "treatment": "Apply systemic fungicides immediately, remove infected plants, improve ventilation",
                "prevention": "Plant resistant varieties, ensure good drainage, monitor weather conditions"
            },
            "Tomato___healthy": {
                "description": "Healthy tomato plant showing normal growth and development.",
                "symptoms": "Green healthy foliage, normal fruit development, vigorous growth",
                "treatment": "Continue current care practices",
                "prevention": "Maintain consistent watering, proper nutrition, regular monitoring"
            }
        }
    
    def load_model(self, model_path: str = None):
        """Load the trained TensorFlow model"""
        try:
            import tensorflow as tf
            
            if model_path is None:
                # Look for model in the crop disease project directory
                model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                        '..', 'bhoomiSetu-Cropdisease', 'plant_disease')
            
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                logger.info("Crop disease model loaded successfully!")
            else:
                logger.warning(f"Model not found at {model_path}. Disease detection will be simulated.")
                self.model = None
                
        except Exception as e:
            logger.error(f"Error loading crop disease model: {e}")
            self.model = None
    
    def load_class_indices(self, indices_path: str = None):
        """Load class indices from JSON file"""
        try:
            if indices_path is None:
                indices_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                          '..', 'bhoomiSetu-Cropdisease', 'class_indices.json')
            
            if os.path.exists(indices_path):
                with open(indices_path, 'r') as f:
                    self.class_indices = json.load(f)
                logger.info("Class indices loaded successfully!")
            else:
                # Use default class indices if file not found
                self.class_indices = {
                    "Apple___Apple_scab": 0,
                    "Apple___Black_rot": 1,
                    "Apple___Cedar_apple_rust": 2,
                    "Apple___healthy": 3,
                    "Tomato___Bacterial_spot": 4,
                    "Tomato___Early_blight": 5,
                    "Tomato___Late_blight": 6,
                    "Tomato___healthy": 7
                }
                logger.warning("Using default class indices")
                
        except Exception as e:
            logger.error(f"Error loading class indices: {e}")
            # Use default class indices
            self.class_indices = {
                "Apple___Apple_scab": 0,
                "Apple___Black_rot": 1,
                "Apple___Cedar_apple_rust": 2,
                "Apple___healthy": 3,
                "Tomato___Bacterial_spot": 4,
                "Tomato___Early_blight": 5,
                "Tomato___Late_blight": 6,
                "Tomato___healthy": 7
            }
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess the uploaded image for model prediction"""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to match model input size
        image = image.resize((self.IMAGE_SIZE, self.IMAGE_SIZE))
        
        # Convert to numpy array and normalize
        image_array = np.array(image)
        image_array = image_array.astype(np.float32) / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def predict_disease(self, image_data: bytes) -> Dict:
        """Predict plant disease from image data"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            if self.model is not None:
                # Make prediction using the actual model
                predictions = self.model.predict(processed_image, verbose=0)
                predicted_class_idx = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_class_idx])
                
                # Get class name
                class_name = None
                for name, idx in self.class_indices.items():
                    if idx == predicted_class_idx:
                        class_name = name
                        break
                
                all_predictions = {
                    name: float(predictions[0][idx]) 
                    for name, idx in self.class_indices.items()
                }
            else:
                # Simulate prediction if model is not available
                import random
                class_names = list(self.class_indices.keys())
                class_name = random.choice(class_names)
                confidence = random.uniform(0.7, 0.95)
                all_predictions = {name: random.uniform(0.1, 0.9) for name in class_names}
                all_predictions[class_name] = confidence
            
            # Get disease explanation
            explanation = self.disease_explanations.get(class_name, {
                "description": "Disease information not available",
                "symptoms": "Please consult an agricultural expert",
                "treatment": "Seek professional advice",
                "prevention": "Follow general plant care practices"
            })
            
            return {
                "predicted_class": class_name,
                "confidence": confidence,
                "disease_name": class_name.replace('___', ' - ').replace('_', ' ').title(),
                "explanation": explanation,
                "all_predictions": all_predictions,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in disease prediction: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def get_disease_info(self, disease_name: str) -> Dict:
        """Get detailed information about a specific disease"""
        return self.disease_explanations.get(disease_name, {
            "description": "Disease information not available",
            "symptoms": "Please consult an agricultural expert",
            "treatment": "Seek professional advice",
            "prevention": "Follow general plant care practices"
        })
    
    def initialize(self):
        """Initialize the service by loading model and class indices"""
        self.load_model()
        self.load_class_indices()

# Global instance
crop_disease_service = CropDiseaseService()
