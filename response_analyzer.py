"""
LLM-powered response analysis agent
"""

import json
import os
from mistralai import Mistral
from typing import Dict, Any
from energy_types import EnergySignature

class LLMResponseAnalyzer:
    """LLM-powered response analysis instead of pattern matching"""

    def __init__(self):
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set")
        
        self.client = Mistral(api_key=mistral_api_key)
        
        # Model options for fallback
        self.model_options = [
            "open-mistral-7b",
            "mistral-small-latest", 
            "mistral-medium-latest"
        ]
        self.current_model_index = 0

    async def analyze_response_energy(self, user_input: str, energy_signature: EnergySignature, context) -> Dict[str, Any]:
        """Analyze if conversation should continue using Mistral"""
        
        recent_messages = context.messages[-5:] if context.messages else []
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        prompt = f"""Analyze if this conversation should continue:

USER MESSAGE: "{user_input}"
ENERGY: Level={energy_signature.energy_level.value if energy_signature else 'unknown'}, Emotion={energy_signature.dominant_emotion.value if energy_signature else 'unknown'}, Intensity={energy_signature.intensity_score if energy_signature else 0.0}
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

        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[self.current_model_index]
                print(f"🔍 DEBUG: Calling Mistral ({current_model}) for response analysis...")
                
                response = self.client.chat.complete(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                
                response_text = response.choices[0].message.content.strip()
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
                print(f"Mistral Response Analysis Error with {current_model}: {e}")
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.model_options)
                if attempt == len(self.model_options) - 1:
                    print("All Mistral models failed for response analysis")
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
