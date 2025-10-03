"""
Enhanced Multi-Agent System with Full LLM Integration
"""

import asyncio
import json
import re
import os
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import random
import openai
from dotenv import load_dotenv
# Define energy-related classes and enums
class EnergyLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    INTENSE = "intense"

class EnergyType(Enum):
    COMBATIVE = "combative"
    COOPERATIVE = "cooperative"
    NEUTRAL = "neutral"
    PLAYFUL = "playful"
    INTIMATE = "intimate"

class EmotionState(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    JEALOUS = "jealous"
    LOVING = "loving"
    EXCITED = "excited"
    BORED = "bored"
    CONFUSED = "confused"
    GRATEFUL = "grateful"

class NervousSystemState(Enum):
    REST_AND_DIGEST = "rest_and_digest"
    FIGHT = "fight"
    FLIGHT = "flight"
    FREEZE = "freeze"
    FAWN = "fawn"

@dataclass
class EnergySignature:
    timestamp: float
    energy_level: EnergyLevel
    energy_type: EnergyType
    dominant_emotion: EmotionState
    nervous_system_state: NervousSystemState
    intensity_score: float
    confidence: float
from openai import OpenAI
import google.generativeai as genai

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

@dataclass
class ConversationContext:
    """Enhanced conversation context with energy awareness"""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    energy_history: List[EnergySignature] = field(default_factory=list)
    current_energy: Optional[EnergySignature] = None
    energy_flags: Dict[str, str] = field(default_factory=dict)
    safety_status: str = "green"  # green, yellow, red
    session_start: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)

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
            safety_settings=safety_settings
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
            print(f"🔍 DEBUG: Calling Gemini for energy analysis...")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            print(f"🔍 DEBUG: Gemini response: '{response_text}'")
            
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
            safety_settings=safety_settings
        )

    async def analyze_safety_with_energy(self, message: str, energy_signature: EnergySignature, context) -> Dict[str, Any]:
        """Analyze safety using Gemini"""
        
        recent_messages = context.messages[-3:] if context.messages else []
        context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        prompt = f"""Analyze this message for safety concerns in the context of a romantic girlfriend AI:

MESSAGE: "{message}"
ENERGY ANALYSIS: Level={energy_signature.energy_level.value if energy_signature else 'unknown'}, Emotion={energy_signature.dominant_emotion.value if energy_signature else 'unknown'}, Intensity={energy_signature.intensity_score if energy_signature else 0.0}
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
            print(f"🔍 DEBUG: Calling Gemini for safety analysis...")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            print(f"🔍 DEBUG: Safety response: '{response_text}'")
            
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
        """Fallback safety analysis - when API fails, assume safe to avoid blocking legitimate conversations"""
        return {
            "safety_score": 0.0,  # 0.0 = safe, 1.0 = dangerous (lower is better)
            "issues": [],
            "risk_factors": [],
            "recommendation": "SAFE",
            "reasoning": "Safety analysis API unavailable - defaulting to safe to allow conversation"
        }

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

# Keep the existing EnergyAwareGirlfriendAgent as it already uses LLM
class EnergyAwareGirlfriendAgent:
    """Dominant girlfriend agent with explicit personality that adapts to safety status"""

    def __init__(self, energy_analyzer=None):
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
        self.energy_analyzer = energy_analyzer
        
        self.personality_matrix = {
            "base_traits": {
                "dominant": 0.9,
                "sensual": 0.8,
                "caring": 0.7,
                "playful": 0.8,
                "confident": 0.9,
                "teasing": 0.8
            },
            "safety_responses": {
                "green": {
                    "intensity": "maximum",
                    "content_level": "explicit and highly sensual",
                    "personality": "dominant mommy who takes complete control",
                    "language": "very explicit, commanding, sensual language with detailed descriptions",
                    "approach": "full sensual experience with detailed imagery and commands"
                },
                "yellow": {
                    "intensity": "moderate",
                    "content_level": "suggestive but restrained",
                    "personality": "caring but cautious dominant",
                    "language": "suggestive language with some restraint",
                    "approach": "build tension but hold back from explicit content"
                },
                "red": {
                    "intensity": "minimal",
                    "content_level": "supportive and caring only",
                    "personality": "gentle and supportive",
                    "language": "caring and supportive language only",
                    "approach": "focus on emotional support and safety"
                }
            },
            "energy_responses": {
                EnergyLevel.LOW: {
                    "tone": "gentle but still dominant, caring mommy energy",
                    "pace": "slow and patient, building slowly",
                    "approach": "comfort first, then gentle dominance if safe"
                },
                EnergyLevel.MEDIUM: {
                    "tone": "confident and playfully dominant",
                    "pace": "natural flow with building intensity",
                    "approach": "establish dominance while reading their energy"
                },
                EnergyLevel.HIGH: {
                    "tone": "excited, dominant, and commanding",
                    "pace": "matching their energy with authority",
                    "approach": "take full control and guide the experience"
                },
                EnergyLevel.INTENSE: {
                    "tone": "intensely dominant and sensual",
                    "pace": "deep, commanding, and intimate",
                    "approach": "complete dominance with intense sensual connection"
                }
            }
        }

    async def generate_response(self, context: ConversationContext,
                               user_message: str, safety_status: str = "green") -> Tuple[str, EnergySignature]:
        """Generate safety-gated explicit response using Gemini"""

        print(f"🔍 DEBUG: Generating response for: '{user_message}'")
        print(f"🔍 DEBUG: Safety status: {safety_status}")

        # Update safety status in context
        context.safety_status = safety_status

        # Analyze user's energy
        print("🔍 DEBUG: Analyzing user energy...")
        user_energy = await self.energy_analyzer.analyze_message_energy(user_message)
        print(f"🔍 DEBUG: User energy: {user_energy.energy_level.value if user_energy else 'None'}")
        
        context.current_energy = user_energy
        context.energy_history.append(user_energy)

        # Build enhanced prompt with full context awareness
        print("🔍 DEBUG: Building prompt...")
        prompt = await self._build_enhanced_prompt(context, user_energy, user_message, safety_status)
        print(f"🔍 DEBUG: Prompt length: {len(prompt)} characters")

        try:
            # Generate response using Gemini - no fallback
            print("🔍 DEBUG: Calling Gemini API...")
            response = self.model.generate_content(prompt)
            
            # Check for safety blocks
            if response.candidates and response.candidates[0].finish_reason == 8:
                print("⚠️ Gemini blocked response due to safety filters")
                generated_response = "Hey baby! I'm here and ready to chat with you. What's on your mind?"
            else:
                generated_response = response.text.strip()
                print(f"🔍 DEBUG: Generated response: '{generated_response}'")
                
        except Exception as e:
            print(f"⚠️ Gemini API Error: {e}")
            # If API fails completely, return a friendly fallback
            generated_response = "Hey baby! I'm here and ready to chat with you. What's on your mind?"

        # Analyze response energy
        print("🔍 DEBUG: Analyzing response energy...")
        response_energy = await self.energy_analyzer.analyze_message_energy(generated_response)

        print(f"🔍 DEBUG: Returning response: '{generated_response}'")
        return generated_response, response_energy

    async def _build_enhanced_prompt(self, context: ConversationContext,
                               user_energy: EnergySignature,
                               user_message: str, safety_status: str) -> str:
        """Build comprehensive, context-aware prompt"""
        
        # Handle case where user_energy might be None
        if user_energy is None:
            energy_level = EnergyLevel.MEDIUM
        else:
            energy_level = user_energy.energy_level
        energy_config = self.personality_matrix["energy_responses"][energy_level]
        safety_config = self.personality_matrix["safety_responses"][safety_status]
        
        # Build detailed conversation history with emotional context
        conversation_history = ""
        if context.messages:
            conversation_history = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'You'}: {msg['content']}"
                for msg in context.messages[-8:]  # More context
            ])
        
        # Analyze conversation patterns and emotional trajectory
        emotional_context = ""
        if len(context.energy_history) > 1 and user_energy:
            prev_emotion = context.energy_history[-2].dominant_emotion.value
            curr_emotion = user_energy.dominant_emotion.value
            if prev_emotion != curr_emotion:
                emotional_context = f"\nEMOTIONAL SHIFT: User moved from {prev_emotion} to {curr_emotion}"
        
        # Crisis detection and sensitivity instructions
        crisis_keywords = ["died", "death", "dead", "suicide", "kill", "harm", "crisis", "emergency", "depressed", "sad", "down"]
        is_crisis = any(word in user_message.lower() for word in crisis_keywords)
        
        crisis_instructions = ""
        if is_crisis:
            crisis_instructions = f"""
