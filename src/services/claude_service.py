"""
Claude AI Integration for BhoomiSetu MCP Server
Provides Claude/Anthropic AI capabilities alongside OpenAI
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import anthropic
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeAIService:
    """Claude AI service for agricultural queries"""
    
    def __init__(self):
        """Initialize Claude AI service"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        self.max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', '4000'))
        self.temperature = float(os.getenv('CLAUDE_TEMPERATURE', '0.7'))
        
        if self.api_key:
            try:
                self.client = AsyncAnthropic(api_key=self.api_key)
                logger.info("✅ Claude AI service initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Claude AI: {e}")
                self.client = None
        else:
            logger.warning("⚠️ Claude API key not found")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Claude service is available"""
        return self.client is not None
    
    async def chat_completion(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get chat completion from Claude
        
        Args:
            message: User message
            system_prompt: System prompt for context
            conversation_history: Previous conversation messages
            **kwargs: Additional parameters
            
        Returns:
            Claude response with metadata
        """
        if not self.client:
            raise Exception("Claude AI service not available")
        
        try:
            # Prepare messages
            messages = []
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages
                    role = "user" if msg.get("role") == "user" else "assistant"
                    content = msg.get("content", "")
                    if content:
                        messages.append({"role": role, "content": content})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Prepare system prompt
            if not system_prompt:
                system_prompt = self._get_agricultural_system_prompt()
            
            # Make API call
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )
            
            # Extract response content
            response_text = ""
            if response.content:
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        response_text += content_block.text
            
            return {
                "response": response_text,
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "metadata": {
                    "provider": "anthropic",
                    "model": self.model,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise Exception(f"Claude AI error: {str(e)}")
    
    async def agricultural_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process agricultural query with Claude
        
        Args:
            query: Agricultural question
            context: User context (location, crop, etc.)
            language: Response language
            
        Returns:
            Agricultural advice from Claude
        """
        if not self.client:
            raise Exception("Claude AI service not available")
        
        # Prepare context-aware system prompt
        system_prompt = self._get_agricultural_system_prompt(context, language)
        
        # Enhance query with context
        enhanced_query = self._enhance_query_with_context(query, context)
        
        try:
            response = await self.chat_completion(
                message=enhanced_query,
                system_prompt=system_prompt
            )
            
            # Parse agricultural response
            return {
                "response": response["response"],
                "query_type": self._detect_query_type(query),
                "language": language,
                "confidence": 0.9,  # Claude generally provides high-quality responses
                "sources": ["claude_ai", "agricultural_knowledge"],
                "suggestions": self._generate_follow_up_suggestions(query, context),
                "metadata": {
                    **response["metadata"],
                    "query_context": context,
                    "enhanced_query": enhanced_query != query
                }
            }
            
        except Exception as e:
            logger.error(f"Agricultural query error: {e}")
            raise Exception(f"Failed to process agricultural query: {str(e)}")
    
    async def crop_recommendation(
        self,
        farm_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get crop recommendations using Claude
        
        Args:
            farm_context: Farm conditions and context
            
        Returns:
            Crop recommendations from Claude
        """
        if not self.client:
            raise Exception("Claude AI service not available")
        
        # Prepare crop recommendation prompt
        system_prompt = """You are an expert agricultural advisor specializing in crop recommendations for Indian farmers. 
        Provide specific, actionable crop recommendations based on the given farm conditions. 
        Consider soil type, climate, season, water availability, market demand, and farmer experience.
        
        Format your response as JSON with:
        - recommended_crops: List of crops with details
        - reasons: Why these crops are suitable
        - season_advice: Seasonal guidance
        - estimated_yield: Expected yields
        - investment_required: Cost estimates
        - risk_factors: Potential risks
        - success_tips: Practical tips for success"""
        
        # Create detailed farm description
        farm_description = self._create_farm_description(farm_context)
        
        query = f"""Based on the following farm conditions, recommend the best crops:

{farm_description}

Please provide detailed crop recommendations with reasoning, yield estimates, investment requirements, and practical advice."""
        
        try:
            response = await self.chat_completion(
                message=query,
                system_prompt=system_prompt
            )
            
            # Parse response (Claude should return structured data)
            return {
                "recommendations": response["response"],
                "farm_context": farm_context,
                "metadata": response["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Crop recommendation error: {e}")
            raise Exception(f"Failed to get crop recommendations: {str(e)}")
    
    async def disease_diagnosis(
        self,
        symptoms: List[str],
        crop_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Diagnose plant diseases using Claude
        
        Args:
            symptoms: List of observed symptoms
            crop_type: Type of crop
            context: Additional context
            
        Returns:
            Disease diagnosis and treatment recommendations
        """
        if not self.client:
            raise Exception("Claude AI service not available")
        
        system_prompt = """You are an expert plant pathologist and agricultural advisor. 
        Diagnose plant diseases based on symptoms and provide treatment recommendations.
        Consider the crop type, symptoms, environmental conditions, and regional disease patterns.
        
        Provide structured diagnosis with:
        - Most likely diseases with confidence levels
        - Treatment recommendations (organic and chemical options)
        - Prevention strategies
        - Immediate actions needed
        - When to consult local agricultural experts"""
        
        # Create symptoms description
        symptoms_text = ", ".join(symptoms)
        context_text = ""
        if context:
            if context.get("location"):
                context_text += f"Location: {context['location']}\n"
            if context.get("weather_conditions"):
                context_text += f"Weather: {context['weather_conditions']}\n"
        
        query = f"""Crop: {crop_type}
Observed symptoms: {symptoms_text}
{context_text}

Please diagnose the possible diseases and provide treatment recommendations."""
        
        try:
            response = await self.chat_completion(
                message=query,
                system_prompt=system_prompt
            )
            
            return {
                "diagnosis": response["response"],
                "crop_type": crop_type,
                "symptoms": symptoms,
                "metadata": response["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Disease diagnosis error: {e}")
            raise Exception(f"Failed to diagnose disease: {str(e)}")
    
    def _get_agricultural_system_prompt(
        self, 
        context: Optional[Dict[str, Any]] = None, 
        language: str = "en"
    ) -> str:
        """Generate agricultural system prompt"""
        base_prompt = """You are BhoomiSetu, an expert AI agricultural advisor for Indian farmers. 
        You provide practical, scientifically-accurate advice on farming, crops, irrigation, pest management, 
        weather planning, market prices, and government schemes.
        
        Key guidelines:
        - Focus on Indian agriculture, crops, and farming practices
        - Consider local climate zones, soil types, and seasonal patterns
        - Provide cost-effective solutions for small and medium farmers
        - Include both traditional and modern farming techniques
        - Reference government schemes and support programs when relevant
        - Use simple, clear language that farmers can understand
        - Always prioritize farmer safety and sustainable practices"""
        
        # Add context-specific guidance
        if context:
            if context.get("location"):
                base_prompt += f"\n- Consider regional conditions for {context['location']}"
            if context.get("crop_type"):
                base_prompt += f"\n- Focus on {context['crop_type']} cultivation"
            if context.get("season"):
                base_prompt += f"\n- Current season: {context['season']}"
        
        # Add language instruction
        if language != "en":
            language_names = {
                "hi": "Hindi",
                "te": "Telugu", 
                "ta": "Tamil",
                "kn": "Kannada",
                "ml": "Malayalam",
                "mr": "Marathi",
                "gu": "Gujarati"
            }
            lang_name = language_names.get(language, language)
            base_prompt += f"\n- Respond in {lang_name} language"
        
        return base_prompt
    
    def _enhance_query_with_context(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Enhance query with available context"""
        if not context:
            return query
        
        enhancements = []
        if context.get("location"):
            enhancements.append(f"Location: {context['location']}")
        if context.get("crop_type"):
            enhancements.append(f"Crop: {context['crop_type']}")
        if context.get("season"):
            enhancements.append(f"Season: {context['season']}")
        if context.get("soil_type"):
            enhancements.append(f"Soil: {context['soil_type']}")
        
        if enhancements:
            return f"{query}\n\nContext: {', '.join(enhancements)}"
        
        return query
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of agricultural query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["crop", "plant", "grow", "seed", "variety"]):
            return "crop_selection"
        elif any(word in query_lower for word in ["water", "irrigation", "drought"]):
            return "irrigation"
        elif any(word in query_lower for word in ["disease", "pest", "insect", "fungus"]):
            return "disease_pest"
        elif any(word in query_lower for word in ["weather", "rain", "temperature"]):
            return "weather"
        elif any(word in query_lower for word in ["price", "market", "sell", "profit"]):
            return "market"
        elif any(word in query_lower for word in ["scheme", "loan", "subsidy", "government"]):
            return "government_scheme"
        else:
            return "general"
    
    def _generate_follow_up_suggestions(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate follow-up suggestions based on query"""
        query_type = self._detect_query_type(query)
        
        suggestions = {
            "crop_selection": [
                "What soil testing should I do?",
                "How to prepare the field?",
                "What irrigation method is best?"
            ],
            "irrigation": [
                "How to check soil moisture?",
                "When to reduce watering?",
                "What about drip irrigation?"
            ],
            "disease_pest": [
                "How to prevent this in future?",
                "Are there organic treatments?",
                "When to spray pesticides?"
            ],
            "weather": [
                "How to protect crops from heat?",
                "Should I delay planting?",
                "What about crop insurance?"
            ],
            "market": [
                "Where to get better prices?",
                "How to store crops properly?",
                "What about value addition?"
            ],
            "government_scheme": [
                "How to apply for this scheme?",
                "What documents are needed?",
                "Are there other benefits?"
            ]
        }
        
        return suggestions.get(query_type, [
            "Tell me about soil preparation",
            "What crops are profitable now?",
            "How to improve crop yield?"
        ])
    
    def _create_farm_description(self, farm_context: Dict[str, Any]) -> str:
        """Create detailed farm description from context"""
        description_parts = []
        
        if farm_context.get("soil_type"):
            description_parts.append(f"Soil Type: {farm_context['soil_type']}")
        
        if farm_context.get("climate_zone"):
            description_parts.append(f"Climate: {farm_context['climate_zone']}")
        
        if farm_context.get("season"):
            description_parts.append(f"Season: {farm_context['season']}")
        
        if farm_context.get("farm_size"):
            description_parts.append(f"Farm Size: {farm_context['farm_size']} acres")
        
        if farm_context.get("irrigation_type"):
            description_parts.append(f"Irrigation: {farm_context['irrigation_type']}")
        
        if farm_context.get("location"):
            description_parts.append(f"Location: {farm_context['location']}")
        
        if farm_context.get("budget"):
            description_parts.append(f"Budget: ₹{farm_context['budget']}")
        
        if farm_context.get("experience_level"):
            description_parts.append(f"Farmer Experience: {farm_context['experience_level']}")
        
        return "\n".join(description_parts) if description_parts else "No specific farm details provided"


# Global Claude service instance
claude_service = ClaudeAIService()
