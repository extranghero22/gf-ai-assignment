"""
Utility functions for the conversation system
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_available_gemini_model():
    """Get the first available Gemini model"""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        models = genai.list_models()
        
        # Preferred models in order of preference
        preferred_models = [
            'gemini-1.5-pro',
            'gemini-1.5-flash', 
            'gemini-1.0-pro',
            'gemini-pro'
        ]
        
        # Get available model names
        available_models = [model.name for model in models if 'generateContent' in model.supported_generation_methods]
        
        # Find first preferred model that's available
        for model_name in preferred_models:
            if f'models/{model_name}' in available_models:
                return model_name
        
        # Fallback to first available model
        if available_models:
            return available_models[0].replace('models/', '')
        
        raise Exception("No Gemini models available")
        
    except Exception as e:
        print(f"Error getting available models: {e}")
        return 'gemini-1.0-pro'  # Fallback