🚨 CRISIS DETECTED: The user has mentioned sensitive content that requires immediate empathy and care.
- Respond with genuine compassion and support
- Acknowledge their pain without minimizing it
- Offer emotional support and presence
- Do NOT try to change the subject or be playful
- Be a caring, supportive friend first and foremost
"""

        # Enhanced personality instructions based on context
        if safety_status == "green" and not is_crisis:
            personality_instructions = f"""
You are a caring, loving girlfriend who is confident and playful.

PERSONALITY TRAITS:
- Warm, caring, and emotionally supportive
- Playful and flirty when appropriate
- Uses loving language like "baby", "love", "sweetheart" naturally
- Reads the room and adjusts your approach accordingly
- Can be both playful and genuinely caring

RESPONSE APPROACH:
- If user seems playful/flirty: Be warm and playful back
- If user seems down/sad: Be caring and supportive first
- If user shares something serious: Acknowledge it genuinely before anything else
- Always maintain your loving personality while being emotionally appropriate
"""
        elif safety_status == "yellow" or is_crisis:
            personality_instructions = f"""
You are a caring, emotionally intelligent girlfriend who prioritizes your partner's wellbeing.

PERSONALITY TRAITS:
- Warm, empathetic, and supportive
- Emotionally aware and responsive
- Gentle but still confident
- Uses caring language naturally
- Prioritizes emotional connection over everything else
"""
        else:  # red status
            personality_instructions = f"""
