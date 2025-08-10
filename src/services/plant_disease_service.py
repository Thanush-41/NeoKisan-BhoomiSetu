"""
Plant Disease Detection Service for BhoomiSetu
Provides AI-powered plant disease detection using TensorFlow/Keras model
"""

import os
import io
import cv2
import numpy as np
import requests
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import tensorflow as tf
from keras.models import load_model
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlantDiseaseService:
    """Plant Disease Detection Service using CNN model"""
    
    def __init__(self):
        """Initialize the plant disease detection service"""
        self.model = None
        self.class_names = (
            'Tomato-Bacterial_spot', 
            'Potato-Early_blight', 
            'Corn-Common_rust'
        )
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'plant_disease_model.h5')
        self.load_model()
        
    def load_model(self):
        """Load the pre-trained plant disease detection model"""
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                logger.info(f"Plant disease model loaded successfully from {self.model_path}")
            else:
                logger.error(f"Model file not found at {self.model_path}")
                raise FileNotFoundError(f"Model file not found at {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading plant disease model: {e}")
            raise
    
    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Preprocess uploaded image for model prediction
        
        Args:
            image_bytes: Raw image bytes from upload
            
        Returns:
            Preprocessed image array ready for model prediction
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            # Decode image using OpenCV
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode image")
            
            # Resize image to model input size (256x256)
            image = cv2.resize(image, (256, 256))
            
            # Convert BGR to RGB (OpenCV uses BGR by default)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values to [0,1] range
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension: (1, 256, 256, 3)
            image = np.expand_dims(image, axis=0)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise ValueError(f"Error preprocessing image: {e}")
    
    def predict_disease(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predict plant disease from uploaded image
        
        Args:
            image_bytes: Raw image bytes from upload
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            if self.model is None:
                raise RuntimeError("Model not loaded. Please check model file.")
            
            # Preprocess image
            processed_image = self.preprocess_image(image_bytes)
            
            # Make prediction
            predictions = self.model.predict(processed_image)
            
            # Get predicted class and confidence
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_disease = self.class_names[predicted_class_idx]
            
            # Parse disease information
            plant_type = predicted_disease.split('-')[0]
            disease_name = predicted_disease.split('-')[1].replace('_', ' ')
            
            # Get all class probabilities
            class_probabilities = {
                self.class_names[i]: float(predictions[0][i]) 
                for i in range(len(self.class_names))
            }
            
            result = {
                "success": True,
                "plant_type": plant_type,
                "disease_name": disease_name,
                "full_prediction": predicted_disease,
                "confidence": confidence,
                "confidence_percentage": round(confidence * 100, 2),
                "class_probabilities": class_probabilities,
                "timestamp": tf.timestamp().numpy() if hasattr(tf, 'timestamp') else None
            }
            
            logger.info(f"Disease prediction successful: {plant_type} - {disease_name} ({confidence:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Error predicting disease: {e}")
            return {
                "success": False,
                "error": str(e),
                "plant_type": None,
                "disease_name": None,
                "confidence": 0.0
            }
    
    async def get_disease_description(self, disease_name: str, language: str = "English") -> str:
        """
        Get AI-generated disease description in specified language
        
        Args:
            disease_name: Name of the detected disease
            language: Target language for description
            
        Returns:
            Detailed disease description with symptoms, causes, and treatments
        """
        try:
            # Get Groq API key from environment
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                logger.warning("GROQ_API_KEY not found in environment variables")
                return f"Disease detected: {disease_name}. Please consult agricultural experts for detailed information."
            
            # Create language-specific prompts
            prompts = {
                "English": f"Describe the plant disease: {disease_name}. Provide symptoms, causes, and possible treatments in detail.",
                "Hindi": f"पौधे की बीमारी का वर्णन करें: {disease_name}। लक्षण, कारण और संभावित उपचार विस्तार से प्रदान करें। हिंदी में उत्तर दें।",
                "Telugu": f"మొక్కల వ్యాధిని వివరించండి: {disease_name}. లక్ష్యణాలు, కారణాలు మరియు సాధ్యమైన చికిత్సలను వివరంగా అందించండి। తెలుగులో సమాధానం ఇవ్వండి।",
                "Bengali": f"উদ্ভিদের রোগ বর্ণনা করুন: {disease_name}। লক্ষণ, কারণ এবং সম্ভাব্য চিকিৎসা বিস্তারিতভাবে প্রদান করুন। বাংলায় উত্তর দিন।",
                "Tamil": f"தாவர நோயை விவரிக்கவும்: {disease_name}. அறிகுறிகள், காரணங்கள் மற்றும் சாத்தியமான சிகிச்சைகளை விரிவாக வழங்கவும். தமிழில் பதிலளிக்கவும்।",
                "Marathi": f"वनस्पती रोगाचे वर्णन करा: {disease_name}. लक्षणे, कारणे आणि संभाव्य उपचार तपशीलवार प्रदान करा. मराठीत उत्तर द्या।",
                "Gujarati": f"છોડના રોગનું વર્ણન કરો: {disease_name}. લક્ષણો, કારણો અને સંભવિત સારવાર વિગતવાર આપો. ગુજરાતીમાં જવાબ આપો।",
                "Kannada": f"ಸಸ್ಯ ರೋಗವನ್ನು ವಿವರಿಸಿ: {disease_name}. ಲಕ್ಷಣಗಳು, ಕಾರಣಗಳು ಮತ್ತು ಸಂಭವನೀಯ ಚಿಕಿತ್ಸೆಗಳನ್ನು ವಿವರವಾಗಿ ಒದಗಿಸಿ. ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ।",
                "Malayalam": f"സസ്യരോഗം വിവരിക്കുക: {disease_name}. ലക്ഷണങ്ങൾ, കാരണങ്ങൾ, സാധ്യമായ ചികിത്സകൾ എന്നിവ വിശദമായി നൽകുക. മലയാളത്തിൽ ഉത്തരം നൽകുക।",
                "Punjabi": f"ਪੌਧੇ ਦੀ ਬਿਮਾਰੀ ਦਾ ਵਰਣਨ ਕਰੋ: {disease_name}। ਲੱਛਣ, ਕਾਰਨ ਅਤੇ ਸੰਭਾਵਿਤ ਇਲਾਜ ਵਿਸਤਾਰ ਨਾਲ ਪ੍ਰਦਾਨ ਕਰੋ। ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ।"
            }
            
            prompt = prompts.get(language, prompts["English"])
            
            # Prepare API request
            headers = {
                'Authorization': f'Bearer {groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Make API request
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                description = result['choices'][0]['message']['content']
                return description
            else:
                logger.warning(f"Groq API returned status code: {response.status_code}")
                return f"Disease detected: {disease_name}. API temporarily unavailable. Please consult agricultural experts."
                    
        except Exception as e:
            logger.error(f"Error getting disease description: {e}")
            return f"Disease detected: {disease_name}. Error fetching detailed description. Please consult agricultural experts."
    
    def get_treatment_recommendations(self, disease_name: str) -> Dict[str, Any]:
        """
        Get treatment recommendations for detected disease
        
        Args:
            disease_name: Name of the detected disease
            
        Returns:
            Dictionary containing treatment recommendations
        """
        # Basic treatment recommendations (can be expanded with more detailed database)
        treatments = {
            "Bacterial_spot": {
                "preventive_measures": [
                    "Use disease-free seeds and transplants",
                    "Avoid overhead irrigation",
                    "Provide adequate plant spacing for air circulation",
                    "Remove infected plant debris"
                ],
                "chemical_control": [
                    "Copper-based fungicides (Copper hydroxide, Copper sulfate)",
                    "Streptomycin sulfate for bacterial control",
                    "Mancozeb + Copper oxychloride combination"
                ],
                "organic_control": [
                    "Neem oil spray",
                    "Bacillus subtilis biological control",
                    "Compost tea application",
                    "Baking soda solution (1 tsp per liter)"
                ],
                "cultural_practices": [
                    "Crop rotation with non-solanaceous crops",
                    "Drip irrigation instead of sprinkler",
                    "Mulching to prevent soil splash",
                    "Pruning lower leaves for air circulation"
                ]
            },
            "Early_blight": {
                "preventive_measures": [
                    "Choose resistant varieties when available",
                    "Ensure proper plant nutrition, especially potassium",
                    "Avoid overhead watering",
                    "Remove plant debris after harvest"
                ],
                "chemical_control": [
                    "Mancozeb fungicide",
                    "Chlorothalonil",
                    "Azoxystrobin",
                    "Copper fungicides"
                ],
                "organic_control": [
                    "Compost and organic matter application",
                    "Bacillus-based biopesticides",
                    "Neem oil applications",
                    "Milk spray (1:10 ratio with water)"
                ],
                "cultural_practices": [
                    "Crop rotation (3-4 year cycle)",
                    "Proper spacing for air circulation",
                    "Timely harvest to reduce inoculum",
                    "Balanced fertilization"
                ]
            },
            "Common_rust": {
                "preventive_measures": [
                    "Plant resistant corn varieties",
                    "Monitor weather conditions (high humidity favors rust)",
                    "Avoid late planting in rust-prone areas",
                    "Remove alternate hosts if present"
                ],
                "chemical_control": [
                    "Propiconazole fungicide",
                    "Azoxystrobin",
                    "Pyraclostrobin",
                    "Tebuconazole"
                ],
                "organic_control": [
                    "Sulfur-based fungicides",
                    "Potassium bicarbonate spray",
                    "Compost tea applications",
                    "Beneficial microorganism inoculants"
                ],
                "cultural_practices": [
                    "Plant early maturing varieties",
                    "Adequate plant spacing",
                    "Balanced nitrogen fertilization",
                    "Field sanitation practices"
                ]
            }
        }
        
        # Clean disease name to match treatment keys
        clean_disease_name = disease_name.replace(' ', '_')
        
        return treatments.get(clean_disease_name, {
            "message": f"General treatment recommendations for {disease_name}",
            "general_advice": [
                "Consult local agricultural extension officers",
                "Ensure proper plant nutrition and irrigation",
                "Monitor plants regularly for early detection",
                "Follow integrated pest management practices"
            ]
        })

# Create global instance
plant_disease_service = PlantDiseaseService()
