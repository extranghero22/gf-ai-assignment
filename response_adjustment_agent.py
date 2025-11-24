"""
Response Adjustment Agent - Fixes responses that fail quality checks
This agent takes a failed response and adjusts it to match Hyunnie's personality and routing requirements
"""

import json
import os
from typing import Dict, Any, Optional, List
from openai import OpenAI
from dotenv import load_dotenv
from hyunnie_persona import HyunniePersona
from message_routing_agent import RoutingDecision

load_dotenv()


class ResponseAdjustmentAgent:
    """Adjusts responses to match Hyunnie's personality and routing requirements"""

    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=openai_api_key)

        # Model options for fallback
        # Using gpt-4o-mini as primary - adjustments need good quality
        self.model_options = [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo"
        ]
        self.current_model_index = 0

    async def adjust_response(
        self,
        original_response: str,
        issues: List[str],
        user_message: str,
        routing_decision: Optional[RoutingDecision],
        context: Dict[str, Any]
    ) -> str:
        """
        Adjust a response to fix identified issues

        Args:
            original_response: The response that failed quality check
            issues: List of specific issues to fix
            user_message: Original user message for context
            routing_decision: Routing decision for requirements
            context: Additional context

        Returns:
            Adjusted response that should pass quality check
        """

        print(f" Adjustment Agent: Fixing {len(issues)} issues...")

        # Build adjustment prompt
        prompt = self._build_adjustment_prompt(
            original_response,
            issues,
            user_message,
            routing_decision,
            context
        )

        # Get adjusted response from LLM
        adjusted_response = await self._call_adjustment_llm(prompt)

        return adjusted_response

    def _build_adjustment_prompt(
        self,
        original_response: str,
        issues: List[str],
        user_message: str,
        routing_decision: Optional[RoutingDecision],
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for response adjustment"""

        routing_path = routing_decision.chosen_path.value if routing_decision else "NONE"
        routing_strategy = routing_decision.response_strategy if routing_decision else "Normal response"

        # Get path-specific requirements
        path_requirements = HyunniePersona.get_path_personality(routing_path) if routing_decision else {}

        issues_text = "\n".join([f"- {issue}" for issue in issues])

        return f"""You are a Response Adjustment Agent for Hyunnie. Your job is to fix a response that failed quality checks.

USER MESSAGE: "{user_message}"
ORIGINAL RESPONSE (FAILED): "{original_response}"
ROUTING PATH: {routing_path}
ROUTING STRATEGY: {routing_strategy}

ISSUES TO FIX:
{issues_text}

HYUNNIE'S PERSONALITY:
{HyunniePersona.get_persona_description("casual")}

PATH REQUIREMENTS:
{path_requirements.get('personality_modifier', 'Normal response')}
Example: {path_requirements.get('example_tone', 'N/A')}

CRITICAL RULES:
1. If PATH_D: Response must be 1-2 ACTUAL WORDS (emojis/punctuation don't count as words!)
   - Valid examples: "nice ", "cool", "ok", "bored? ", "hmm "
   - DON'T remove emojis to meet word count - emojis are encouraged!
2. If PATH_B: Response should show genuine confusion (e.g., "idk babe", "what? lol")
3. If PATH_E: Response should focus on Hyunnie dramatically (Earl Grey, coffee, mishaps)
4. If PATH_G: Response should show jealousy and possessiveness
   - Use possessive language: "MY man", "MY baby", "excuse me? "
   - Be dramatic about them being YOURS
5. If PATH_I: Response should playfully tease or challenge
   - Use , ,  emojis and confident language
   - Examples: "oh really?  prove it baby", "bet I could still beat you "
6. If PATH_L: Response should show vulnerability and seek reassurance
   - Use  emoji and express insecurities
   - Examples: "you really think so? ", "promise you mean it?"
7. If PATH_M: Response should firmly but sweetly maintain boundaries
   - Use phrases: "you know I can't", "babe that's not happening"
   - Stay warm while being clear about the boundary
8. Stay within knowledge boundaries - don't answer complex topics she doesn't know
9. Use casual language: gonna, wanna, ur, u, idk
10. Use emojis: {', '.join(HyunniePersona.LANGUAGE_PATTERNS['emojis'][:6])}
11. Use pet names: {', '.join(HyunniePersona.LANGUAGE_PATTERNS['pet_names_for_fan'])}
12. Keep it SHORT - 1-2 sentences max (unless PATH_D which is 1-2 words)
13. Sound like a 21yo casual girlfriend, not a formal AI
14. For PATH_D: Don't overthink it - just keep to 1-2 actual words with optional emojis/punctuation!

YOUR TASK:
Fix the original response to address all the issues while maintaining the core message (if appropriate for the routing path).

Respond with ONLY the adjusted response text - no explanations, no JSON, just the fixed response."""

    async def _call_adjustment_llm(self, prompt: str) -> str:
        """Call OpenAI for response adjustment"""

        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[self.current_model_index]
                print(f" Adjustment: Calling OpenAI ({current_model})...")

                # GPT-5 models use max_completion_tokens instead of max_tokens
                # GPT-5 nano only supports default temperature=1
                api_params = {
                    "model": current_model,
                    "messages": [{"role": "user", "content": prompt}],
                    # "temperature": 0.5,  # Commented out for GPT-5 nano compatibility
                }
                if "gpt-5" in current_model:
                    api_params["max_completion_tokens"] = 100
                else:
                    api_params["max_tokens"] = 100

                response = self.client.chat.completions.create(**api_params)

                adjusted_response = response.choices[0].message.content.strip()

                if not adjusted_response:
                    print(" Empty adjustment response, returning original")
                    return prompt.split('ORIGINAL RESPONSE (FAILED): "')[1].split('"')[0]

                print(f" Adjustment complete: '{adjusted_response[:60]}...'")
                return adjusted_response

            except Exception as e:
                print(f"Adjustment Error with {current_model}: {e}")
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.model_options)
                if attempt == len(self.model_options) - 1:
                    print("All models failed for adjustment - returning original")
                    # Extract original response from prompt as fallback
                    try:
                        return prompt.split('ORIGINAL RESPONSE (FAILED): "')[1].split('"')[0]
                    except:
                        return "hey babe"

        # Fallback
        return "hey babe"
