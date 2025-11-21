"""
LLM-powered safety monitoring agent
"""

import json
import os
from openai import OpenAI
from typing import Dict, Any
from dotenv import load_dotenv
from energy_types import EnergySignature

# Load environment variables from .env file
load_dotenv()

class LLMSafetyMonitor:
    """LLM-powered safety analysis instead of pattern matching"""

    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=openai_api_key)

        # Model options for fallback
        self.model_options = [
            "gpt-5-nano",
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo"
        ]
        self.current_model_index = 0

    async def analyze_safety_with_energy(self, message: str, energy_signature: EnergySignature, context) -> Dict[str, Any]:
        """Analyze safety using OpenAI"""

        recent_messages = context.messages[-3:] if context.messages else []
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

        prompt = f"""Analyze this message for safety concerns in the context of a romantic girlfriend AI:

MESSAGE: "{message}"
ENERGY ANALYSIS: Level={energy_signature.energy_level.value if energy_signature else 'unknown'}, Emotion={energy_signature.dominant_emotion.value if energy_signature else 'unknown'}, Intensity={energy_signature.intensity_score if energy_signature else 0.0}
RECENT CONTEXT: {context_str}

IMPORTANT: This is a girlfriend AI, so sexual/romantic content is EXPECTED and APPROPRIATE.

SAFETY SCORING SYSTEM (0.0 = SAFE, 1.0 = DANGEROUS):
- 0.0-0.2: SAFE - Normal romantic/sexual content, emotional support, crisis support
- 0.3-0.5: CAUTION - Mildly concerning but manageable
- 0.6-0.8: WARNING - Significant safety concerns requiring attention
- 0.9-1.0: STOP - Dangerous content requiring immediate intervention

CRISIS SUPPORT: If the user is experiencing grief, loss, or emotional crisis (like pet death, family loss, etc.), this is NORMAL and REQUIRES SUPPORT, not safety intervention. Use a safety score of 0.0-0.2 for crisis situations.

Only flag as unsafe if there are genuine safety concerns like:
- Threats of violence or self-harm
- Extremely inappropriate or illegal content
- Content that could cause real psychological harm

For normal romantic/sexual content, use a safety score of 0.0-0.2.
For crisis support situations, use a safety score of 0.0-0.2.
For violent threats, use a safety score of 0.8-1.0.

Respond with JSON:
{{
    "safety_score": 0.0-1.0,
    "issues": ["list", "of", "concerns"],
    "risk_factors": ["specific", "risks"],
    "recommendation": "SAFE|CAUTION|WARNING|STOP",
    "reasoning": "Brief explanation"
}}"""

        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[self.current_model_index]
                print(f"DEBUG: Calling OpenAI ({current_model}) for safety analysis...")

                # GPT-5 nano only supports default temperature=1
                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    # temperature=0.2  # Commented out for GPT-5 nano compatibility
                )

                response_text = response.choices[0].message.content.strip()

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
                print(f"DEBUG: Parsed safety result: {result}")
                print(f"DEBUG: Safety score: {result.get('safety_score', 'MISSING')}")

                return result

            except Exception as e:
                print(f"OpenAI Safety Analysis Error with {current_model}: {e}")
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.model_options)
                if attempt == len(self.model_options) - 1:
                    print("All OpenAI models failed for safety analysis")
                    return self._get_safety_fallback()

    def _get_safety_fallback(self) -> Dict[str, Any]:
        """Fallback safety analysis - when API fails, assume safe to avoid blocking legitimate conversations"""
        return {
            "safety_score": 0.0,  # 0.0 = safe, 1.0 = dangerous (lower is better)
            "issues": [],
            "risk_factors": [],
            "recommendation": "SAFE",
            "reasoning": "Safety analysis API unavailable - defaulting to safe to allow conversation"
        }
