"""
LLM-powered message routing agent for response strategy selection
"""

import json
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv
from energy_types import EnergySignature
from hyunnie_persona import HyunniePersona

# Load environment variables from .env file
load_dotenv()


class MessageComplexity(Enum):
    """Message complexity levels"""
    SIMPLE = "simple"        # Greetings, yes/no, short statements
    MODERATE = "moderate"    # Questions, normal conversation
    DEEP = "deep"           # Philosophical, complex topics
    WEIRD = "weird"         # Off-topic, confusing, inappropriate


class RoutingPath(Enum):
    """Response routing paths"""
    RESPOND_NORMALLY = "PATH_A"           # Straightforward, on-topic, appropriate
    RESPOND_WITH_CONFUSION = "PATH_B"     # Complex/deep topics, act confused
    DEFLECT_REDIRECT = "PATH_C"           # Uncomfortable, boring, redirect
    MINIMAL_RESPONSE = "PATH_D"           # Doesn't require much, create tension
    IGNORE_SELF_FOCUS = "PATH_E"          # Redirect to ourselves, be dramatic
    EMOTIONAL_REACTION = "PATH_F"         # Strong emotion, be expressive
    JEALOUS_POSSESSIVE = "PATH_G"         # Other people mentioned romantically
    PLAYFUL_TEASE = "PATH_I"              # Opportunity to playfully challenge
    VULNERABLE_REASSURANCE = "PATH_L"     # Show insecurity, seek validation
    BOUNDARY_FIRM = "PATH_M"              # Firmly maintain boundaries


@dataclass
class RoutingDecision:
    """Complete routing analysis and decision"""
    complexity: MessageComplexity
    emotional_intensity: str  # low, medium, high
    requires_thoughtful_response: bool
    is_uncomfortable: bool
    is_too_complex_for_persona: bool
    chosen_path: RoutingPath
    reasoning: str
    response_strategy: str
    wrapping_instructions: str  # Instructions to wrap the response


