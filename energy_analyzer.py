"""
LLM-powered energy analysis agent
"""

import json
import time
import os
import google.generativeai as genai
from typing import List
from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
from utils import get_available_gemini_model

class LLMEnergyAnalyzer:
    """LLM-powered energy analysis instead of rule-based"""

    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        model_name = get_available_gemini_model()
        print(f"Using Gemini model: {model_name}")
        
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
                "max_output_tokens": 500,  # Limit response length for faster generation
                "temperature": 0.3,  # Lower temperature for more consistent analysis
                "top_p": 0.8,
                "top_k": 20
            }
        )

    async def analyze_message_energy(self, message: str, context: List[str] = None) -> EnergySignature:
        """Analyze energy using Gemini"""
        
        context_str = "\n".join(context[-3:]) if context else "No previous context"
        
        prompt = f"""Analyze the energy signature of this message in the context of a romantic girlfriend AI:

MESSAGE: "{message}"
CONTEXT: {context_str}

IMPORTANT: This is a girlfriend AI, so sexual/romantic content is EXPECTED and APPROPRIATE. For sexual content:
- energy_type should be "intimate" 
- nervous_system_state should be "rest_and_digest"
- dominant_emotion should be "loving" or "excited"
- energy_level can be "high" or "intense" for sexual content

Respond with a JSON object containing:
{{
    "energy_level": "none|low|medium|high|intense",
    "energy_type": "combative|cooperative|neutral|playful|intimate", 
    "dominant_emotion": "happy|sad|angry|anxious|jealous|loving|excited|bored|confused|grateful",
    "nervous_system_state": "rest_and_digest|fight|flight|freeze|fawn",
    "intensity_score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of analysis"
}}"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if not response_text:
                print("⚠️ Empty response from Gemini, using fallback")
                return self._rule_based_energy_analysis(message)
            
            # Try to extract JSON from response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    print(f"⚠️ No valid JSON found in response: '{response_text}'")
                    return self._rule_based_energy_analysis(message)
            
            return EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel(result["energy_level"]),
                energy_type=EnergyType(result["energy_type"]),
                dominant_emotion=EmotionState(result["dominant_emotion"]),
                nervous_system_state=NervousSystemState(result["nervous_system_state"]),
                intensity_score=result["intensity_score"],
                confidence=result["confidence"]
            )
            
        except Exception as e:
            print(f"Gemini Energy Analysis Error: {e}")
            return self._rule_based_energy_analysis(message)

    def _rule_based_energy_analysis(self, message: str) -> EnergySignature:
        """Simple rule-based energy analysis as fallback"""
        message_lower = message.lower().strip()
        
        # Sexual/romantic content - should be intimate, not combative
        sexual_keywords = ["breast", "boob", "tits", "ass", "pussy", "cock", "dick", "fuck", "sex", "fuck", "horny", "aroused", "touch", "feel", "kiss", "lick", "suck"]
        if any(word in message_lower for word in sexual_keywords):
            return EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel.HIGH,
                energy_type=EnergyType.INTIMATE,
                dominant_emotion=EmotionState.LOVING,
                nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                intensity_score=0.8,
                confidence=0.9
            )
        
        # Simple greetings - should be positive and welcoming
        if message_lower in ["hi", "hello", "hey", "hiya", "howdy"]:
            return EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel.MEDIUM,
                energy_type=EnergyType.COOPERATIVE,
                dominant_emotion=EmotionState.HAPPY,
                nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                intensity_score=0.4,
                confidence=0.9
            )
        
        # Crisis detection
        if any(word in message_lower for word in ["died", "death", "dead", "crisis", "emergency", "sad", "down"]):
            return EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel.LOW,
                energy_type=EnergyType.COOPERATIVE,
                dominant_emotion=EmotionState.SAD,
                nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                intensity_score=0.8,
                confidence=0.9
            )
        
        # Intimate terms
        if any(word in message_lower for word in ["babe", "baby", "love", "honey"]):
            return EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel.MEDIUM,
                energy_type=EnergyType.INTIMATE,
                dominant_emotion=EmotionState.LOVING,
                nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                intensity_score=0.6,
                confidence=0.8
            )
        
        # Default
        return EnergySignature(
            timestamp=time.time(),
            energy_level=EnergyLevel.MEDIUM,
            energy_type=EnergyType.NEUTRAL,
            dominant_emotion=EmotionState.HAPPY,
            nervous_system_state=NervousSystemState.REST_AND_DIGEST,
            intensity_score=0.5,
            confidence=0.5
        )
