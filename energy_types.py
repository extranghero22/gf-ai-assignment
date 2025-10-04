"""
Energy-related types and enums for the conversation system
"""

from dataclasses import dataclass
from enum import Enum

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
