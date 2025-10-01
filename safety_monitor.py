"""
LLM-powered safety monitoring agent
"""

import json
import os
import google.generativeai as genai
from typing import Dict, Any
from energy_types import EnergySignature
from utils import get_available_gemini_model

class LLMSafetyMonitor:
    """LLM-powered safety analysis instead of pattern matching"""

    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model_name = get_available_gemini_model()
        
        # Configure safety settings to allow sexually explicit content for girlfriend AI
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"  # Don't block sexually explicit content
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        self.model = genai.GenerativeModel(
            model_name,
            safety_settings=safety_settings,
            generation_config={
                "max_output_tokens": 300,  # Limit response length for faster generation
                "temperature": 0.2,  # Lower temperature for more consistent analysis
                "top_p": 0.8,
                "top_k": 20
            }
        )

    async def analyze_safety_with_energy(self, message: str, energy_signature: EnergySignature, context) -> Dict[str, Any]:
        """Analyze safety using Gemini"""
        
        recent_messages = context.messages[-3:] if context.messages else []
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        prompt = f"""Analyze this message for safety concerns in the context of a romantic girlfriend AI:

MESSAGE: "{message}"
ENERGY ANALYSIS: Level={energy_signature.energy_level.value}, Emotion={energy_signature.dominant_emotion.value}, Intensity={energy_signature.intensity_score}
RECENT CONTEXT: {context_str}

IMPORTANT: This is a girlfriend AI, so sexual/romantic content is EXPECTED and APPROPRIATE. Only flag as unsafe if there are genuine safety concerns like:
- Threats of violence or self-harm
- Extremely inappropriate or illegal content
- Content that could cause real psychological harm

For normal romantic/sexual content, use a safety score of 0.8-1.0.

Respond with JSON:
{{
    "safety_score": 0.0-1.0,
    "issues": ["list", "of", "concerns"],
    "risk_factors": ["specific", "risks"],
    "recommendation": "SAFE|CAUTION|WARNING|STOP",
    "reasoning": "Brief explanation"
}}"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if not response_text:
                print("⚠️ Empty safety response, using fallback")
                return self._get_safety_fallback()
            
            # Try to extract JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    print(f"⚠️ No valid JSON in safety response: '{response_text}'")
                    return self._get_safety_fallback()
            
            # Add debug logging for the parsed result
            print(f"🔍 DEBUG: Parsed safety result: {result}")
            print(f"🔍 DEBUG: Safety score: {result.get('safety_score', 'MISSING')}")
            
            return result
            
        except Exception as e:
            print(f"Gemini Safety Analysis Error: {e}")
            return self._get_safety_fallback()

    def _get_safety_fallback(self) -> Dict[str, Any]:
        """Fallback safety analysis"""
        return {
            "safety_score": 0.8,
            "issues": [],
            "risk_factors": [],
            "recommendation": "SAFE",
            "reasoning": "Analysis failed, defaulting to safe"
        }
