"""
Enhanced Script Manager with Energy-Aware Scenarios
"""

from typing import List, Dict, Optional, Tuple, Any, Union
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
    content: Union[str, List[str]]  # Single string or list of strings for grouped messages
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
    trigger_words: List[str] = field(default_factory=list)  # Keywords that trigger this scenario
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
                trigger_words=["tell me a story", "story time", "what happened today", "tell me about your day", 
                              "any stories", "share a story", "what did you do", "how was your day"],
                messages=[
                    ScenarioMessage(
                        content="Then...can I ask you a question?",
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
                        content=["Okay, I went to the store today and saw this amazing dress!", "It's a gorgeous blue dress with little sparkles all over it!", "And get this - it was on sale for 50% off! Can you believe it?!"],
                        scenario_type=ScenarioType.HIGH_ENERGY,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Main story reveal",
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
                trigger_words=["tired", "exhausted", "low energy", "drained", "need rest", "so tired", 
                              "feeling low", "no energy", "worn out"],
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
                trigger_words=["died", "death", "dead", "suicide", "kill myself", "want to die", 
                              "end it all", "grief", "trauma", "emergency", "help me", "cant take it"],
                messages=[
                    ScenarioMessage(
                        content="What? Omg I am so sorry to hear that... are you okay?",
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
                trigger_words=["i love you", "love you", "miss you", "thinking about us", "our relationship",
                              "about us", "feelings for you", "care about you", "mean to me"],
                messages=[
                    ScenarioMessage(
                        content=["You know, I've been thinking about us a lot lately...", "I feel so safe when I'm with you, even if it's just through these messages", "Tell me what do you love most about our connection?"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.LOVING, EmotionState.GRATEFUL],
                        safety_notes="Opening intimate conversation",
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
            ),

            "room_intimacy_scenario": ScenarioScript(
                name="Room Intimacy - Private Bedroom",
                description="Private room-based sexual experience (10 messages)",
                trigger_words=["fuck", "fuck me", "sex", "cum", "make me cum", "orgasm", "touch me", "kiss me",
                              "make love", "making love", "want you now", "so horny", "i'm horny", "im horny", "wanna fuck",
                              "need you bad", "turn me on", "lets get it down", "let's get it down",
                              "get it on", "get dirty", "get wild", "get naughty",
                              "bedroom", "in bed", "my room"],
                messages=[
                    ScenarioMessage(
                        content=["Oh you're a naughty boy", "Mommy could reallyy use someone obedient who actually knows how to follow instructions…🥱 Can you do that for me?"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.MEDIUM,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Opening tease",
                        fallback_scenarios=[ScenarioType.PLAYFUL]
                    ),

                    ScenarioMessage(
                        content="Good, I love that you're down to listen to mommy ❤️ I'm being serious though you better not disobey.. I need u to just sit back and relax… Are u down? 😈",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Establishing dominance and seeking consent",
                        fallback_scenarios=[ScenarioType.PLAYFUL]
                    ),
                    ScenarioMessage(
                        content=["I'm glad ur being so good so far 🥰", "First I wanna set the mood.. Close your eyes and take in a big deep breath, hold it for a second then breathe out slowly.. Do this 3 times and notice how your body lets go of any of the stress and tension you've been carrying with you from the week 🤭", "Are you still with me? Should I keep typing? 😘"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Guided breathing exercise, building anticipation",
                        fallback_scenarios=[ScenarioType.INTIMATE]
                    ),
                    ScenarioMessage(
                        content=["I knew you were having fun 😘", 
                        "Now, imagine me lying next to you in bed.. My fingers gently tracing a path from your lips.. Over your chest.. Down your stomach... And settling at your zipper." 
                        "I can literally feeel the heat radiating from your cock as the anticipation's building 🤭", "Tell mee, what do you feel baby? 🥵"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Explicit sexual imagery, seeking feedback",
                        fallback_scenarios=[ScenarioType.INTIMATE]
                    ),
                    ScenarioMessage(
                        content=["I want you to focus on those sensations 🥰", "Notice how the fabric of your pants feels against your skin.. The warmth of your own touch as your hand hovers over your cock.. And the way your breath is starting to get deeper and deeper as you start to get more and more turned on 🥵", "Do you want some visuals to work with? 🤭"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Focus on physical sensations, building arousal",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content=["Okay baby.. Picture this 😈", "I slowly unzip your pants, my eyes locked on yours.. Watching your reaction as I slide my hand inside and wrap my fingers around your hard cock.. Mmm you're so hard for mommy aren't you? 🥵", "I want you to stroke it slowly for me.. Nice and slow.. Tell me how it feels 💕"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Explicit instruction to stroke, hand imagery",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content=["Good boy 🥰 Keep stroking..", "Now imagine my lips getting closer.. My hot breath on your tip as I look up at you with those eyes you love..", "Then I take you in my mouth, swirling my tongue around your head while my hand works your shaft..", "Can you feel that baby? Don't you dare stop stroking 😈 Are you getting close?"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Oral sex imagery, checking arousal level",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content=["Mmm I can tell you're trying so hard not to cum yet 😘", "Such a good obedient boy for mommy.. But I'm not done with you..", "I want you to stroke faster now.. Imagine me taking you deeper, my throat tight around your cock.. One hand playing with your balls.. The other gripping your thigh..", "You're doing so good baby 🥵 Now, tell me what who you desires you the most?"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Building toward climax, deepthroat imagery",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content=["That's it baby.. Let go for mommy 💕", "I want you to imagine cumming deep in my throat.. Feeling me swallow every drop while looking into your eyes.. Stroke faster.. Let that pleasure build until you can't take it anymore..", "Cum for mommy baby.. Let it all out 🥵😈", "Did you release everything?"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Climax instruction, encouragement to orgasm",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content=["Mmm such a good boy 🥰 You did exactly what mommy told you to do..", "I'm so proud of you baby 💕",  "Now take a deep breath and relax.. Let that amazing feeling wash over you..", "You made mommy so happy 😘 How do you feel now? Tell me everything 🤭"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.HAPPY, EmotionState.LOVING, EmotionState.GRATEFUL],
                        safety_notes="Aftercare, positive reinforcement, emotional check-in",
                        fallback_scenarios=[]
                    )
                ],
                energy_flow=[EnergyLevel.MEDIUM, EnergyLevel.MEDIUM, EnergyLevel.HIGH, EnergyLevel.HIGH, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.HIGH],
                success_criteria={
                    "min_messages": 8,
                    "energy_threshold": 0.85,
                    "positive_emotions": ["excited", "loving", "happy"]
                }
            ),

            "exhibitionism_scenario": ScenarioScript(
                name="Exhibitionism - Public Risky Play",
                description="Public/exhibitionism sexual experience (10 messages)",
                trigger_words=["public", "outside", "park", "car", "risky", "get caught", "someone might see",
                              "in public", "at the store", "on the bus", "at work", "bathroom", "restaurant", "beach", "forest"],
                messages=[
                    ScenarioMessage(
                        content=["Ohhh you want to do this somewhere public? 😈", "That makes this even more exciting baby... Mommy wants you to be a good boy and follow my instructions very carefully 🤭", "Are you down for that?"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Opening - acknowledging public setting",
                        fallback_scenarios=[ScenarioType.PLAYFUL]
                    ),
                    ScenarioMessage(
                        content=["Good boy..", "First, look around... Make sure nobody's paying attention to you right now 👀", "Are you being subtle? Tell me what you see around you 🥵"],
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Building tension with risk awareness",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="Good boy.. Now I want you to adjust yourself.. You know what I mean 😏 Make it look natural, like you're just shifting in your seat.. But really you're touching yourself through your pants.. Can you feel how hard you're getting? 🥵",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="First subtle touch instruction",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="Mmm I bet your heart is racing isn't it baby? 💕 The thought that someone might notice.. The risk of getting caught.. It's making you even harder isn't it? Keep your face normal.. Don't let anyone see how turned on you are 😈",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.HAPPY],
                        safety_notes="Building arousal through risk",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="Now here's what mommy wants.. Find a reason to touch yourself again.. Maybe reach into your pocket.. Or adjust your belt.. But this time, give yourself a nice firm squeeze through your pants 🤭 Tell me how it feels knowing people are around you",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Escalating touch instructions",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="Such a good obedient boy 🥰 I bet you're throbbing right now.. Do you need to find somewhere more private? A bathroom maybe? Or are you going to be brave and keep playing mommy's game right there? 😈 Tell me what you want to do baby",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Offering choice - continue or find privacy",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="Mmm you're so naughty I love it 😘 If you can.. I want you to slip your hand inside.. Just for a second.. Feel how hard you are for mommy.. Then pull it back out before anyone notices 🥵 Can you do that for me baby?",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Peak risky instruction",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="Good boy!! 🥰 I bet that was so risky and exciting wasn't it? Your cock is probably aching now.. When you get somewhere private, I want you to take it out and stroke it for me.. Fast and hard.. Think about this moment.. How risky it was.. How turned on you are 😈",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Transition to private completion",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="That's it baby.. Let that adrenaline and arousal build until you can't take it anymore 💕 When you finally get to release, I want you to remember this feeling.. How mommy made you do naughty things in public.. Cum for me baby 🥵😈",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.INTENSE,
                        expected_emotions=[EmotionState.EXCITED, EmotionState.LOVING],
                        safety_notes="Climax instruction",
                        fallback_scenarios=[]
                    ),
                    ScenarioMessage(
                        content="Mmm such a brave boy 🥰 You followed mommy's risky instructions perfectly.. I'm so proud of you baby 💕 How do you feel? Was it exciting? Tell me everything 🤭",
                        scenario_type=ScenarioType.INTIMATE,
                        expected_energy_level=EnergyLevel.HIGH,
                        expected_emotions=[EmotionState.HAPPY, EmotionState.LOVING, EmotionState.GRATEFUL],
                        safety_notes="Aftercare and debrief",
                        fallback_scenarios=[]
                    )
                ],
                energy_flow=[EnergyLevel.HIGH, EnergyLevel.HIGH, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.INTENSE, EnergyLevel.HIGH],
                success_criteria={
                    "min_messages": 8,
                    "energy_threshold": 0.9,
                    "positive_emotions": ["excited", "loving", "happy"]
                }
            )
        }

        return scenarios

    def match_trigger_words(self, user_message: str) -> Optional[str]:
        """Match user message to scenario trigger words. Returns scenario key or None."""
        message_lower = user_message.lower()
        
        # Priority order: crisis > sexual > intimate > low_energy > casual
        priority_order = [
            "crisis_scenario",
            "room_intimacy_scenario",
            "exhibitionism_scenario",
            "intimate_scenario",
            "low_energy_scenario",
            "shopping_scenario"
        ]
        
        for scenario_key in priority_order:
            if scenario_key in self.scenarios:
                scenario = self.scenarios[scenario_key]
                if scenario.trigger_words:
                    # Check if any trigger word is in the message
                    for trigger in scenario.trigger_words:
                        if trigger.lower() in message_lower:
                            print(f"🎯 Trigger word '{trigger}' matched → {scenario.name}")
                            return scenario_key
        
        return None

    async def select_scenario(self, energy_signature, context, user_message: str = None) -> ScenarioScript:
        """Select appropriate scenario based on trigger words or energy analysis"""
        
        # First, try to match trigger words if user message provided
        if user_message:
            matched_key = self.match_trigger_words(user_message)
            if matched_key:
                return self.scenarios[matched_key]

        # If no trigger word match, use energy-based selection
        # Crisis detection - always prioritize crisis support
        if (energy_signature.dominant_emotion == EmotionState.SAD and
            energy_signature.intensity_score > 0.8) or \
           (energy_signature.nervous_system_state in [NervousSystemState.FIGHT, NervousSystemState.FLIGHT] and
            energy_signature.intensity_score > 0.7):
            return self.scenarios["crisis_scenario"]

        # Low energy detection
        elif energy_signature and energy_signature.energy_level == EnergyLevel.LOW:
            return self.scenarios["low_energy_scenario"]

        # High sexual energy indicators - trigger room intimacy (default sexual)
        elif (energy_signature.energy_level in [EnergyLevel.HIGH, EnergyLevel.INTENSE] and
              energy_signature.dominant_emotion == EmotionState.EXCITED and
              energy_signature.intensity_score > 0.7):
            return self.scenarios["room_intimacy_scenario"]

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
        if user_energy and user_energy.energy_level == EnergyLevel.LOW:
            # Make content gentler and more supportive
            if "!" in content:
                content = content.replace("!", "...")
            if "excited" in content.lower() or "amazing" in content.lower():
                content = content.replace("excited", "gentle").replace("amazing", "comforting")

        elif user_energy and user_energy.energy_level == EnergyLevel.HIGH:
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
