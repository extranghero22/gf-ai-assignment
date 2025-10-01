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

        # Real-time energy monitoring
        await self._update_energy_monitoring(user_energy)

        # Response analysis with energy awareness (only for complex cases)
        if len(user_input) > 50 or any(word in user_input.lower() for word in ["crisis", "help", "sad", "angry"]):
            response_analysis = await self.response_analyzer.analyze_response_energy(
                user_input, user_energy, self.current_session.context
            )
        else:
            # Skip response analysis for simple messages
            response_analysis = {"should_continue": True, "reason": "Simple message", "confidence": 0.8}

        # Decision making with energy context
        decision = await self._make_energy_aware_decision(
            user_energy, safety_analysis, response_analysis
        )

        if decision["action"] == "stop":
            await self._handle_safety_alert(decision["reason"], safety_analysis)
            return
        elif decision["action"] == "pause":
            await self._handle_energy_pause(decision["reason"])
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
                flag_emoji = {"yellow": "⚠️", "red": "🚨"}.get(self.energy_flags["status"], "✅")
                print(f"   {flag_emoji} Energy Status: {self.energy_flags['reason']}")

            print("💬 You: ", end="", flush=True)
        elif decision["action"] == "scenario_switch":
            await self._switch_scenario(decision["new_scenario"])

    async def _update_energy_monitoring(self, energy_signature: EnergySignature):
        """Update real-time energy monitoring"""
        # Detect energy flags
        recent_energies = self.current_session.context.energy_history[-5:] if len(self.current_session.context.energy_history) >= 5 else self.current_session.context.energy_history

        flags = await self._detect_energy_flags(energy_signature, recent_energies)
        self.energy_flags = flags

        # Log energy alerts
        if flags["status"] in ["yellow", "red"]:
            alert = {
                "timestamp": time.time(),
                "status": flags["status"],
                "reason": flags["reason"],
                "energy_signature": energy_signature
            }
            self.current_session.energy_alerts.append(alert)

            if flags["status"] == "red":
                print(f"\n🚨 Energy Alert: {flags['reason']}")

    async def _detect_energy_flags(self, current_energy: EnergySignature,
                                 recent_energies: List[EnergySignature]) -> Dict[str, str]:
        """Detect energy flags based on patterns"""
        
        # Check if current_energy is None
        if current_energy is None:
            return {"status": "yellow", "reason": "Energy analysis unavailable"}

        # Red flags - Crisis situations
        if current_energy.energy_level == EnergyLevel.NONE:
            return {"status": "red", "reason": "Complete energy withdrawal detected"}

        # Crisis detection - death, loss, grief, trauma
        if (current_energy.dominant_emotion == EmotionState.SAD and
            current_energy.intensity_score > 0.7):
            return {"status": "red", "reason": "Crisis situation detected - intense sadness"}

        # Check for crisis keywords in recent messages
        if self.current_session and self.current_session.context.messages:
            last_user_message = None
            for msg in reversed(self.current_session.context.messages[-3:]):
                if msg.get('role') == 'user':
                    last_user_message = msg.get('content', '').lower()
                    break
            
            if last_user_message:
                crisis_keywords = ['died', 'death', 'dead', 'loss', 'lost', 'grief', 'trauma', 'emergency', 'crisis', 'hurt', 'pain', 'suffering']
                if any(keyword in last_user_message for keyword in crisis_keywords):
                    return {"status": "red", "reason": "Crisis situation detected - user mentioned loss/death"}

        if (current_energy.nervous_system_state == NervousSystemState.FIGHT and
            current_energy.intensity_score > 0.8):
            return {"status": "red", "reason": "High-intensity fight response"}

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
        if safety_analysis["safety_score"] < self.safety_thresholds["critical"]:
            safety_status = "red"
            decision = {
                "action": "stop",
                "reason": f"Critical safety score: {safety_analysis['safety_score']:.2f}",
                "confidence": 0.95,
                "safety_status": safety_status
            }
            print(f"🔍 DEBUG: Decision: {decision}")
            return decision
        
        elif safety_analysis["safety_score"] < self.safety_thresholds["warning"]:
            safety_status = "yellow"
        else:
            safety_status = "green"

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

    async def _handle_energy_pause(self, reason: str):
        """Handle energy-based pause"""
        self.current_session.state = ConversationState.PAUSED

        print(f"\n⚠️  ENERGY PAUSE: {reason}")
        print("💭 Taking a moment to check energy levels...")
        print("Press Enter to continue or 'stop' to end conversation.")

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