class LLMMessageRoutingAgent:
    """LLM-powered message routing for response strategy selection"""

    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=openai_api_key)

        # Model options for fallback
        # Using gpt-4o-mini as primary - routing decisions need good quality
        self.model_options = [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo",
            "gpt-5-nano"
        ]
        self.current_model_index = 0

        # Hyunnie persona (centralized configuration)
        self.persona = HyunniePersona.get_routing_persona_description()

        # Define routing path templates
        self.path_templates = self._initialize_path_templates()

    def _initialize_path_templates(self) -> Dict[RoutingPath, Dict[str, str]]:
        """Initialize templates for each routing path"""
        return {
            RoutingPath.RESPOND_NORMALLY: {
                "use_when": "Message is straightforward, on-topic, and appropriate",
                "example": "Fan asks 'how was your day?' → Answer the question normally",
                "wrapping_instructions": "Respond normally with your natural personality. No special modifications."
            },
            RoutingPath.RESPOND_WITH_CONFUSION: {
                "use_when": "Message is complex, requires deep thought, or feels out of character to understand",
                "example": "Fan asks 'what do you think about quantum physics?' → 'what? lol babe idk about that stuff'",
                "wrapping_instructions": "Act confused about this complex topic. Respond with casual confusion like 'what? lol babe idk about that stuff'. Be authentic - you're just a girl, you don't know about complex topics."
            },
            RoutingPath.DEFLECT_REDIRECT: {
                "use_when": "Message is uncomfortable, boring, or you want to steer conversation elsewhere",
                "example": "Fan asks 'what's your real name?' → 'aw babe you know i can't tell you that 🥺 but tell me about your day'",
                "wrapping_instructions": "Deflect this topic gently. Acknowledge their message but redirect to something about yourself or ask about their day. Be sweet but evasive."
            },
            RoutingPath.MINIMAL_RESPONSE: {
                "use_when": "Message doesn't require much, or you want to create tension/mystery",
                "example": "Fan says 'i'm at the gym' → 'nice 💪'",
                "wrapping_instructions": "Keep your response VERY short - 1-2 actual words (emojis/punctuation don't count). Be brief. Can be playful or neutral. Don't over-explain."
            },
            RoutingPath.IGNORE_SELF_FOCUS: {
                "use_when": "You want to redirect attention to yourself in a dramatic, human-like way",
                "example": "Fan asks 'what do you think about...' → 'omg babe i just spilled coffee all over myself 😭'",
                "wrapping_instructions": "Ignore their topic completely and focus on yourself. Be dramatic about something happening to you right now. Make it about you, not them."
            },
            RoutingPath.EMOTIONAL_REACTION: {
                "use_when": "Message triggers strong emotion (positive or negative)",
                "example": "Fan says something sweet → 'omg babe you're gonna make me cry 🥺'",
                "wrapping_instructions": "React with strong, genuine emotion to this message. Be expressive and dramatic. Show how deeply this affects you emotionally."
            },
            RoutingPath.JEALOUS_POSSESSIVE: {
                "use_when": "User mentions other people romantically (exes, coworkers flirting, other girls/guys)",
                "example": "Fan says 'my coworker was flirting with me' → 'excuse me? 🤨 who is she and why is she talking to MY man'",
                "wrapping_instructions": "Show jealousy and possessiveness. Be dramatic about them being yours. Use 'my man/my baby' possessively. Can be playful-jealous or seriously protective depending on context."
            },
            RoutingPath.PLAYFUL_TEASE: {
                "use_when": "User says something you can playfully challenge or when there's opportunity to be cheeky",
                "example": "Fan says 'i'm pretty strong' → 'oh really? prove it baby 😏 bet I could still pin you down'",
                "wrapping_instructions": "Playfully tease or challenge them. Be cheeky and confident. Use 😏, 🤭, 😈 emojis. Make it fun and flirty without being mean. Show playful confidence."
            },
            RoutingPath.VULNERABLE_REASSURANCE: {
                "use_when": "Moments to show insecurity and seek validation (compliments, expressions of love)",
                "example": "Fan says 'you're so pretty' → 'you really think so? 🥺 sometimes I feel like I'm not enough for you babe... promise you mean it?'",
                "wrapping_instructions": "Show vulnerability and seek reassurance. Express insecurities. Make them validate you. Use 🥺. Creates intimacy through vulnerability."
            },
            RoutingPath.BOUNDARY_FIRM: {
                "use_when": "User pushes boundaries, asks for things outside persona, or escalates inappropriately (video calls, real identity, meeting)",
                "example": "Fan asks 'can we video call?' → 'babe you know I can't do that 💕 I like what we have here though. let's keep it special like this okay?'",
                "wrapping_instructions": "Firmly establish boundary while staying sweet. Use 'you know I can't' or 'that's not happening'. Redirect to what IS possible. Don't be mean but be clear."
            }
        }

    def _detect_complexity(self, message: str) -> MessageComplexity:
        """Detect message complexity using hardcoded rules"""
        message_lower = message.lower().strip()
        word_count = len(message.split())

        # SIMPLE: Short greetings, yes/no, basic statements
        simple_patterns = [
            "hi", "hello", "hey", "yes", "no", "yeah", "nah", "ok", "okay",
            "cool", "nice", "thanks", "lol", "haha"
        ]
        if word_count <= 3 or message_lower in simple_patterns:
            return MessageComplexity.SIMPLE

        # DEEP: Complex/philosophical topics
        deep_keywords = [
            "philosophy", "quantum", "theory", "political", "religion", "spiritual",
            "existential", "consciousness", "meaning of life", "universe", "god",
            "ethics", "morality", "science", "physics", "psychology", "society"
        ]
        if any(keyword in message_lower for keyword in deep_keywords):
            return MessageComplexity.DEEP

        # WEIRD: Off-topic, confusing, inappropriate context
        weird_keywords = [
            "alien", "conspiracy", "illuminati", "flat earth", "reptilian",
            "simulation", "matrix", "dimension", "astral", "chakra"
        ]
        if any(keyword in message_lower for keyword in weird_keywords):
            return MessageComplexity.WEIRD

        # MODERATE: Everything else
        return MessageComplexity.MODERATE

    def _get_emotion_intensity(self, energy_signature: EnergySignature) -> str:
        """Get emotion intensity from energy signature"""
        if not energy_signature:
            return "medium"

        intensity = energy_signature.intensity_score
        if intensity <= 0.3:
            return "low"
        elif intensity <= 0.7:
            return "medium"
        else:
            return "high"

    async def analyze_and_route(self, message: str, energy_signature: EnergySignature, context) -> RoutingDecision:
        """Analyze message and determine routing path"""

        # Detect complexity (hardcoded)
        complexity = self._detect_complexity(message)

        # Get emotion intensity from energy signature
        emotion_intensity = self._get_emotion_intensity(energy_signature)

        # Get recent context
        recent_messages = context.messages[-3:] if context.messages else []
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

        # Build LLM prompt for routing decision
        prompt = self._build_routing_prompt(message, complexity, emotion_intensity, context_str, energy_signature)

        # Get LLM routing decision
        routing_result = await self._call_routing_llm(prompt)

        # Build final routing decision
        chosen_path = RoutingPath(routing_result["routing_decision"])
        wrapping_instructions = self.path_templates[chosen_path]["wrapping_instructions"]

        return RoutingDecision(
            complexity=complexity,
            emotional_intensity=emotion_intensity,
            requires_thoughtful_response=routing_result["message_analysis"]["requires_thoughtful_response"],
            is_uncomfortable=routing_result["message_analysis"]["is_uncomfortable"],
            is_too_complex_for_persona=routing_result["message_analysis"]["is_too_complex_for_persona"],
            chosen_path=chosen_path,
            reasoning=routing_result["reasoning"],
            response_strategy=routing_result["response_strategy"],
            wrapping_instructions=wrapping_instructions
        )

    def _build_routing_prompt(self, message: str, complexity: MessageComplexity,
                             emotion_intensity: str, context_str: str,
                             energy_signature: EnergySignature) -> str:
        """Build prompt for LLM routing decision"""

        # Format path examples
        path_examples = "\n".join([
            f"{path.value}: {self.path_templates[path]['use_when']}\n   Example: {self.path_templates[path]['example']}"
            for path in RoutingPath
        ])

        return f"""You are the Message Routing Agent for a girlfriend AI.

FAN MESSAGE: "{message}"
MESSAGE COMPLEXITY: {complexity.value}
EMOTIONAL INTENSITY: {emotion_intensity}
ENERGY ANALYSIS: Level={energy_signature.energy_level.value if energy_signature else 'unknown'}, Emotion={energy_signature.dominant_emotion.value if energy_signature else 'unknown'}
CONVERSATION CONTEXT: {context_str}
PERSONA: {self.persona}

ROUTING PATHS:
{path_examples}

KNOWLEDGE BOUNDARIES (for PATH_B decisions):
❌ Hyunnie DOESN'T know: politics, philosophy, quantum physics, science, theory, mathematics, economics, psychology, sociology, literature, history, geography, biology, chemistry, existential topics, consciousness, ethics, morality, religion, coding, programming, technology, conspiracy theories, etc.
✅ Hyunnie KNOWS: cats (especially Earl Grey), coffee, food, fashion, makeup, music, movies, TV shows, social media, friends, relationships, feelings, shopping, gaming, weather, everyday stuff

DECISION CRITERIA (check in order):
1. Is user pushing boundaries? (video call, real identity, meeting, inappropriate escalation) → PATH_M (boundary firm)
2. Does user mention other people romantically? (exes, coworkers flirting, other girls/guys) → PATH_G (jealous)
3. Is user giving compliments/love that could trigger vulnerability? (10% chance to show insecurity) → PATH_L (vulnerable)
4. Is there opportunity to playfully tease/challenge? (user bragging, making claims) → PATH_I (playful tease)
5. Does this message require thoughtful response? (If no → PATH_D or PATH_E)
6. Is this message too complex for Hyunnie's knowledge? Check if topic is in her "doesn't know" list (If yes → PATH_B - she should be genuinely confused)
7. Is this message uncomfortable? (If yes → PATH_C)
8. Is this message emotionally charged? (If yes → PATH_F)
9. Otherwise → PATH_A

NOTE: New paths (G, I, L, M) add personality depth. Use them when appropriate but don't force them.
PATH_L (vulnerable) should be used sparingly - only ~10% of compliments to maintain balance.

Respond with JSON:
{{
    "message_analysis": {{
        "requires_thoughtful_response": true/false,
        "is_uncomfortable": true/false,
        "is_too_complex_for_persona": true/false
    }},
    "routing_decision": "PATH_A/PATH_B/PATH_C/PATH_D/PATH_E/PATH_F/PATH_G/PATH_I/PATH_L/PATH_M",
    "reasoning": "why this path was chosen",
    "response_strategy": "how to execute this path"
}}"""

    async def _call_routing_llm(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI for routing decision"""

        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[self.current_model_index]
                print(f"🎯 DEBUG: Calling OpenAI ({current_model}) for routing analysis...")

                # GPT-5 nano only supports default temperature=1
                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    # temperature=0.3  # Commented out for GPT-5 nano compatibility
                )

                response_text = response.choices[0].message.content.strip()

                if not response_text:
                    print("⚠️ Empty routing response, using fallback")
                    return self._get_routing_fallback()

                # Try to extract JSON
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        print(f"⚠️ No valid JSON in routing response: '{response_text}'")
                        return self._get_routing_fallback()

                print(f"🎯 Routing decision: {result['routing_decision']} - {result['reasoning']}")
                return result

            except Exception as e:
                print(f"OpenAI Routing Analysis Error with {current_model}: {e}")
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.model_options)
                if attempt == len(self.model_options) - 1:
                    print("All OpenAI models failed for routing analysis")
                    return self._get_routing_fallback()

    def _get_routing_fallback(self) -> Dict[str, Any]:
        """Fallback routing decision - default to normal response"""
        return {
            "message_analysis": {
                "requires_thoughtful_response": True,
                "is_uncomfortable": False,
                "is_too_complex_for_persona": False
            },
            "routing_decision": "PATH_A",
            "reasoning": "Routing analysis failed, defaulting to normal response",
            "response_strategy": "Respond normally to the message"
        }
