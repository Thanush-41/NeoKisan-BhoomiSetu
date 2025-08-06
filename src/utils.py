"""
Utility functions for BhoomiSetu Agricultural AI Agent
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidator:
    """Validate and clean data from various sources"""
    
    @staticmethod
    def validate_weather_data(data: Dict) -> bool:
        """Validate weather data structure"""
        required_fields = ['main', 'weather', 'wind']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_price_data(data: Dict) -> bool:
        """Validate commodity price data"""
        required_fields = ['commodity', 'market', 'modal_price']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text input"""
        if not text:
            return ""
        return text.strip().lower()

class CacheManager:
    """Simple in-memory cache for API responses"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.default_ttl):
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Dict) -> None:
        """Cache data with timestamp"""
        self.cache[key] = (data, datetime.now())
    
    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()

class TextProcessor:
    """Process and analyze agricultural text queries"""
    
    IRRIGATION_KEYWORDS = [
        'irrigate', 'irrigation', 'water', 'watering', 'sprinkle',
        'पानी', 'सिंचाई', 'पानी देना', 'నీరు', 'నీటిపోత'
    ]
    
    CROP_KEYWORDS = [
        'crop', 'seed', 'variety', 'plant', 'sow', 'grow',
        'फसल', 'बीज', 'किस्म', 'बोना', 'పంట', 'విత్తనం', 'రకం'
    ]
    
    WEATHER_KEYWORDS = [
        'weather', 'rain', 'temperature', 'climate', 'forecast',
        'मौसम', 'बारिश', 'तापमान', 'వాతావరణం', 'వర్షం', 'ఉష్ణోగ్రత'
    ]
    
    PRICE_KEYWORDS = [
        'price', 'cost', 'market', 'sell', 'buy', 'rate',
        'दाम', 'भाव', 'बाजार', 'बेचना', 'ధర', 'మార్కెట్', 'అమ్మకం'
    ]
    
    FINANCE_KEYWORDS = [
        'loan', 'credit', 'scheme', 'subsidy', 'money', 'finance',
        'ऋण', 'कर्ज', 'योजना', 'सब्सिडी', 'రుణం', 'పథకం', 'సబ్సిడీ'
    ]
    
    @staticmethod
    def extract_location(text: str) -> Optional[str]:
        """Extract location from text query"""
        # Common location indicators
        location_indicators = ['in', 'at', 'from', 'near', 'में', 'से', 'లో', 'నుండి']
        
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in location_indicators and i + 1 < len(words):
                return words[i + 1].strip('.,!?')
        
        return None
    
    @staticmethod
    def extract_crop(text: str) -> Optional[str]:
        """Extract crop name from text query"""
        common_crops = [
            'rice', 'wheat', 'cotton', 'sugarcane', 'maize', 'potato',
            'tomato', 'onion', 'garlic', 'chili', 'turmeric',
            'धान', 'गेहूं', 'कपास', 'गन्ना', 'मक्का', 'आलू',
            'వరి', 'గోధుమ', 'పత్తి', 'మొక్కజొన్న', 'బంగాళాదుంప'
        ]
        
        text_lower = text.lower()
        for crop in common_crops:
            if crop in text_lower:
                return crop
        
        return None

class ErrorHandler:
    """Handle and log errors gracefully"""
    
    @staticmethod
    def handle_api_error(error: Exception, api_name: str) -> Dict:
        """Handle API errors and return user-friendly message"""
        logger.error(f"{api_name} API error: {error}")
        return {
            "error": f"Unable to fetch data from {api_name}. Please try again later.",
            "technical_error": str(error)
        }
    
    @staticmethod
    def handle_processing_error(error: Exception, context: str) -> str:
        """Handle processing errors"""
        logger.error(f"Processing error in {context}: {error}")
        return "I'm sorry, I encountered an error while processing your request. Please try rephrasing your question."

class ResponseFormatter:
    """Format responses for different platforms"""
    
    @staticmethod
    def format_for_telegram(text: str) -> str:
        """Format text for Telegram (Markdown)"""
        # Add basic Markdown formatting
        text = text.replace("**", "*")  # Bold
        text = text.replace("##", "")   # Remove headers
        return text
    
    @staticmethod
    def format_for_web(text: str) -> str:
        """Format text for web interface (HTML)"""
        # Basic HTML formatting
        text = text.replace("\n", "<br>")
        text = text.replace("**", "<strong>").replace("**", "</strong>")
        return text
    
    @staticmethod
    def truncate_response(text: str, max_length: int = 4000) -> str:
        """Truncate response if too long"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length-50]
        return truncated + "\n\n[Response truncated - please ask for specific details]"

# Initialize global utilities
cache_manager = CacheManager()
text_processor = TextProcessor()
error_handler = ErrorHandler()
response_formatter = ResponseFormatter()
