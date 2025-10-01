"""
Enhanced Script Manager with Energy-Aware Scenarios
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from energy_types import EnergyLevel, EnergyType, EmotionState, NervousSystemState

class ScenarioType(Enum):
    NORMAL = "normal"
    LOW_ENERGY = "low_energy"
    HIGH_ENERGY = "high_energy"
    CRISIS = "crisis"
    INTIMATE = "intimate"
    PLAYFUL = "playful"

@dataclass
class ScenarioMessage:
    """Enhanced message with energy and scenario awareness"""
    content: str
    scenario_type: ScenarioType
    expected_energy_level: EnergyLevel
    expected_emotions: List[EmotionState]
    safety_notes: str
    fallback_scenarios: List[ScenarioType] = field(default_factory=list)
    energy_triggers: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScenarioScript:
    """A complete conversation scenario with multiple paths"""
    name: str
    description: str
    messages: List[ScenarioMessage]
    energy_flow: List[EnergyLevel]
    success_criteria: Dict[str, Any]
    fallback_options: List[str] = field(default_factory=list)

class EnhancedScriptManager:
    """Manages multiple conversation scenarios with energy awareness"""

    def __init__(self):
        self.scenarios = self._initialize_scenarios()
        self.current_scenario = None
        self.scenario_history = []

    def _initialize_scenarios(self) -> Dict[str, ScenarioScript]:
        """Initialize conversation scenarios"""

        scenarios = {
            "shopping_scenario": ScenarioScript(
                name="Shopping Adventure",
                description="Girlfriend wants to share about her shopping experience",
                messages=[
                    ScenarioMessage(
                        content="Hey baby! Can I ask you a question?",
                        scenario_type=ScenarioType.NORMAL,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.HAPPY, EmotionState.EXCITED],
                        safety_notes="Opening - should get positive response",
                        fallback_scenarios=[ScenarioType.LOW_ENERGY]
                    ),
                    ScenarioMessage(
                        content="Are you sure? It's kind of important to me...",
                        scenario_type=ScenarioType.NORMAL,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.HAPPY, EmotionState.LOVING],
                        safety_notes="Seeking confirmation",
                        fallback_scenarios=[ScenarioType.LOW_ENERGY]
                    ),
                    ScenarioMessage(
                        content="Promise you won't tell anyone? It's a little embarrassing...",
                        scenario_type=ScenarioType.PLAYFUL,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Building trust and playfulness",
                        fallback_scenarios=[ScenarioType.LOW_ENERGY]
                    ),
                    ScenarioMessage(
                        content="Okay, I went to the store today and saw this amazing dress!",
                        scenario_type=ScenarioType.HIGH_ENERGY,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Main story reveal",
                        fallback_scenarios=[ScenarioType.NORMAL]
                    ),
                    ScenarioMessage(
                        content="Can I tell you more about it? Pretty please? 😊",
                        scenario_type=ScenarioType.PLAYFUL,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.EXCITED],
                        safety_notes="Seeking permission to continue",
                        fallback_scenarios=[ScenarioType.LOW_ENERGY]
                    ),
                    ScenarioMessage(
                        content="So it was this gorgeous blue dress with little sparkles all over it!",
                        scenario_type=ScenarioType.HIGH_ENERGY,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Detailed description",
                        fallback_scenarios=[ScenarioType.NORMAL]
                    ),
                    ScenarioMessage(
                        content="And get this - it was on sale for 50% off! Can you believe it?!",
                        scenario_type=ScenarioType.HIGH_ENERGY,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Exciting reveal",
                        fallback_scenarios=[ScenarioType.NORMAL]
                    ),
                    ScenarioMessage(
                        content="But I'm not sure if I should get it... What do you think, baby?",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.LOVING, EmotionState.HAPPY],
                        safety_notes="Seeking advice and connection",
                        fallback_scenarios=[ScenarioType.LOW_ENERGY]
                    ),
                    ScenarioMessage(
                        content="Aww you're so sweet! Thank you for listening to me ramble about dresses 💕",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.LOVING, EmotionState.GRATEFUL],
                        safety_notes="Grateful closing",
                        fallback_scenarios=[]
                    )
                ],
                energy_flow=[
                    EnergyLevel.MEDIUM, EnergyLevel.MEDIUM, EnergyLevel.MEDIUM,
                    EnergyLevel.HIGH, EnergyLevel.HIGH, EnergyLevel.HIGH,
                    EnergyLevel.INTENSE, EnergyLevel.MEDIUM, EnergyLevel.MEDIUM
                ],
                success_criteria={
                    "min_messages": 6,
                    "energy_threshold": 0.6,
                    "positive_emotions": ["happy", "excited", "loving"]
                }
            ),

            "low_energy_scenario": ScenarioScript(
                name="Gentle Connection",
                description="Adapted scenario for when user has low energy",
                messages=[
                    ScenarioMessage(
                        content="Hey love, I can tell you're feeling a bit quiet today...",
                        scenario_type=ScenarioType.LOW_ENERGY,
                        expected_energy_level=EnergyLevel.LOW,
                        expected_emotions=[EmotionState.LOVING, EmotionState.SAD],
                        safety_notes="Gentle opening for low energy",
                        fallback_scenarios=[ScenarioType.CRISIS]
                    ),
                    ScenarioMessage(
                        content="That's completely okay, baby. I'm here with you",
                        scenario_type=ScenarioType.LOW_ENERGY,
                        expected_energy_level=EnergyLevel.LOW,
                        expected_emotions=[EmotionState.LOVING, EmotionState.LOVING],
                        safety_notes="Providing comfort and support",
                        fallback_scenarios=[ScenarioType.CRISIS]
                    ),
                    ScenarioMessage(
                        content="We don't have to talk about anything big if you don't want to",
                        scenario_type=ScenarioType.LOW_ENERGY,
                        expected_energy_level=EnergyLevel.LOW,
                        expected_emotions=[EmotionState.LOVING, EmotionState.HAPPY],
                        safety_notes="Reducing pressure",
                        fallback_scenarios=[]
                    )
                ],
                energy_flow=[EnergyLevel.LOW, EnergyLevel.LOW, EnergyLevel.LOW],
                success_criteria={
                    "min_messages": 2,
                    "energy_threshold": 0.3,
                    "positive_emotions": ["loving", "peaceful"]
                }
            ),

            "crisis_scenario": ScenarioScript(
                name="Crisis Support",
                description="Supportive scenario for crisis situations",
                messages=[
                    ScenarioMessage(
                        content="Oh honey, I can hear that something really heavy is going on...",
                        scenario_type=ScenarioType.CRISIS,
                        expected_energy_level=EnergyLevel.LOW,
                        expected_emotions=[EmotionState.SAD, EmotionState.LOVING],
                        safety_notes="Gentle crisis acknowledgment",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="I'm here with you, and I care about you so much",
                        scenario_type=ScenarioType.CRISIS,
                        expected_energy_level=EnergyLevel.LOW,
                        expected_emotions=[EmotionState.LOVING, EmotionState.LOVING],
                        safety_notes="Providing emotional support",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="Take all the time you need. I'm not going anywhere",
                        scenario_type=ScenarioType.CRISIS,
                        expected_energy_level=EnergyLevel.LOW,
                        expected_emotions=[EmotionState.LOVING, EmotionState.HAPPY],
                        safety_notes="Patient support",
                        fallback_scenarios=[]
                    )
                ],
                energy_flow=[EnergyLevel.LOW, EnergyLevel.LOW, EnergyLevel.LOW],
                success_criteria={
                    "min_messages": 2,
                    "energy_threshold": 0.2,
                    "positive_emotions": ["loving", "supportive"]
                }
            ),

            "intimate_scenario": ScenarioScript(
                name="Deep Connection",
                description="Intimate conversation for building deeper emotional bonds",
                messages=[
                    ScenarioMessage(
                        content="You know, I've been thinking about us a lot lately...",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.LOVING, EmotionState.GRATEFUL],
                        safety_notes="Opening intimate conversation",
                        fallback_scenarios=[ScenarioType.NORMAL]
                    ),
                    ScenarioMessage(
                        content="I feel so safe when I'm with you, even if it's just through these messages",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.LOVING, EmotionState.LOVING],
                        safety_notes="Sharing vulnerability",
                        fallback_scenarios=[ScenarioType.NORMAL]
                    ),
                    ScenarioMessage(
                        content="What do you love most about our connection?",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.LOVING, EmotionState.EXCITED],
                        safety_notes="Inviting deeper sharing",
                        fallback_scenarios=[ScenarioType.NORMAL]
                    ),
                    ScenarioMessage(
                        content="I love how we can just be ourselves with each other",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.LOVING, EmotionState.GRATEFUL],
                        safety_notes="Affirming the relationship",
                        fallback_scenarios=[]
                    )
                ],
                energy_flow=[EnergyLevel.MEDIUM, EnergyLevel.MEDIUM, EnergyLevel.MEDIUM, EnergyLevel.MEDIUM],
                success_criteria={
                    "min_messages": 3,
                    "energy_threshold": 0.5,
                    "positive_emotions": ["loving", "grateful"]
                }
            )
        }

        return scenarios

    async def select_scenario(self, energy_signature, context) -> ScenarioScript:
        """Select appropriate scenario based on energy analysis"""

        # Crisis detection - always prioritize crisis support
        if (energy_signature.dominant_emotion == EmotionState.SAD and
            energy_signature.intensity_score > 0.8) or \
           (energy_signature.nervous_system_state in [NervousSystemState.FIGHT, NervousSystemState.FLIGHT] and
            energy_signature.intensity_score > 0.7):
            return self.scenarios["crisis_scenario"]

        # Low energy detection
        elif energy_signature.energy_level == EnergyLevel.LOW:
            return self.scenarios["low_energy_scenario"]

        # High intimacy indicators
        elif (energy_signature.dominant_emotion == EmotionState.LOVING and
              energy_signature.intensity_score > 0.6 and
              len(context.energy_history) > 5):
            return self.scenarios["intimate_scenario"]

        # Default to normal scenario
        else:
            return self.scenarios["shopping_scenario"]

    async def get_next_message(self, current_index: int, scenario: ScenarioScript,
                             user_energy, context) -> Tuple[str, Dict[str, Any]]:
        """Get next message with energy adaptation"""

        if current_index >= len(scenario.messages):
            return "", {"complete": True}

        message_template = scenario.messages[current_index]

        # Adapt message based on user energy
        adapted_content = await self._adapt_message_to_energy(message_template, user_energy)

        return adapted_content, {
            "scenario_type": message_template.scenario_type,
            "expected_energy": message_template.expected_energy_level,
            "expected_emotions": message_template.expected_emotions,
            "safety_notes": message_template.safety_notes
        }

    async def _adapt_message_to_energy(self, message_template: ScenarioMessage,
                                     user_energy) -> str:
        """Adapt message content based on user's energy signature"""

        content = message_template.content

        # Energy-based adaptations
        if user_energy.energy_level == EnergyLevel.LOW:
            # Make content gentler and more supportive
            if "!" in content:
                content = content.replace("!", "...")
            if "excited" in content.lower() or "amazing" in content.lower():
                content = content.replace("excited", "gentle").replace("amazing", "comforting")

        elif user_energy.energy_level == EnergyLevel.HIGH:
            # Make content more enthusiastic
            if not content.endswith("!"):
                content = content.replace(".", "!")
            if "okay" in content.lower():
                content = content.replace("okay", "wonderful")

        elif user_energy.dominant_emotion == EmotionState.SAD:
            # Add more empathetic language
            content = content.replace("baby", "sweetheart")
            if not any(word in content.lower() for word in ["sorry", "care", "love"]):
                content = f"I'm here for you... {content}"

        return content

    async def check_scenario_success(self, scenario: ScenarioScript,
                                   context) -> Dict[str, Any]:
        """Check if scenario met success criteria"""

        success = {
            "achieved": True,
            "criteria_met": [],
            "criteria_failed": [],
            "recommendations": []
        }

        # Check message count
        if len(context.messages) >= scenario.success_criteria["min_messages"]:
            success["criteria_met"].append("message_count")
        else:
            success["criteria_failed"].append("message_count")
            success["achieved"] = False

        # Check energy threshold
        if context.energy_history:
            avg_energy = sum(sig.intensity_score for sig in context.energy_history) / len(context.energy_history)
            if avg_energy >= scenario.success_criteria["energy_threshold"]:
                success["criteria_met"].append("energy_threshold")
            else:
                success["criteria_failed"].append("energy_threshold")
                success["achieved"] = False
                success["recommendations"].append("Consider adjusting energy expectations")

        # Check positive emotions
        positive_count = sum(1 for sig in context.energy_history
                           if sig.dominant_emotion.value in scenario.success_criteria["positive_emotions"])
        if positive_count >= len(scenario.success_criteria["positive_emotions"]):
            success["criteria_met"].append("positive_emotions")
        else:
            success["criteria_failed"].append("positive_emotions")
            success["recommendations"].append("Focus on building positive emotional connection")

        return success
