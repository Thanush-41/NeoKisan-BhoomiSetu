"""
Internationalization (i18n) Configuration and Language Support
Provides multi-language support for the BhoomiSetu web application
"""

import json
import os
from typing import Dict, Optional

class LanguageConfig:
    """Configuration for supported languages"""
    
    # Language codes to full language names mapping
    LANGUAGES = {
        'en': 'English',
        'hi': 'हिंदी (Hindi)',
        'te': 'తెలుగు (Telugu)', 
        'kn': 'ಕನ್ನಡ (Kannada)',
        'gu': 'ગુજરાતી (Gujarati)',
        'pa': 'ਪੰਜਾਬੀ (Punjabi)',
        'ta': 'தமிழ் (Tamil)',
        'ml': 'മലയാളം (Malayalam)',
        'bn': 'বাংলা (Bengali)',
        'mr': 'मराठी (Marathi)',
        'or': 'ଓଡ଼ିଆ (Odia)',
        'as': 'অসমীয়া (Assamese)'
    }
    
    # Default language
    DEFAULT_LANGUAGE = 'en'
    
    # Language to locale mapping
    LOCALES = {
        'en': 'en_US',
        'hi': 'hi_IN',
        'te': 'te_IN',
        'kn': 'kn_IN',
        'gu': 'gu_IN',
        'pa': 'pa_IN',
        'ta': 'ta_IN',
        'ml': 'ml_IN',
        'bn': 'bn_IN',
        'mr': 'mr_IN',
        'or': 'or_IN',
        'as': 'as_IN'
    }

class I18nService:
    """Internationalization service for loading and managing translations"""
    
    def __init__(self):
        self.translations = {}
        self.current_dir = os.path.dirname(__file__)
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        for lang_code in LanguageConfig.LANGUAGES.keys():
            try:
                translation_file = os.path.join(self.current_dir, f"{lang_code}.json")
                if os.path.exists(translation_file):
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                else:
                    # Fallback to English if translation file doesn't exist
                    self.translations[lang_code] = self.translations.get('en', {})
            except Exception as e:
                print(f"Error loading translation for {lang_code}: {e}")
                self.translations[lang_code] = {}
    
    def get_text(self, key: str, language: str = 'en', **kwargs) -> str:
        """
        Get translated text for a given key and language
        
        Args:
            key: Translation key in dot notation (e.g., 'nav.home')
            language: Language code
            **kwargs: Variables for string formatting
        
        Returns:
            Translated text or key if translation not found
        """
        if language not in self.translations:
            language = LanguageConfig.DEFAULT_LANGUAGE
        
        translation_dict = self.translations.get(language, {})
        
        # Navigate through nested keys
        keys = key.split('.')
        value = translation_dict
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Fallback to English if key not found
                if language != 'en':
                    return self.get_text(key, 'en', **kwargs)
                return key  # Return key if not found even in English
        
        # Format with provided kwargs if value is a string
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        
        return value if isinstance(value, str) else key
    
    def get_language_name(self, lang_code: str) -> str:
        """Get the display name for a language code"""
        return LanguageConfig.LANGUAGES.get(lang_code, lang_code)
    
    def get_all_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        return LanguageConfig.LANGUAGES.copy()
    
    def is_supported_language(self, lang_code: str) -> bool:
        """Check if a language code is supported"""
        return lang_code in LanguageConfig.LANGUAGES

# Global instance
i18n_service = I18nService()

def t(key: str, language: str = 'en', **kwargs) -> str:
    """
    Shorthand function for translation
    
    Args:
        key: Translation key
        language: Language code
        **kwargs: Variables for string formatting
    
    Returns:
        Translated text
    """
    return i18n_service.get_text(key, language, **kwargs)
