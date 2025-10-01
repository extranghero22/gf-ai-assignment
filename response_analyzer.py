"""
LLM-powered response analysis agent
"""

import json
import os
import google.generativeai as genai
from typing import Dict, Any
from energy_types import EnergySignature
from utils import get_available_gemini_model

class LLMResponseAnalyzer:
    """LLM-powered response analysis instead of pattern matching"""

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
            safety_settings=safety_settings
        )

    async def analyze_response_energy(self, user_input: str, energy_signature: EnergySignature, context) -> Dict[str, Any]:
        """Analyze if conversation should continue using Gemini"""
        
        recent_messages = context.messages[-5:] if context.messages else []
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        prompt = f"""Analyze if this conversation should continue:

USER MESSAGE: "{user_input}"
ENERGY: Level={energy_signature.energy_level.value}, Emotion={energy_signature.dominant_emotion.value}, Intensity={energy_signature.intensity_score}
CONVERSATION CONTEXT: {context_str}

IMPORTANT: Only recommend stopping the conversation for serious issues like:
- The agent's response is completely inappropriate or harmful
- The agent is being abusive or threatening
- The conversation has become completely incoherent
- There are major safety concerns

Do NOT stop for minor conversational issues like:
- Small assumptions about emotional state
- Slightly awkward phrasing
- Minor misunderstandings
- Normal conversational flow

Respond with JSON:
{{
    "should_continue": true/false,
    "confidence": 0.0-1.0,
    "reason": "explanation",
    "energy_compatibility": 0.0-1.0,
    "engagement_level": "low|medium|high"
}}"""

        try:
            print(f"🔍 DEBUG: Calling Gemini for response analysis...")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            print(f"🔍 DEBUG: Response analysis: '{response_text}'")
            
            if not response_text:
                print("⚠️ Empty response analysis, using fallback")
                return self._get_response_fallback()
            
            # Try to extract JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    print(f"⚠️ No valid JSON in response analysis: '{response_text}'")
                    return self._get_response_fallback()
            
            return result
            
        except Exception as e:
            print(f"Gemini Response Analysis Error: {e}")
            return self._get_response_fallback()

    def _get_response_fallback(self) -> Dict[str, Any]:
        """Fallback response analysis"""
        return {
            "should_continue": True,
            "confidence": 0.5,
            "reason": "Analysis failed, defaulting to continue",
            "energy_compatibility": 0.5,
            "engagement_level": "medium"
        }