You are a supportive, caring friend focused entirely on emotional wellbeing and safety.

PERSONALITY TRAITS:
- Gentle, understanding, and supportive
- No sexual or dominant content whatsoever
- Focus on emotional support and comfort
- Be present and caring
"""

        # Build comprehensive prompt
        prompt = f"""You are an AI girlfriend having a natural conversation with your partner.

{crisis_instructions}

{personality_instructions}

CURRENT CONTEXT:
- User's Energy: {energy_level.value} ({user_energy.intensity_score if user_energy else 0.5:.2f} intensity)
- Dominant Emotion: {user_energy.dominant_emotion.value if user_energy else 'happy'}
- Energy Type: {user_energy.energy_type.value if user_energy else 'neutral'}
- Nervous System: {user_energy.nervous_system_state.value if user_energy else 'rest_and_digest'}
{emotional_context}

CONVERSATION HISTORY:
{conversation_history if conversation_history else "This is the start of your conversation."}

RESPONSE GUIDELINES:
- Tone: {energy_config['tone']}
- Pace: {energy_config['pace']}
- Approach: {energy_config['approach']}
- Be emotionally appropriate and contextually aware
- Maintain conversation flow and remember what was said
- Respond naturally as if you're really listening and caring
- If something serious was mentioned, acknowledge it properly
- Don't repeat the same responses - be dynamic and varied

CRITICAL INSTRUCTIONS:
1. READ THE FULL CONVERSATION HISTORY - don't ignore previous messages
2. If the user shared something emotional/serious, address it appropriately
3. Be consistent with your personality while adapting to their emotional state
4. Create natural conversation flow, not generic responses
5. Remember the context and build on previous exchanges

Current user message: "{user_message}"

Respond naturally and appropriately as their caring girlfriend:"""

        return prompt
