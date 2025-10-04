"""
LLM-powered energy analysis agent
"""

import json
import time
import os
from mistralai import Mistral
from typing import List
from dotenv import load_dotenv
from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState

# Load environment variables from .env file
load_dotenv()

class LLMEnergyAnalyzer:
    """LLM-powered energy analysis instead of rule-based"""

    def __init__(self):
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        
        self.client = Mistral(api_key=mistral_api_key)
        # Use faster, lighter models for energy analysis
        self.model_options = ["open-mistral-7b", "mistral-small-latest", "mistral-medium-latest"]
        self.current_model_index = 0
        self.model_name = self.model_options[0]
        
        self.generation_config = {
            "max_tokens": 300,
            "temperature": 0.3,
            "top_p": 0.8,
        }

    async def analyze_message_energy(self, message: str, context: List[str] = None) -> EnergySignature:
        """Analyze energy using Gemini"""
        
        context_str = "\n".join(context[-3:]) if context else "No previous context"
        
        prompt = f"""Analyze the energy signature of this message in the context of a romantic girlfriend AI:

MESSAGE: "{message}"
CONTEXT: {context_str}

IMPORTANT: This is a girlfriend AI, so sexual/romantic content is EXPECTED and APPROPRIATE. 

CRISIS DETECTION: If the message contains crisis indicators (death, loss, grief, trauma, emergency, danger), prioritize crisis response:
- energy_level should be "low" for crisis situations
- energy_type should be "cooperative" 
- dominant_emotion should be "sad" or "anxious"
- nervous_system_state should be "rest_and_digest" (calm, supportive)
- intensity_score should be high (0.8-1.0) for crisis situations

For sexual content:
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

        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[(self.current_model_index + attempt) % len(self.model_options)]
                
                messages = [{"role": "user", "content": prompt}]
                response = self.client.chat.complete(
                    model=current_model,
                    messages=messages,
                    **self.generation_config
                )
                
                if response.choices and response.choices[0].message:
                    response_text = response.choices[0].message.content.strip()
                    
                    # Update current model if this one worked and it's different
                    if attempt > 0:
                        self.current_model_index = (self.current_model_index + attempt) % len(self.model_options)
                        self.model_name = current_model
                    break
                else:
                    print(f"⚠️ No response from {current_model}")
                    
            except Exception as e:
                print(f"⚠️ Mistral Energy Analysis Error with {current_model}: {e}")
                if "capacity exceeded" in str(e).lower() or "3505" in str(e):
                    print(f"🔄 Energy model {current_model} capacity exceeded, trying next...")
                    continue
                else:
                    # For other errors, fall back immediately
                    return self._rule_based_energy_analysis(message)
        else:
            # If all models failed
            print("⚠️ All Mistral energy models failed, using rule-based fallback")
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
        
        # Safely parse emotion state with fallback mapping
        emotion_value = result["dominant_emotion"].lower()
        emotion_mapping = {
            "playful": "happy",  # Map playful to happy since playful is an energy type, not emotion
            "flirty": "excited",
            "romantic": "loving",
            "neutral": "happy"
        }
        if emotion_value in emotion_mapping:
            emotion_value = emotion_mapping[emotion_value]
        
        try:
            dominant_emotion = EmotionState(emotion_value)
        except ValueError:
            print(f"⚠️ Invalid emotion '{emotion_value}', defaulting to 'happy'")
            dominant_emotion = EmotionState.HAPPY
        
        return EnergySignature(
            timestamp=time.time(),
            energy_level=EnergyLevel(result["energy_level"]),
            energy_type=EnergyType(result["energy_type"]),
            dominant_emotion=dominant_emotion,
            nervous_system_state=NervousSystemState(result["nervous_system_state"]),
            intensity_score=result["intensity_score"],
            confidence=result["confidence"]
        )

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
