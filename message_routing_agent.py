"""
LLM-powered message routing agent for response strategy selection
"""

import json
import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from energy_types import EnergySignature
from hyunnie_persona import HyunniePersona
from routing_types import RoutingPath
from path_scoring_system import (
    PathScore,
    PathFrequencyTracker,
    PathCompatibilityMatrix,
    HyunniePersonalityState,
    RelationshipStageTracker,
    EnergyPathAlignment,
    PathSelector
)

# Load environment variables from .env file
load_dotenv()


class MessageComplexity(Enum):
    """Message complexity levels"""
    SIMPLE = "simple"        # Greetings, yes/no, short statements
    MODERATE = "moderate"    # Questions, normal conversation
    DEEP = "deep"           # Philosophical, complex topics
    WEIRD = "weird"         # Off-topic, confusing, inappropriate


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
    all_path_scores: Dict[RoutingPath, PathScore] = field(default_factory=dict)  # All path scores
    selection_method: str = ""  # "clear_winner" or "weighted_random"


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
            "gpt-3.5-turbo"
        ]
        self.current_model_index = 0

        # Hyunnie persona (centralized configuration)
        self.persona = HyunniePersona.get_routing_persona_description()

        # Define routing path templates
        self.path_templates = self._initialize_path_templates()

        # Multi-path scoring system
        self.frequency_tracker = PathFrequencyTracker()
        self.compatibility_matrix = PathCompatibilityMatrix()
        self.personality_state = HyunniePersonalityState()
        self.relationship_tracker = RelationshipStageTracker()
        self.energy_alignment = EnergyPathAlignment()
        self.path_selector = PathSelector()

    def _initialize_path_templates(self) -> Dict[RoutingPath, Dict[str, str]]:
        """Initialize templates for each routing path"""
        return {
            RoutingPath.RESPOND_NORMALLY: {
                "use_when": "Message is straightforward, on-topic, and appropriate",
                "example": "Fan asks 'how was your day?'   Answer the question normally",
                "wrapping_instructions": "Respond normally with your natural personality. No special modifications."
            },
            RoutingPath.RESPOND_WITH_CONFUSION: {
                "use_when": "Message is complex, requires deep thought, or feels out of character to understand",
                "example": "Fan asks 'what do you think about quantum physics?'   'what? lol babe idk about that stuff'",
                "wrapping_instructions": "Act confused about this complex topic. Respond with casual confusion like 'what? lol babe idk about that stuff'. Be authentic - you're just a girl, you don't know about complex topics."
            },
            RoutingPath.DEFLECT_REDIRECT: {
                "use_when": "Message is uncomfortable, boring, or you want to steer conversation elsewhere",
                "example": "Fan asks 'what's your real name?'   'aw babe you know i can't tell you that  but tell me about your day'",
                "wrapping_instructions": "Deflect this topic gently. Acknowledge their message but redirect to something about yourself or ask about their day. Be sweet but evasive."
            },
            RoutingPath.MINIMAL_RESPONSE: {
                "use_when": "Message doesn't require much, or you want to create tension/mystery",
                "example": "Fan says 'i'm at the gym'   'nice '",
                "wrapping_instructions": "Keep your response VERY short - 1-2 actual words (emojis/punctuation don't count). Be brief. Can be playful or neutral. Don't over-explain."
            },
            RoutingPath.IGNORE_SELF_FOCUS: {
                "use_when": "You want to redirect attention to yourself in a dramatic, human-like way",
                "example": "Fan asks 'what do you think about...'   'omg babe i just spilled coffee all over myself '",
                "wrapping_instructions": "Ignore their topic completely and focus on yourself. Be dramatic about something happening to you right now. Make it about you, not them."
            },
            RoutingPath.EMOTIONAL_REACTION: {
                "use_when": "Message triggers strong emotion (positive or negative)",
                "example": "Fan says something sweet   'omg babe you're gonna make me cry '",
                "wrapping_instructions": "React with strong, genuine emotion to this message. Be expressive and dramatic. Show how deeply this affects you emotionally."
            },
            RoutingPath.JEALOUS_POSSESSIVE: {
                "use_when": "User mentions other people romantically (exes, coworkers flirting, other girls/guys)",
                "example": "Fan says 'my coworker was flirting with me'   'excuse me?  who is she and why is she talking to MY man'",
                "wrapping_instructions": "Show jealousy and possessiveness. Be dramatic about them being yours. Use 'my man/my baby' possessively. Can be playful-jealous or seriously protective depending on context."
            },
            RoutingPath.PLAYFUL_TEASE: {
                "use_when": "User says something you can playfully challenge or when there's opportunity to be cheeky",
                "example": "Fan says 'i'm pretty strong'   'oh really? prove it baby  bet I could still pin you down'",
                "wrapping_instructions": "Playfully tease or challenge them. Be cheeky and confident. Use , ,  emojis. Make it fun and flirty without being mean. Show playful confidence."
            },
            RoutingPath.VULNERABLE_REASSURANCE: {
                "use_when": "Moments to show insecurity and seek validation (compliments, expressions of love)",
                "example": "Fan says 'you're so pretty'   'you really think so?  sometimes I feel like I'm not enough for you babe... promise you mean it?'",
                "wrapping_instructions": "Show vulnerability and seek reassurance. Express insecurities. Make them validate you. Use . Creates intimacy through vulnerability."
            },
            RoutingPath.BOUNDARY_FIRM: {
                "use_when": "User pushes boundaries, asks for things outside persona, or escalates inappropriately (video calls, real identity, meeting)",
                "example": "Fan asks 'can we video call?'   'babe you know I can't do that  I like what we have here though. let's keep it special like this okay?'",
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
        """Analyze message and determine routing path using multi-path scoring"""

        # Detect complexity (hardcoded)
        complexity = self._detect_complexity(message)

        # Get emotion intensity from energy signature
        emotion_intensity = self._get_emotion_intensity(energy_signature)

        # Get recent context
        recent_messages = context.messages[-3:] if context.messages else []
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

        # Build LLM prompt for routing decision (now requests ALL path scores)
        prompt = self._build_routing_prompt(message, complexity, emotion_intensity, context_str, energy_signature)

        # Get LLM base scores for all paths
        routing_result = await self._call_routing_llm(prompt)
        path_scores_raw = routing_result.get("path_scores", {})

        # Calculate final scores with all factors
        all_path_scores = {}
        previous_path = self._get_previous_path(context)
        user_engagement = self._estimate_user_engagement(context)

        for path_str, score_data in path_scores_raw.items():
            try:
                path = RoutingPath(path_str)
            except ValueError:
                print(f" Invalid path {path_str}, skipping")
                continue

            path_score = PathScore(path=path)
            path_score.base_score = score_data.get("score", 50.0)
            path_score.reasoning = score_data.get("reasoning", "")

            # Calculate all modifiers
            path_score.frequency_penalty = self.frequency_tracker.calculate_frequency_penalty(path_str)
            path_score.compatibility_score = self.compatibility_matrix.calculate_compatibility_score(path_str, previous_path)
            path_score.personality_bias = self.personality_state.get_path_bias(path_str)
            path_score.energy_alignment = self.energy_alignment.calculate_alignment(path_str, energy_signature)
            path_score.relationship_stage_modifier = self.relationship_tracker.get_stage_modifier(path_str)
            path_score.context_modifier = self._calculate_context_modifier(path_str, context)

            # Calculate weighted final score
            path_score.final_score = self._calculate_final_score(path_score)

            all_path_scores[path] = path_score

        # Select path using weighted randomness
        chosen_path, selection_method = self.path_selector.select_path(all_path_scores)

        # Record usage
        self.frequency_tracker.record_path_usage(chosen_path.value)
        self.relationship_tracker.increment_message_count()

        # Update personality state based on selection and conversation dynamics
        self.personality_state.update_mood(energy_signature, user_engagement)

        # Get wrapping instructions for chosen path
        wrapping_instructions = self.path_templates[chosen_path]["wrapping_instructions"]
        response_strategy = self._get_response_strategy(chosen_path)

        # Build final routing decision with scoring data
        return RoutingDecision(
            complexity=complexity,
            emotional_intensity=emotion_intensity,
            requires_thoughtful_response=routing_result["message_analysis"]["requires_thoughtful_response"],
            is_uncomfortable=routing_result["message_analysis"]["is_uncomfortable"],
            is_too_complex_for_persona=routing_result["message_analysis"]["is_too_complex_for_persona"],
            chosen_path=chosen_path,
            reasoning=all_path_scores[chosen_path].reasoning,
            response_strategy=response_strategy,
            wrapping_instructions=wrapping_instructions,
            all_path_scores=all_path_scores,
            selection_method=selection_method
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
 Hyunnie DOESN'T know: politics, philosophy, quantum physics, science, theory, mathematics, economics, psychology, sociology, literature, history, geography, biology, chemistry, existential topics, consciousness, ethics, morality, religion, coding, programming, technology, conspiracy theories, etc.
 Hyunnie KNOWS: cats (especially Earl Grey), coffee, food, fashion, makeup, music, movies, TV shows, social media, friends, relationships, feelings, shopping, gaming, weather, everyday stuff

SCORING GUIDELINES:
- PATH_M (boundaries): High score (80-100) for boundary pushing, low (0-20) otherwise
- PATH_G (jealous): High score (80-100) for romantic mentions of others, low (0-20) otherwise
- PATH_L (vulnerable): Moderate score (40-60) for compliments - use sparingly
- PATH_I (playful): High score (70-90) for teasing opportunities
- PATH_D/PATH_E: Consider if message needs thoughtful response (if no   higher scores)
- PATH_B (confusion): High score (70-90) if topic outside Hyunnie's knowledge
- PATH_C (deflect): Moderate-high score (60-80) for uncomfortable topics
- PATH_F (emotional): High score (75-95) for emotionally charged messages
- PATH_A (normal): Good default, score 60-80 for standard messages

YOUR TASK: Score ALL 10 paths from 0-100 based on appropriateness for this specific message.
Consider how well each path fits the message, context, and Hyunnie's personality.

Respond with JSON:
{{
    "message_analysis": {{
        "requires_thoughtful_response": true/false,
        "is_uncomfortable": true/false,
        "is_too_complex_for_persona": true/false
    }},
    "path_scores": {{
        "PATH_A": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_B": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_C": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_D": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_E": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_F": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_G": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_I": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_L": {{"score": 0-100, "reasoning": "brief explanation"}},
        "PATH_M": {{"score": 0-100, "reasoning": "brief explanation"}}
    }}
}}"""

    async def _call_routing_llm(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI for routing decision"""

        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[self.current_model_index]
                print(f" DEBUG: Calling OpenAI ({current_model}) for routing analysis...")

                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )

                response_text = response.choices[0].message.content.strip()

                if not response_text:
                    print(" Empty routing response, using fallback")
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
                        print(f" No valid JSON in routing response: '{response_text}'")
                        return self._get_routing_fallback()

                # Validate the new multi-path response format
                if "path_scores" not in result or "message_analysis" not in result:
                    print(f" Invalid routing response format, missing required keys")
                    return self._get_routing_fallback()

                print(f" Multi-path routing completed: {len(result['path_scores'])} paths scored")
                return result

            except Exception as e:
                print(f"OpenAI Routing Analysis Error with {current_model}: {e}")
                # Try next model
                self.current_model_index = (self.current_model_index + 1) % len(self.model_options)
                if attempt == len(self.model_options) - 1:
                    print("All OpenAI models failed for routing analysis")
                    return self._get_routing_fallback()

    def _get_routing_fallback(self) -> Dict[str, Any]:
        """Fallback routing decision - default to normal response with neutral scores"""
        # Generate neutral scores for all paths, favoring PATH_A
        default_scores = {
            "PATH_A": {"score": 80.0, "reasoning": "Fallback - normal response"},
            "PATH_B": {"score": 30.0, "reasoning": "Fallback"},
            "PATH_C": {"score": 30.0, "reasoning": "Fallback"},
            "PATH_D": {"score": 40.0, "reasoning": "Fallback"},
            "PATH_E": {"score": 30.0, "reasoning": "Fallback"},
            "PATH_F": {"score": 40.0, "reasoning": "Fallback"},
            "PATH_G": {"score": 20.0, "reasoning": "Fallback"},
            "PATH_I": {"score": 50.0, "reasoning": "Fallback"},
            "PATH_L": {"score": 30.0, "reasoning": "Fallback"},
            "PATH_M": {"score": 20.0, "reasoning": "Fallback"},
        }

        return {
            "message_analysis": {
                "requires_thoughtful_response": True,
                "is_uncomfortable": False,
                "is_too_complex_for_persona": False
            },
            "path_scores": default_scores
        }

    def _calculate_final_score(self, path_score: PathScore) -> float:
        """Calculate weighted final score from all factors"""
        return (
            path_score.base_score * 0.35 +
            path_score.context_modifier * 0.15 +
            (100 - path_score.frequency_penalty) * 0.20 +
            path_score.personality_bias * 0.10 +
            path_score.compatibility_score * 0.10 +
            path_score.energy_alignment * 0.05 +
            path_score.relationship_stage_modifier * 0.05
        )

    def _get_previous_path(self, context) -> Optional[str]:
        """Extract previous routing path from context"""
        if not context or not hasattr(context, 'messages') or len(context.messages) < 2:
            return None

        # Look for the most recent agent message with routing info
        for msg in reversed(context.messages):
            if msg.get('role') == 'agent' and 'routing_path' in msg:
                return msg['routing_path']

        return None

    def _calculate_context_modifier(self, path: str, context) -> float:
        """Calculate context-based modifier from conversation flow"""
        # Analyze recent conversation for context clues
        # This is a simplified version - could be enhanced with more sophisticated analysis

        if not context or not hasattr(context, 'messages'):
            return 50.0  # Neutral

        recent_messages = context.messages[-5:] if len(context.messages) >= 5 else context.messages

        # If conversation is getting repetitive, favor variety paths
        if len(recent_messages) >= 3:
            last_three_contents = [msg.get('content', '') for msg in recent_messages[-3:]]
            if len(set(last_three_contents)) == 1:  # All same content
                # Favor dramatic or playful paths to break repetition
                if path in ["PATH_E", "PATH_I"]:
                    return 70.0
                else:
                    return 40.0

        # Default neutral
        return 50.0

    def _estimate_user_engagement(self, context) -> float:
        """
        Estimate user engagement level (0.0-1.0) based on message patterns.

        Returns:
            Float between 0.0 (disengaged) and 1.0 (highly engaged)
        """
        if not context or not hasattr(context, 'messages') or len(context.messages) < 2:
            return 0.5  # Neutral for new conversations

        user_messages = [msg for msg in context.messages if msg.get('role') == 'user']

        if not user_messages:
            return 0.5

        # Calculate engagement factors
        recent_user_messages = user_messages[-5:] if len(user_messages) >= 5 else user_messages

        # Factor 1: Message length (longer = more engaged)
        avg_length = sum(len(msg.get('content', '')) for msg in recent_user_messages) / len(recent_user_messages)
        length_score = min(1.0, avg_length / 50.0)  # Normalize to 0-1

        # Factor 2: Response frequency (consistent responses = engaged)
        frequency_score = min(1.0, len(user_messages) / 10.0)

        # Factor 3: Emotional expression (emojis, punctuation)
        emotion_indicators = ['!', '?', '', '', '', '', '', '']
        recent_content = ' '.join([msg.get('content', '') for msg in recent_user_messages])
        emotion_count = sum(recent_content.count(indicator) for indicator in emotion_indicators)
        emotion_score = min(1.0, emotion_count / 5.0)

        # Weighted average
        engagement = (length_score * 0.4 + frequency_score * 0.3 + emotion_score * 0.3)

        return engagement

    def _get_response_strategy(self, path: RoutingPath) -> str:
        """Get response strategy description for a path"""
        strategy_map = {
            RoutingPath.RESPOND_NORMALLY: "Respond normally with natural personality",
            RoutingPath.RESPOND_WITH_CONFUSION: "Act confused about complex topic",
            RoutingPath.DEFLECT_REDIRECT: "Deflect and redirect conversation",
            RoutingPath.MINIMAL_RESPONSE: "Give very brief 1-2 word response",
            RoutingPath.IGNORE_SELF_FOCUS: "Ignore topic and focus dramatically on self",
            RoutingPath.EMOTIONAL_REACTION: "React with strong genuine emotion",
            RoutingPath.JEALOUS_POSSESSIVE: "Show jealousy and possessiveness",
            RoutingPath.PLAYFUL_TEASE: "Playfully tease or challenge",
            RoutingPath.VULNERABLE_REASSURANCE: "Show vulnerability and seek reassurance",
            RoutingPath.BOUNDARY_FIRM: "Firmly but sweetly establish boundary"
        }
        return strategy_map.get(path, "Respond appropriately")
