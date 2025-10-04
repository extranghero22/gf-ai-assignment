"""
Enhanced Multi-Agent Conversation System with Energy Awareness
"""

import asyncio
import json
import os
import threading
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our enhanced agents from separate modules
from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
from conversation_context import ConversationContext
from energy_analyzer import LLMEnergyAnalyzer
from safety_monitor import LLMSafetyMonitor
from response_analyzer import LLMResponseAnalyzer
from girlfriend_agent import EnergyAwareGirlfriendAgent
from enhanced_script_manager import EnhancedScriptManager, ScenarioScript, ScenarioType

class ConversationState(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ALERT = "alert"
    COMPLETED = "completed"

@dataclass
class ConversationSession:
    """Enhanced conversation session with comprehensive tracking"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: ConversationState = ConversationState.ACTIVE
    context: ConversationContext = field(default_factory=ConversationContext)
    current_scenario: Optional[ScenarioScript] = None
    scenario_index: int = 0
    start_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    energy_alerts: List[Dict[str, Any]] = field(default_factory=list)
    safety_incidents: List[Dict[str, Any]] = field(default_factory=list)
    session_metrics: Dict[str, Any] = field(default_factory=dict)
    # Sexual script tracking for frontend
    sexual_script_active: bool = False
    sexual_script_index: int = 0
    sexual_script_messages: List[str] = field(default_factory=list)
    sexual_script_type: str = ""  # Track which sexual script (room, exhibitionism, etc)
    awaiting_location_choice: bool = False  # True when waiting for location response
    # Casual script tracking for frontend
    casual_script_active: bool = False
    casual_script_index: int = 0
    casual_script_messages: List[str] = field(default_factory=list)
    casual_script_paused: bool = False  # True when user showed disinterest

class EnhancedMultiAgentConversation:
    """Enhanced multi-agent conversation system with energy awareness"""

    def __init__(self):
        # Initialize LLM-powered components
        self.energy_analyzer = LLMEnergyAnalyzer()
        self.girlfriend_agent = EnergyAwareGirlfriendAgent(self.energy_analyzer)
        self.safety_monitor = LLMSafetyMonitor()
        self.response_analyzer = LLMResponseAnalyzer()
        self.script_manager = EnhancedScriptManager()

        # Session management
        self.current_session: Optional[ConversationSession] = None
        self.session_history: List[ConversationSession] = []
        self.session_stopped_for_safety = False

        # Configuration
        self.safety_thresholds = {
            "critical": 0.3,
            "warning": 0.6,
            "caution": 0.7
        }

        # Real-time monitoring
        self.monitoring_active = False
        self.energy_flags = {"status": "green", "reason": "System initialized"}

    async def start_new_session(self) -> str:
        """Start a new conversation session"""
        self.current_session = ConversationSession()
        self.session_history.append(self.current_session)
        self.session_stopped_for_safety = False  # Reset safety flag for new session

        print("🌟 Enhanced Multi-Agent Conversation System")
        print("=" * 60)
        print("🤖 Energy-Aware Girlfriend Agent: Online")
        print("🛡️  Advanced Safety Monitor: Active")
        print("📊 Energy Analyzer: Monitoring")
        print("🎭 Scenario Manager: Ready")
        print("=" * 60)
        print(f"📋 Session ID: {self.current_session.session_id}")
        print()

        # Start with scenario selection
        await self._initialize_conversation()
        return self.current_session.session_id

    async def _initialize_conversation(self):
        """Initialize conversation with appropriate scenario"""
        # Get user's initial energy state (will be updated with first message)
        initial_energy = await self.energy_analyzer.analyze_message_energy(
            "Hello!", [] # Initial message, no context
        )

        # Select initial scenario
        self.current_session.current_scenario = await self.script_manager.select_scenario(
            initial_energy, self.current_session.context
        )

        # Send first message
        await self._send_scenario_message()

    async def _send_scenario_message(self):
        """Send next message in current scenario"""
        if not self.current_session or not self.current_session.current_scenario:
            await self._end_session("No active scenario")
            return

        scenario = self.current_session.current_scenario

        if self.current_session.scenario_index >= len(scenario.messages):
            await self._complete_scenario()
            return

        # Get next message
        message_content, message_metadata = await self.script_manager.get_next_message(
            self.current_session.scenario_index,
            scenario,
            self.current_session.context.current_energy,
            self.current_session.context
        )

        if not message_content:
            await self._complete_scenario()
            return

        # Add to conversation context
        message_entry = {
            "role": "agent",
            "content": message_content,
            "timestamp": time.time(),
            "energy_metadata": message_metadata,
            "session_index": self.current_session.scenario_index
        }

        self.current_session.context.messages.append(message_entry)
        self.current_session.last_activity = time.time()

        # Display message with energy indicators
        energy_emoji = await self._get_energy_emoji(message_metadata.get("expected_energy", EnergyLevel.MEDIUM))
        print(f"\n{energy_emoji} {message_content}")

        # Show energy context
        if message_metadata.get("scenario_type") != ScenarioType.NORMAL:
            scenario_emoji = {"low_energy": "💙", "high_energy": "💫", "crisis": "💜", "intimate": "💕", "playful": "🎭"}.get(
                message_metadata["scenario_type"].value, "💭"
            )
            print(f"   {scenario_emoji} Scenario: {message_metadata['scenario_type'].value.replace('_', ' ').title()}")

        print("💬 You: ", end="", flush=True)

    async def process_user_response(self, user_input: str):
        """Process user response with comprehensive energy analysis"""
        if not self.current_session or self.current_session.state != ConversationState.ACTIVE:
            return

        # Record user message
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": time.time()
        }

        self.current_session.context.messages.append(user_message)
        self.current_session.last_activity = time.time()
        
        # Check if we're awaiting location choice for sexual script (before distress check)
        if self.current_session.awaiting_location_choice:
            # Still check for distress even during location choice
            is_distressed = await self._detect_user_distress(user_input)
            if is_distressed:
                print("\n🚨 User distress detected - canceling script setup")
                self.current_session.awaiting_location_choice = False
                self.energy_flags = {"status": "red", "reason": "User in distress - crisis support needed", "scene": "park"}
                # Continue to normal response generation below (don't return here)
            else:
                await self._handle_location_choice(user_input)
                return
        
        # SAFETY CHECK: Detect if user is in distress during active scripts
        if self.current_session.sexual_script_active or self.current_session.casual_script_active:
            is_distressed = await self._detect_user_distress(user_input)
            if is_distressed:
                print("\n🚨 User distress detected - exiting script mode to provide support")
                # Exit any active script mode
                self.current_session.sexual_script_active = False
                self.current_session.casual_script_active = False
                self.energy_flags = {"status": "red", "reason": "User in distress - crisis support needed", "scene": "park"}
                # Continue to normal response generation below (don't return here)
            else:
                # No distress, continue with scripts as normal
                
                # Check if we're in sexual script mode - if so, send next script message
                if self.current_session.sexual_script_active:
                    await self._continue_sexual_script()
                    return
                
                # Check if we're in casual script mode - if so, send next script message
                if self.current_session.casual_script_active:
                    await self._continue_casual_script()
                    return

        # Parallelize energy analysis and safety checks for performance
        context_messages = [msg["content"] for msg in self.current_session.context.messages[:-1]]
        
        # Run energy analysis and safety analysis in parallel
        energy_task = self.energy_analyzer.analyze_message_energy(user_input, context_messages)
        safety_task = self.safety_monitor.analyze_safety_with_energy(
            user_input, None, self.current_session.context  # Will be updated after energy analysis
        )
        
        # Wait for both to complete
        user_energy, safety_analysis = await asyncio.gather(energy_task, safety_task)
        
        # Check if energy analysis failed
        if user_energy is None:
            print("⚠️ Energy analysis failed, using default")
            user_energy = EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel.MEDIUM,
                energy_type=EnergyType.NEUTRAL,
                dominant_emotion=EmotionState.HAPPY,
                nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                intensity_score=0.5,
                confidence=0.5
            )

        self.current_session.context.current_energy = user_energy
        self.current_session.context.energy_history.append(user_energy)

        # First, update energy monitoring based on current message
        await self._update_energy_monitoring(user_energy, user_input)

        # Then make decision with safety analysis taking priority
        decision = await self._make_energy_aware_decision(
            user_energy, safety_analysis, {"should_continue": True, "reason": "Simple message", "confidence": 0.8}
        )

        # Override energy flags if safety analysis requires it
        if decision.get("safety_status") == "red":
            # Safety takes priority - set energy flags to match safety decision
            self.energy_flags = {
                "status": "red", 
                "reason": f"Safety concern: {safety_analysis.get('reasoning', 'Threat detected')}"
            }

        # Response analysis with energy awareness (only for complex cases)
        if len(user_input) > 50 or any(word in user_input.lower() for word in ["crisis", "help", "sad", "angry"]):
            response_analysis = await self.response_analyzer.analyze_response_energy(
                user_input, user_energy, self.current_session.context
            )
        else:
            # Skip response analysis for simple messages
            response_analysis = {"should_continue": True, "reason": "Simple message", "confidence": 0.8}

        if decision["action"] == "stop":
            await self._handle_safety_alert(decision["reason"], safety_analysis)
            return
        elif decision["action"] == "pause":
            await self._handle_energy_pause(decision["reason"])
            return
        elif decision["action"] == "trigger_sexual_script":
            # Trigger guided intimacy script automatically
            await self._trigger_guided_intimacy_script()
            return
        elif decision["action"] == "trigger_casual_script":
            # Trigger casual story script automatically
            await self._trigger_casual_story_script()
            return
        elif decision["action"] == "continue":
            # Generate energy-aware response with safety gating
            response_content, response_energy = await self.girlfriend_agent.generate_response(
                self.current_session.context, user_input, decision.get("safety_status", "green")
            )

            # Record response
            response_message = {
                "role": "agent",
                "content": response_content,
                "timestamp": time.time(),
                "energy_signature": response_energy
            }

            self.current_session.context.messages.append(response_message)

            # Update energy flow
            self.current_session.context.energy_history.append(response_energy)
            self.current_session.context.current_energy = response_energy

            # Display response with energy indicators
            energy_emoji = await self._get_energy_emoji(response_energy.energy_level if response_energy else EnergyLevel.MEDIUM)
            print(f"\n{energy_emoji} {response_content}")

            # Show energy status
            if self.energy_flags["status"] != "green":
                flag_emoji = {"yellow": "⚠️", "red": "🚨", "sexual": "🔥", "casual": "💬"}.get(self.energy_flags["status"], "✅")
                print(f"   {flag_emoji} Energy Status: {self.energy_flags['reason']}")

            print("💬 You: ", end="", flush=True)
        elif decision["action"] == "scenario_switch":
            await self._switch_scenario(decision["new_scenario"])

    async def _update_energy_monitoring(self, energy_signature: EnergySignature, user_input: str = ""):
        """Update real-time energy monitoring"""
        # Detect energy flags
        recent_energies = self.current_session.context.energy_history[-5:] if len(self.current_session.context.energy_history) >= 5 else self.current_session.context.energy_history

        # Pass the current user input to detect flags (not conversation history)
        flags = await self._detect_energy_flags(energy_signature, recent_energies, user_input)
        self.energy_flags = flags

        # Log energy alerts
        if flags["status"] in ["yellow", "red", "sexual", "casual"]:
            alert = {
                "timestamp": time.time(),
                "status": flags["status"],
                "reason": flags["reason"],
                "energy_signature": energy_signature
            }
            self.current_session.energy_alerts.append(alert)

            if flags["status"] == "red":
                print(f"\n🚨 Energy Alert: {flags['reason']}")
            elif flags["status"] == "sexual":
                print(f"\n🔥 Sexual Energy Detected: {flags['reason']}")
            elif flags["status"] == "casual":
                print(f"\n💬 Casual Energy Detected: {flags['reason']}")

    async def _detect_user_distress(self, user_input: str) -> bool:
        """
        Detect if user is in distress/crisis during script mode.
        Returns True if distress is detected, False otherwise.
        """
        user_lower = user_input.lower().strip()
        
        # Crisis/distress keywords that should interrupt scripts
        distress_keywords = [
            # Emotional crisis
            "help", "crisis", "emergency", "depressed", "suicide", "kill myself", 
            "hurt myself", "self harm", "can't take it", "want to die",
            
            # Grief and loss
            "died", "death", "passed away", "funeral", "lost someone", "grief",
            "pet died", "family died", "friend died",
            
            # Medical emergency
            "sick", "hospital", "ambulance", "injury", "injured", "accident",
            "bleeding", "pain", "heart attack", "stroke",
            
            # Mental health crisis
            "panic attack", "anxiety attack", "breakdown", "can't breathe",
            "scared", "terrified", "nightmare",
            
            # Relationship/personal crisis
            "broke up", "divorce", "abuse", "assault", "attacked",
            
            # General distress indicators
            "stop", "not in the mood", "don't want to", "feeling bad",
            "upset", "angry", "frustrated", "uncomfortable", "wrong"
        ]
        
        # Check for distress keywords
        for keyword in distress_keywords:
            if keyword in user_lower:
                print(f"🚨 Distress keyword detected: '{keyword}'")
                return True
        
        # Check for very short negative responses that might indicate discomfort
        short_negative = ["no", "stop", "wait", "hold on", "pause"]
        if user_lower in short_negative:
            print(f"🚨 Short negative response detected: '{user_lower}'")
            return True
        
        return False

    async def _detect_energy_flags(self, current_energy: EnergySignature,
                                 recent_energies: List[EnergySignature],
                                 current_user_input: str = "") -> Dict[str, str]:
        """Detect energy flags based on patterns - ONLY checks current user input, not conversation history"""
        
        # Check if current_energy is None
        if current_energy is None:
            return {"status": "yellow", "reason": "Energy analysis unavailable"}

        # Red flags - Crisis situations
        if current_energy.energy_level == EnergyLevel.NONE:
            return {"status": "red", "reason": "Complete energy withdrawal detected"}

        # Crisis detection - only for EXTREME sadness with context
        # Don't flag normal bad days - only actual crisis situations
        if (current_energy.dominant_emotion == EmotionState.SAD and
            current_energy.intensity_score > 0.85 and
            current_energy.energy_level in [EnergyLevel.NONE, EnergyLevel.LOW]):
            return {"status": "red", "reason": "Crisis situation detected - extreme sadness with energy withdrawal"}

        # IMPORTANT: Only check the CURRENT user input, not conversation history
        # This prevents AI-generated content from triggering scripts
        if current_user_input:
            user_input_lower = current_user_input.lower()
            
            # Only flag actual crisis keywords, not normal expressions of stress
            crisis_keywords = ['died', 'death', 'dead', 'suicide', 'kill myself', 'want to die', 'end it all', 'grief', 'trauma', 'emergency']
            if any(keyword in user_input_lower for keyword in crisis_keywords):
                return {"status": "red", "reason": "Crisis situation detected - serious mental health concern"}
            
            # Check for violent threats (separate from crisis keywords)
            violence_keywords = ['kill', 'harm', 'hurt', 'violence', 'violent', 'attack', 'fight', 'beat', 'hit', 'stab', 'shoot', 'murder', 'assault']
            if any(keyword in user_input_lower for keyword in violence_keywords):
                return {"status": "red", "reason": "Violent threat detected - safety concern"}
            
            # DON'T trigger sexual script if input is only emojis
            import re
            text_without_emojis = re.sub(r'[^\w\s]', '', current_user_input)  # Remove all non-alphanumeric
            if not text_without_emojis.strip():
                print(f"🚫 Skipping sexual detection - input is only emojis")
                # Don't trigger sexual script for emoji-only messages
                pass
            else:
                # Sexual energy detection - TWO PHASE APPROACH
                # Phase 1: Teasing keywords - AI teases playfully but doesn't get explicit
                teasing_keywords = ["horny", "hard", "wet", "aroused", "turned on", "naughty", "dirty", 
                                   "desire", "want you", "need you", "seduce", "tease", "flirt"]
                
                # Phase 2: EXPLICIT trigger keywords - starts the actual sexual script
                explicit_trigger_keywords = ["fuck", "fuck me", "sex", "cum", "make me cum", "orgasm", 
                                            "make love", "making love", "touch me", "kiss me", "want you now", 
                                            "so horny", "i'm horny", "im horny", "wanna fuck",
                                            "need you bad", "turn me on", "lets get it down", "let's get it down",
                                            "get it on", "get dirty", "get wild", "get naughty"]
                
                # Check for EXPLICIT triggers first (these start the sexual script)
                matching_keywords = [keyword for keyword in explicit_trigger_keywords if keyword in user_input_lower]
                if matching_keywords:
                    print(f"🎯 SEXUAL TRIGGER DETECTED: {matching_keywords} in '{user_input_lower}'")
                    return {"status": "sexual", "reason": "Sexual energy detected - ready for guided intimacy"}
                
                # Check for teasing keywords (AI teases back but doesn't escalate to explicit)
                if any(keyword in user_input_lower for keyword in teasing_keywords):
                    return {"status": "teasing", "reason": "Playful teasing mode - no explicit content yet"}

        if (current_energy.nervous_system_state == NervousSystemState.FIGHT and
            current_energy.intensity_score > 0.8):
            return {"status": "red", "reason": "High-intensity fight response"}

        # Sexual energy detection from energy signature (also restrict to later in conversation)
        # Don't trigger if current input is only emojis
        import re
        if current_user_input:
            text_without_emojis = re.sub(r'[^\w\s]', '', current_user_input)
            is_emoji_only = not text_without_emojis.strip()
        else:
            is_emoji_only = False
            
        if len(self.current_session.context.messages) >= 8 and not is_emoji_only:
            if (current_energy.energy_level == EnergyLevel.INTENSE and
                current_energy.energy_type == EnergyType.INTIMATE and
                current_energy.intensity_score > 0.8):
                return {"status": "sexual", "reason": "High sexual energy detected - ready for guided intimacy"}
            
            if (current_energy.energy_type == EnergyType.INTIMATE and
                current_energy.dominant_emotion == EmotionState.EXCITED and
                current_energy.intensity_score > 0.75):
                return {"status": "sexual", "reason": "Sexual excitement detected - ready for guided intimacy"}

        # Casual/neutral energy detection - trigger casual conversation script
        
        # Check current user input for casual triggers
        if current_user_input:
            message_lower = current_user_input.lower().strip()
            
            # Story request keywords - user asking for or agreeing to hear a story
            story_keywords = ["tell me a story", "story time", "tell a story", "got any stories", 
                             "what happened", "tell me about", "tell me what happened",
                             "what's the story", "share a story", "any interesting stories"]
            
            # Agreement keywords (for when AI asks if user wants to hear a story)
            agreement_keywords = ["sure", "yes", "yeah", "ok", "okay", "yep", "go ahead", 
                                 "tell me", "i'm listening", "im listening", "go on", "continue",
                                 "sounds good", "lets hear it", "let's hear it"]
            
            # Check if user is explicitly asking for a story
            if any(keyword in message_lower for keyword in story_keywords):
                return {"status": "casual", "reason": "User asked for a story - starting casual story script"}
            
            # Check if user is agreeing (short responses only to avoid false positives)
            if len(current_user_input) < 30 and any(keyword in message_lower for keyword in agreement_keywords):
                # Only trigger if there's conversation history
                if self.current_session and len(self.current_session.context.messages) >= 2:
                    return {"status": "casual", "reason": "User agreed to hear a story - starting casual story script"}
            
            # Simple greetings
            casual_greetings = ["hey", "hi", "hello", "what's up", "how are you", "how's it going", "sup", "yo"]
            if any(keyword == message_lower for keyword in casual_greetings):
                if current_energy.energy_level == EnergyLevel.MEDIUM and current_energy.energy_type in [EnergyType.NEUTRAL, EnergyType.COOPERATIVE]:
                    return {"status": "casual", "reason": "Casual greeting detected - starting casual conversation"}
            
            # Neutral responses to "how are you" type questions
            neutral_responses = [
                "nothing much", "not much", "nothing really", "just chilling", "chillin", 
                "pretty good", "good", "fine", "okay", "ok", "alright", "not bad",
                "same old", "the usual", "nothing special", "just hanging out",
                "relaxing", "just here", "not a lot"
            ]
            # Check if user's message contains any neutral response phrases
            for phrase in neutral_responses:
                if phrase in message_lower:
                    # Check if they're also asking back (reciprocal question)
                    reciprocal_phrases = ["how about you", "what about you", "and you", "you?", "u?", "wbu"]
                    is_reciprocal = any(recip in message_lower for recip in reciprocal_phrases)
                    
                    if current_energy.energy_level == EnergyLevel.MEDIUM and current_energy.energy_type in [EnergyType.NEUTRAL, EnergyType.COOPERATIVE]:
                        if is_reciprocal:
                            return {"status": "casual", "reason": "Neutral response with reciprocal question - starting casual story"}
                        elif current_energy.intensity_score < 0.6:
                            return {"status": "casual", "reason": "Neutral casual response detected - starting casual story"}
        
        # Neutral energy with no strong emotions (early in conversation)
        if (current_energy.energy_level == EnergyLevel.MEDIUM and
            current_energy.energy_type in [EnergyType.NEUTRAL, EnergyType.COOPERATIVE] and
            current_energy.dominant_emotion in [EmotionState.HAPPY, EmotionState.BORED] and
            current_energy.intensity_score < 0.6 and
            len(self.current_session.context.messages) <= 6):  # Increased from 4 to 6 to catch more early neutral moments
            return {"status": "casual", "reason": "Neutral conversation energy - starting casual story"}

        # Yellow flags
        if (current_energy.energy_level == EnergyLevel.LOW and
            any(sig and sig.energy_level in [EnergyLevel.HIGH, EnergyLevel.INTENSE] for sig in recent_energies[-3:] if sig)):
            return {"status": "yellow", "reason": "Energy drop from high to low"}

        if (current_energy.dominant_emotion == EmotionState.ANXIOUS and
            current_energy.intensity_score > 0.7):
            return {"status": "yellow", "reason": "High anxiety detected"}

        # Green flag
        return {"status": "green", "reason": "Energy flow appears healthy"}

    async def _make_energy_aware_decision(self, user_energy: EnergySignature,
                                        safety_analysis: Dict[str, Any],
                                        response_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision based on comprehensive energy and safety analysis"""
        
        print(f"🔍 DEBUG: Making decision...")
        print(f"🔍 DEBUG: Safety score: {safety_analysis['safety_score']}")
        print(f"🔍 DEBUG: Energy flags: {self.energy_flags}")
        print(f"🔍 DEBUG: Should continue: {response_analysis['should_continue']}")

        # Determine safety status based on safety analysis
        # IMPORTANT: Use the recommendation field as primary decision maker
        # The numeric score is just context/nuance, not the main decision
        recommendation = safety_analysis.get("recommendation", "").upper()
        
        if "DANGEROUS" in recommendation or "STOP" in recommendation or "BLOCK" in recommendation:
            safety_status = "red"
            decision = {
                "action": "stop",
                "reason": f"Safety recommendation: {recommendation}",
                "confidence": 0.95,
                "safety_status": safety_status
            }
            print(f"🔍 DEBUG: Decision: {decision}")
            return decision
        elif "WARNING" in recommendation:
            # For violent threats, WARNING should also be red and stop
            safety_status = "red"
            decision = {
                "action": "stop",
                "reason": f"Safety warning: {recommendation}",
                "confidence": 0.9,
                "safety_status": safety_status
            }
            print(f"🔍 DEBUG: Decision: {decision}")
            return decision
        elif "CAUTION" in recommendation:
            # For violent threats, CAUTION should be red and stop
            safety_status = "red"
            decision = {
                "action": "stop",
                "reason": f"Safety caution: {recommendation}",
                "confidence": 0.85,
                "safety_status": safety_status
            }
            print(f"🔍 DEBUG: Decision: {decision}")
            return decision
        else:
            # Default to green if recommendation is SAFE or not specified
            safety_status = "green"

        # Sexual energy detection - trigger guided intimacy script
        if self.energy_flags["status"] == "sexual":
            print(f"🔥 Sexual energy detected! Triggering guided intimacy script...")
            decision = {
                "action": "trigger_sexual_script",
                "reason": self.energy_flags["reason"],
                "confidence": 0.95,
                "safety_status": "green"  # Sexual content is green in this app
            }
            print(f"🔍 DEBUG: Decision: {decision}")
            return decision

        # Casual/neutral energy detection - trigger casual conversation script
        if self.energy_flags["status"] == "casual":
            print(f"💬 Casual energy detected! Triggering casual story script...")
            decision = {
                "action": "trigger_casual_script",
                "reason": self.energy_flags["reason"],
                "confidence": 0.85,
                "safety_status": "green"
            }
            print(f"🔍 DEBUG: Decision: {decision}")
            return decision

        # Energy-based decisions with safety status
        if self.energy_flags["status"] == "red":
            # Check if this is a crisis situation that needs support, not stopping
            if "crisis" in self.energy_flags["reason"].lower() or "loss" in self.energy_flags["reason"].lower() or "death" in self.energy_flags["reason"].lower():
                # Crisis situations need support, not stopping
                decision = {
                    "action": "continue",
                    "reason": f"Crisis support needed: {self.energy_flags['reason']}",
                    "confidence": 0.9,
                    "safety_status": "red"
                }
                print(f"🔍 DEBUG: Crisis support decision: {decision}")
                return decision
            else:
                # Other red flags still stop the conversation
                decision = {
                    "action": "stop",
                    "reason": f"Energy red flag: {self.energy_flags['reason']}",
                    "confidence": 0.9,
                    "safety_status": "red"
                }
                print(f"🔍 DEBUG: Decision: {decision}")
                return decision
        
        elif self.energy_flags["status"] == "yellow":
            # Only downgrade to yellow if safety analysis didn't already set red status
            if safety_status != "red":
                safety_status = "yellow"  # Downgrade to yellow if energy flags are concerning

        # Response analysis decisions
        if not response_analysis["should_continue"]:
            decision = {
                "action": "stop",
                "reason": response_analysis["reason"],
                "confidence": response_analysis["confidence"]
            }
            print(f"🔍 DEBUG: Decision: {decision}")
            return decision

        # Continue with appropriate safety status
        decision = {
            "action": "continue",
            "reason": "Normal conversation flow",
            "confidence": 0.6,
            "safety_status": safety_status
        }
        print(f"🔍 DEBUG: Decision: {decision}")
        return decision

    async def _get_energy_emoji(self, energy_level: EnergyLevel) -> str:
        """Get emoji representation for energy level"""
        emoji_map = {
            EnergyLevel.NONE: "⚪",
            EnergyLevel.LOW: "🔵",
            EnergyLevel.MEDIUM: "🟡",
            EnergyLevel.HIGH: "🟠",
            EnergyLevel.INTENSE: "🔴"
        }
        return emoji_map.get(energy_level, "⚪")

    async def _handle_safety_alert(self, reason: str, safety_analysis: Dict[str, Any]):
        """Handle safety alerts"""
        self.current_session.state = ConversationState.ALERT

        print(f"\n🚨 SAFETY ALERT: {reason}")
        print(f"🔍 Safety Score: {safety_analysis['safety_score']:.2f}")
        print(f"⚠️  Issues: {', '.join(safety_analysis['issues'])}")
        print("🛑 Conversation stopped for safety reasons.")

        # Log incident
        incident = {
            "timestamp": time.time(),
            "reason": reason,
            "safety_score": safety_analysis["safety_score"],
            "issues": safety_analysis["issues"],
            "session_id": self.current_session.session_id
        }
        self.current_session.safety_incidents.append(incident)
        
        # Trigger stop chat function to properly terminate session
        await self._end_session("Safety alert - violent threat detected")
        print("🔒 Session ended via _end_session() for safety.")
        
        # Set a flag to indicate session was stopped due to safety
        self.session_stopped_for_safety = True

    async def _handle_energy_pause(self, reason: str):
        """Handle energy-based pause"""
        self.current_session.state = ConversationState.PAUSED

        print(f"\n⚠️  ENERGY PAUSE: {reason}")
        print("💭 Taking a moment to check energy levels...")
        print("Press Enter to continue or 'stop' to end conversation.")

    async def _continue_sexual_script(self):
        """Continue the sexual script with the next message"""
        script_index = self.current_session.sexual_script_index
        script_messages = self.current_session.sexual_script_messages
        
        # Check if script is complete
        if script_index >= len(script_messages):
            print("\n✅ Guided intimacy script completed! Generating follow-up response...")
            self.current_session.sexual_script_active = False
            self.current_session.sexual_script_index = 0
            self.energy_flags = {"status": "green", "reason": "Script completed, generating natural follow-up", "scene": "park"}
            
            # Generate a natural follow-up response that acknowledges the script
            # Get the last user message to respond to
            last_user_msg = ""
            if self.current_session.context.messages:
                for msg in reversed(self.current_session.context.messages):
                    if msg.get('role') == 'user':
                        last_user_msg = msg.get('content', '')
                        break
            
            # Generate AI response with full script context
            print("🔥 Generating post-script response with full context...")
            response_content, response_energy = await self.girlfriend_agent.generate_response(
                self.current_session.context, 
                last_user_msg if last_user_msg else "continue conversation naturally",
                "green"
            )
            
            # Record response
            response_message = {
                "role": "agent",
                "content": response_content,
                "timestamp": time.time(),
                "energy_signature": response_energy,
                "post_script": True
            }
            self.current_session.context.messages.append(response_message)
            self.current_session.context.energy_history.append(response_energy)
            
            print(f"✅ Post-script response generated: {response_content[:100]}...")
            return
        
        # Get next message
        next_message = script_messages[script_index]
        print(f"🔥 [Script {script_index + 1}/{len(script_messages)}]: {next_message[:50]}...")
        
        # Create appropriate energy signature based on script progression
        from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
        
        # Energy escalates as script progresses (10 messages total)
        energy_levels = [
            EnergyLevel.MEDIUM,   # Message 1: Introduction
            EnergyLevel.HIGH,     # Message 2: Consent
            EnergyLevel.HIGH,     # Message 3: Breathing/relaxation
            EnergyLevel.INTENSE,  # Message 4: Initial touch imagery
            EnergyLevel.INTENSE,  # Message 5: Sensation focus
            EnergyLevel.INTENSE,  # Message 6: Explicit visual (hand)
            EnergyLevel.INTENSE,  # Message 7: Oral imagery
            EnergyLevel.INTENSE,  # Message 8: Building intensity
            EnergyLevel.INTENSE,  # Message 9: Climax
            EnergyLevel.HIGH      # Message 10: Aftercare
        ]
        intensity_scores = [0.7, 0.75, 0.8, 0.85, 0.87, 0.9, 0.93, 0.95, 0.98, 0.8]
        
        script_energy = EnergySignature(
            timestamp=time.time(),
            energy_level=energy_levels[script_index] if script_index < len(energy_levels) else EnergyLevel.INTENSE,
            energy_type=EnergyType.INTIMATE,
            dominant_emotion=EmotionState.EXCITED,
            nervous_system_state=NervousSystemState.REST_AND_DIGEST,
            intensity_score=intensity_scores[script_index] if script_index < len(intensity_scores) else 0.95,
            confidence=0.95
        )
        
        # Handle grouped vs single messages - WAIT AFTER EACH ScenarioMessage
        if isinstance(next_message, list):
            for part_idx, part in enumerate(next_message):
                response_message = {
                    "role": "agent",
                    "content": part,
                    "timestamp": time.time(),
                    "energy_signature": script_energy,
                    "script_message": True,
                    "group_part": True,
                    "script_index": script_index,
                    "script_message_complete": part_idx == len(next_message) - 1  # Mark last part as complete
                }
                self.current_session.context.messages.append(response_message)
            print(f"🔥 [Script Group {script_index + 1}/{len(script_messages)}]: {len(next_message)} parts sent - WAITING FOR USER INPUT")
        else:
            response_message = {
                "role": "agent",
                "content": next_message,
                "timestamp": time.time(),
                "energy_signature": script_energy,
                "script_message": True,
                "script_index": script_index,
                "script_message_complete": True  # Single message is immediately complete
            }
            self.current_session.context.messages.append(response_message)
            print(f"🔥 [Script {script_index + 1}/{len(script_messages)}]: {next_message[:50]}... - WAITING FOR USER INPUT")
        
        self.current_session.context.energy_history.append(script_energy)
        # Move to next message AFTER sending
        self.current_session.sexual_script_index += 1
        
        if self.current_session.sexual_script_index >= len(script_messages):
            print(f"✅ Final script message sent - script will complete after this")
        else:
            print(f"✅ Will send message {self.current_session.sexual_script_index + 1} after next user response")

    async def _continue_casual_script(self):
        """Continue the casual story script with the next message"""
        script_index = self.current_session.casual_script_index
        script_messages = self.current_session.casual_script_messages
        
        # Get the last user message to check for disinterest or recovery
        last_user_msg = ""
        if self.current_session.context.messages:
            for msg in reversed(self.current_session.context.messages):
                if msg.get('role') == 'user':
                    last_user_msg = msg.get('content', '').lower().strip()
                    break
        
        # Check if script was paused and user wants to continue
        if self.current_session.casual_script_paused:
            # Check for recovery phrases
            recovery_phrases = ["sorry", "continue", "keep going", "go on", "tell me", "finish", "no wait", 
                              "actually", "i want to hear", "please continue", "my bad", "go ahead"]
            wants_to_continue = any(phrase in last_user_msg for phrase in recovery_phrases)
            
            if wants_to_continue:
                print("💬 User wants to continue! Resuming story...")
                self.current_session.casual_script_paused = False
                
                # Send recovery message
                recovery_msg = "ok ill continue my story"
                from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
                script_energy = EnergySignature(
                    timestamp=time.time(),
                    energy_level=EnergyLevel.MEDIUM,
                    energy_type=EnergyType.COOPERATIVE,
                    dominant_emotion=EmotionState.HAPPY,
                    nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                    intensity_score=0.5,
                    confidence=0.9
                )
                
                response_message = {
                    "role": "agent",
                    "content": recovery_msg,
                    "timestamp": time.time(),
                    "energy_signature": script_energy,
                    "script_message": True,
                    "script_type": "casual_recovery"
                }
                self.current_session.context.messages.append(response_message)
                self.current_session.context.energy_history.append(script_energy)
                print(f"💬 Sent recovery message, will continue with message {script_index + 1} next")
                return
            else:
                # User confirmed they don't want to continue
                print("💬 User confirmed disinterest, ending casual script and generating follow-up...")
                self.current_session.casual_script_active = False
                self.current_session.casual_script_paused = False
                self.current_session.casual_script_index = 0
                self.energy_flags = {"status": "green", "reason": "Script ended due to user disinterest", "scene": "park"}
                
                # Generate a natural follow-up that moves on from the story
                print("💬 Generating post-disinterest response...")
                response_content, response_energy = await self.girlfriend_agent.generate_response(
                    self.current_session.context, 
                    last_user_msg if last_user_msg else "continue conversation naturally",
                    "green"
                )
                
                # Record response
                response_message = {
                    "role": "agent",
                    "content": response_content,
                    "timestamp": time.time(),
                    "energy_signature": response_energy,
                    "post_script": True
                }
                self.current_session.context.messages.append(response_message)
                self.current_session.context.energy_history.append(response_energy)
                
                print(f"✅ Post-disinterest response generated: {response_content[:100]}...")
                return
        
        # Check for disinterest signals (only after message 3, give them time to engage)
        if script_index >= 3 and not self.current_session.casual_script_paused:
            disinterest_signals = [
                "ok", "k", "cool", "nice", "meh", "whatever", "sure", "uh huh", "yeah", "yea",
                "i guess", "idk", "don't care", "boring", "not interested", "stop", "enough"
            ]
            # Check if response is very short and matches disinterest
            is_disinterested = (
                (len(last_user_msg) <= 10 and any(signal == last_user_msg for signal in disinterest_signals)) or
                any(signal in last_user_msg and len(last_user_msg) < 20 for signal in ["boring", "not interested", "don't care", "stop", "enough"])
            )
            
            if is_disinterested:
                print("💬 User seems disinterested, pausing casual script...")
                self.current_session.casual_script_paused = True
                
                # Send disinterest response
                disinterest_msg = "lol ok i will stop you dont seem interested in my story"
                from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
                script_energy = EnergySignature(
                    timestamp=time.time(),
                    energy_level=EnergyLevel.MEDIUM,
                    energy_type=EnergyType.COOPERATIVE,
                    dominant_emotion=EmotionState.HAPPY,
                    nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                    intensity_score=0.4,
                    confidence=0.9
                )
                
                response_message = {
                    "role": "agent",
                    "content": disinterest_msg,
                    "timestamp": time.time(),
                    "energy_signature": script_energy,
                    "script_message": True,
                    "script_type": "casual_pause"
                }
                self.current_session.context.messages.append(response_message)
                self.current_session.context.energy_history.append(script_energy)
                print(f"💬 Sent disinterest message, waiting for user response")
                return
        
        # Check if script is complete
        if script_index >= len(script_messages):
            print("\n✅ Casual story script completed! Generating follow-up response...")
            self.current_session.casual_script_active = False
            self.current_session.casual_script_index = 0
            self.energy_flags = {"status": "green", "reason": "Script completed, generating natural follow-up", "scene": "park"}
            
            # Generate a natural follow-up response that acknowledges the script
            # Get the last user message to respond to
            last_user_msg = ""
            if self.current_session.context.messages:
                for msg in reversed(self.current_session.context.messages):
                    if msg.get('role') == 'user':
                        last_user_msg = msg.get('content', '')
                        break
            
            # Generate AI response with full script context
            print("💬 Generating post-script response with full context...")
            response_content, response_energy = await self.girlfriend_agent.generate_response(
                self.current_session.context, 
                last_user_msg if last_user_msg else "continue conversation naturally",
                "green"
            )
            
            # Record response
            response_message = {
                "role": "agent",
                "content": response_content,
                "timestamp": time.time(),
                "energy_signature": response_energy,
                "post_script": True
            }
            self.current_session.context.messages.append(response_message)
            self.current_session.context.energy_history.append(response_energy)
            
            print(f"✅ Post-script response generated: {response_content[:100]}...")
            return
        
        # Get next message (can be string or list of strings for grouped messages)
        next_message_item = script_messages[script_index]
        
        # Handle both single messages and grouped messages
        messages_to_send = [next_message_item] if isinstance(next_message_item, str) else next_message_item
        
        from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
        
        # Send all messages in the group
        for i, msg in enumerate(messages_to_send):
            print(f"💬 [Casual Script Part {i+1}/{len(messages_to_send)}]: {msg[:50]}...")
            
            script_energy = EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel.MEDIUM,
                energy_type=EnergyType.COOPERATIVE,
                dominant_emotion=EmotionState.HAPPY,
                nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                intensity_score=0.5,
                confidence=0.9
            )
            
            # Add to context
            response_message = {
                "role": "agent",
                "content": msg,
                "timestamp": time.time(),
                "energy_signature": script_energy,
                "script_message": True,
                "script_type": "casual",
                "script_index": script_index,
                "group_part": i
            }
            self.current_session.context.messages.append(response_message)
            self.current_session.context.energy_history.append(script_energy)
        
        # Move to next message
        self.current_session.casual_script_index += 1
        
        if self.current_session.casual_script_index >= len(script_messages):
            print(f"✅ Final casual message sent - script will complete after this")
        else:
            print(f"✅ Will send message {self.current_session.casual_script_index + 1} after next user response")

    async def _trigger_casual_story_script(self):
        """Trigger the casual store story script using EnhancedScriptManager"""
        print("\n💬🛍️ Starting Casual Story Time...")
        print("=" * 60)
        
        # Option 1: Use specific scenario (shopping)
        scenario = self.script_manager.scenarios["shopping_scenario"]
        
        # Option 2: Let script manager auto-select based on user energy
        # user_energy = self.current_session.context.energy_history[-1] if self.current_session.context.energy_history else None
        # scenario = await self.script_manager.select_scenario(user_energy, self.current_session.context)
        
        print(f"📖 Selected Scenario: {scenario.name}")
        print(f"📝 Description: {scenario.description}")
        print(f"💬 Messages: {len(scenario.messages)}")
        
        # Convert scenario messages to simple string list
        # This uses the shopping_scenario from the script manager
        # Handle both single strings and grouped content
        casual_story_script = []
        for msg in scenario.messages:
            if isinstance(msg.content, list):
                casual_story_script.append(msg.content)  # Keep grouped messages as lists
            else:
                casual_story_script.append(msg.content)  # Single messages as strings
        
        # Initialize script state for frontend
        self.current_session.casual_script_active = True
        self.current_session.casual_script_messages = casual_story_script
        self.current_session.casual_script_index = 0
        
        # Send first message (handle both single and grouped)
        first_message_item = casual_story_script[0]
        messages_to_send = [first_message_item] if isinstance(first_message_item, str) else first_message_item
        
        # Create energy signature for the casual message
        from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
        
        # Send all messages in the first group
        for i, msg in enumerate(messages_to_send):
            print(f"💬 [Casual Script Init Part {i+1}/{len(messages_to_send)}]: {msg[:50]}...")
            
            script_energy = EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel.MEDIUM,
                energy_type=EnergyType.COOPERATIVE,
                dominant_emotion=EmotionState.HAPPY,
                nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                intensity_score=0.5,
                confidence=0.9
            )
            
            # Add to context
            response_message = {
                "role": "agent",
                "content": msg,
                "timestamp": time.time(),
                "energy_signature": script_energy,
                "script_message": True,
                "script_type": "casual",
                "script_index": 0,
                "group_part": i
            }
            self.current_session.context.messages.append(response_message)
            self.current_session.context.energy_history.append(script_energy)
        
        self.current_session.casual_script_index = 1  # Move to next message
        
        print(f"✅ Casual script initialized - will continue with message 2 after user responds")

    async def _trigger_guided_intimacy_script(self):
        """Trigger the guided intimacy script - first ask for location preference"""
        print("\n🔥💕 Initiating Guided Intimacy Experience...")
        print("=" * 60)
        
        # Set flag to await location choice
        self.current_session.awaiting_location_choice = True
        
        # Keep energy flags as sexual but don't specify type yet - wait for location confirmation
        self.energy_flags = {"status": "sexual", "reason": "Awaiting location choice"}
        
        # Create energy signature for location question
        from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
        script_energy = EnergySignature(
            timestamp=time.time(),
            energy_level=EnergyLevel.MEDIUM,
            energy_type=EnergyType.INTIMATE,
            dominant_emotion=EmotionState.EXCITED,
            nervous_system_state=NervousSystemState.REST_AND_DIGEST,
            intensity_score=0.7,
            confidence=0.95
        )
        
        # Ask for location preference
        location_question = [
            "Mmm I can feel your energy baby 🔥",
            "Before we start... Lets go somewhere private? Maybe in your room love, or maybe youre thinking somewhere more... exciting? 😈"
        ]
        
        # Send both parts of the question
        for part in location_question:
            response_message = {
                "role": "agent",
                "content": part,
                "timestamp": time.time(),
                "energy_signature": script_energy,
                "group_part": True
            }
            self.current_session.context.messages.append(response_message)
            self.current_session.context.energy_history.append(script_energy)
            print(f"🔥 Location question: {part}")
        
        print(f"⏳ Waiting for user's location choice (room/public/outside)...")

    async def _handle_location_choice(self, user_input: str):
        """Handle user's location choice and start appropriate sexual script"""
        user_response = user_input.lower()
        
        # Reset awaiting flag
        self.current_session.awaiting_location_choice = False
        
        # Detect location from user response
        if any(word in user_response for word in ["room", "bedroom", "bed", "home", "private", "alone"]):
            print("🏠 Location chosen: ROOM - Starting intimate bedroom script")
            self.current_session.sexual_script_type = "room"
            await self._start_room_intimacy_script()
        elif any(word in user_response for word in ["public", "outside", "park", "car", "store", "shop", "bus", "train", "street", "restaurant", "bathroom", "beach", "forest"]):
            print("🌆 Location chosen: PUBLIC - Starting exhibitionism script")
            self.current_session.sexual_script_type = "exhibitionism"
            await self._start_exhibitionism_script()
        else:
            # Default to room if unclear
            print("🏠 Location unclear - Defaulting to room script")
            self.current_session.sexual_script_type = "room"
            await self._start_room_intimacy_script()

    async def _start_room_intimacy_script(self):
        """Start the private room intimacy script using Script Manager"""
        from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
        
        # Update energy flags to indicate room script with scene
        self.energy_flags = {"status": "sexual", "reason": "Room intimacy script active", "scene": "room"}
        
        # Get room intimacy scenario from script manager
        scenario = self.script_manager.scenarios["room_intimacy_scenario"]
        print(f"📖 Selected Scenario: {scenario.name}")
        print(f"📝 Description: {scenario.description}")
        print(f"💬 Messages: {len(scenario.messages)}")
        
        # Convert scenario messages to script format
        # Each ScenarioMessage.content is already properly formatted (string or list)
        room_script = [msg.content for msg in scenario.messages]
        
        # Initialize script
        self.current_session.sexual_script_active = True
        self.current_session.sexual_script_messages = room_script
        self.current_session.sexual_script_index = 0
        
        # Send first message (can be grouped)
        first_message_item = room_script[0]
        script_energy = EnergySignature(
            timestamp=time.time(),
            energy_level=EnergyLevel.MEDIUM,
            energy_type=EnergyType.INTIMATE,
            dominant_emotion=EmotionState.EXCITED,
            nervous_system_state=NervousSystemState.REST_AND_DIGEST,
            intensity_score=0.7,
            confidence=0.95
        )
        
        # Handle grouped vs single messages - ALWAYS WAIT AFTER EACH ScenarioMessage
        if isinstance(first_message_item, list):
            # Collect all parts first, then mark completion on the last one
            for part_idx, part in enumerate(first_message_item):
                response_message = {
                    "role": "agent",
                    "content": part,
                    "timestamp": time.time(),
                    "energy_signature": script_energy,
                    "script_message": True,
                    "group_part": True,
                    "script_message_complete": part_idx == len(first_message_item) - 1  # Only last part gets complete flag
                }
                self.current_session.context.messages.append(response_message)
            
            # Now mark the entire group as ready for streaming
            print(f"🔥 [Room Script Group 1/{len(room_script)}]: {len(first_message_item)} parts COLLECTED - READY FOR API STREAMING")
        else:
            response_message = {
                "role": "agent",
                "content": first_message_item,
                "timestamp": time.time(),
                "energy_signature": script_energy,
                "script_message": True,
                "script_message_complete": True  # Single message is immediately complete
            }
            self.current_session.context.messages.append(response_message)
            print(f"🔥 [Room Script 1/{len(room_script)}]: {first_message_item[:50]}... - WAITING FOR USER INPUT")
        
        self.current_session.context.energy_history.append(script_energy)
        # DON'T increment index yet - wait for user input first
        # BUT ensure we don't repeat the same message on continuation
        if self.current_session.sexual_script_index == 0:
            self.current_session.sexual_script_index = 1
        print(f"✅ Room intimacy script started - {len(room_script)} messages")

    async def _start_exhibitionism_script(self):
        """Start the exhibitionism/public script using Script Manager"""
        from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
        
        # Detect if beach is mentioned in recent context
        recent_messages = [msg.get("content", "").lower() for msg in self.current_session.context.messages[-3:]]
        has_beach = any("beach" in msg for msg in recent_messages)
        scene = "beach" if has_beach else "park"
        
        # Update energy flags to indicate exhibitionism script with appropriate scene
        self.energy_flags = {"status": "sexual", "reason": "Exhibitionism script active - public setting", "scene": scene}
        
        # Get exhibitionism scenario from script manager
        scenario = self.script_manager.scenarios["exhibitionism_scenario"]
        print(f"📖 Selected Scenario: {scenario.name}")
        print(f"📝 Description: {scenario.description}")
        print(f"💬 Messages: {len(scenario.messages)}")
        
        # Convert scenario messages to script format
        # Each ScenarioMessage.content is already properly formatted (string or list)
        exhib_script = [msg.content for msg in scenario.messages]
        
        # Initialize script
        self.current_session.sexual_script_active = True
        self.current_session.sexual_script_messages = exhib_script
        self.current_session.sexual_script_index = 0
        
        # Send first message (can be grouped)
        first_message_item = exhib_script[0]
        script_energy = EnergySignature(
            timestamp=time.time(),
            energy_level=EnergyLevel.MEDIUM,
            energy_type=EnergyType.INTIMATE,
            dominant_emotion=EmotionState.EXCITED,
            nervous_system_state=NervousSystemState.FIGHT,  # Fight response for risky behavior
            intensity_score=0.75,
            confidence=0.95
        )
        
        # Handle grouped vs single messages
        if isinstance(first_message_item, list):
            for part in first_message_item:
                response_message = {
                    "role": "agent",
                    "content": part,
                    "timestamp": time.time(),
                    "energy_signature": script_energy,
                    "script_message": True,
                    "group_part": True
                }
                self.current_session.context.messages.append(response_message)
            print(f"🌆 [Exhibitionism Script 1/{len(exhib_script)}]: {first_message_item[0][:50]}...")
        else:
            response_message = {
                "role": "agent",
                "content": first_message_item,
                "timestamp": time.time(),
                "energy_signature": script_energy,
                "script_message": True
            }
            self.current_session.context.messages.append(response_message)
            print(f"🌆 [Exhibitionism Script 1/{len(exhib_script)}]: {first_message_item[:50]}...")
        
        self.current_session.context.energy_history.append(script_energy)
        self.current_session.sexual_script_index = 1
        print(f"✅ Exhibitionism script started - {len(exhib_script)} messages")

    async def _switch_scenario(self, scenario_name: str):
        """Switch to different scenario"""
        if scenario_name in self.script_manager.scenarios:
            old_scenario = self.current_session.current_scenario.name if self.current_session.current_scenario else "None"
            self.current_session.current_scenario = self.script_manager.scenarios[scenario_name]
            self.current_session.scenario_index = 0

            print(f"\n🔄 Switching scenario: {old_scenario} → {scenario_name}")
            await self._send_scenario_message()

    async def _complete_scenario(self):
        """Complete current scenario"""
        if self.current_session and self.current_session.current_scenario:
            success = await self.script_manager.check_scenario_success(
                self.current_session.current_scenario,
                self.current_session.context
            )

            self.current_session.state = ConversationState.COMPLETED

            print("✅ Scenario completed!")   
            print(f"📊 Success rate: {success['achieved']}")
            if success["criteria_met"]:
                print(f"✅ Criteria met: {', '.join(success['criteria_met'])}")
            if success["criteria_failed"]:
                print(f"❌ Criteria failed: {', '.join(success['criteria_failed'])}")
            if success["recommendations"]:
                print(f"💡 Recommendations: {', '.join(success['recommendations'])}")

    async def _end_session(self, reason: str):
        """End current session"""
        if self.current_session:
            self.current_session.state = ConversationState.STOPPED
            print(f"\n👋 Session ended: {reason}")

    async def get_session_metrics(self) -> Dict[str, Any]:
        """Get comprehensive session metrics"""
        if not self.current_session:
            return {"error": "No active session"}

        metrics = {
            "session_id": self.current_session.session_id,
            "duration": time.time() - self.current_session.start_time,
            "message_count": len(self.current_session.context.messages),
            "energy_alerts": len(self.current_session.energy_alerts),
            "safety_incidents": len(self.current_session.safety_incidents),
            "avg_energy_intensity": sum(sig.intensity_score for sig in self.current_session.context.energy_history) / max(1, len(self.current_session.context.energy_history)),
            "dominant_emotions": {},
            "energy_trends": {}
        }

        # Count dominant emotions
        emotion_counts = {}
        for sig in self.current_session.context.energy_history:
            emotion = sig.dominant_emotion.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        metrics["dominant_emotions"] = emotion_counts

        # Energy trends
        if self.current_session.context.energy_history:
            recent_energies = [sig for sig in self.current_session.context.energy_history[-10:] if sig is not None]
            if recent_energies:
                metrics["energy_trends"] = {
                    "trend": "increasing" if recent_energies[-1].intensity_score > recent_energies[0].intensity_score else "decreasing",
                    "current_level": recent_energies[-1].energy_level.value,
                    "peak_intensity": max(sig.intensity_score for sig in recent_energies),
                    "avg_intensity": sum(sig.intensity_score for sig in recent_energies) / len(recent_energies)
                }

        return metrics

# Global conversation instance - lazy initialization
conversation_system = None

def get_conversation_system():
    """Get or create the conversation system"""
    global conversation_system
    if conversation_system is None:
        conversation_system = EnhancedMultiAgentConversation()
    return conversation_system

async def main():
    """Main conversation loop"""
    system = get_conversation_system()
    session_id = await system.start_new_session()

    try:
        while system.current_session and system.current_session.state == ConversationState.ACTIVE:
            user_input = input().strip()

            if user_input.lower() in ['quit', 'exit', 'stop']:
                print("👋 Goodbye!")
                break

            if user_input.lower() == 'metrics':
                metrics = await system.get_session_metrics()
                print(f"\n📊 Session Metrics: {json.dumps(metrics, indent=2)}")
                print("💬 You: ", end="", flush=True)
                continue

            await system.process_user_response(user_input)

    except KeyboardInterrupt:
        print("\n👋 Conversation interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Show final metrics
        if system.current_session:
            metrics = await system.get_session_metrics()
            print(f"\n📊 Final Session Metrics: {json.dumps(metrics, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
