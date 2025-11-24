"""
Data structures for engagement monitoring and topic re-engagement systems
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from routing_types import RoutingPath
from energy_types import EnergyLevel


class TopicCategory(Enum):
    """Topic categories for organization"""
    CASUAL = "casual"
    PLAYFUL = "playful"
    INTIMATE = "intimate"
    DEEP = "deep"
    RANDOM = "random"
    CALLBACK = "callback"


class LoopType(Enum):
    """Types of conversation loops"""
    INTERVIEW_MODE = "interview_mode"
    VALIDATION_SEEKING = "validation_seeking"
    TOPIC_EXHAUSTION = "topic_exhaustion"
    DEAD_END = "dead_end"
    POLITE_DISENGAGEMENT = "polite_disengagement"
    NONE = "none"


@dataclass
class EngagementMetrics:
    """Real-time engagement tracking metrics"""
    # Raw metrics (last 10 data points)
    message_length_trend: List[int] = field(default_factory=list)
    emoji_density_trend: List[float] = field(default_factory=list)
    punctuation_intensity: List[float] = field(default_factory=list)
    question_ratio: List[float] = field(default_factory=list)
    engagement_words_count: List[int] = field(default_factory=list)

    # Derived metrics
    current_engagement_score: float = 0.5
    engagement_trend: str = "stable"  # rising, stable, falling
    trend_velocity: float = 0.0  # Rate of change (-1.0 to +1.0)

    # Loop detection
    topic_repetition_count: int = 0
    path_repetition_pattern: List[str] = field(default_factory=list)
    conversation_depth_score: float = 0.5
    dead_end_count: int = 0

    # Timestamps
    last_engagement_drop: Optional[float] = None
    last_re_engagement_attempt: Optional[float] = None


@dataclass
class LoopAnalysis:
    """Analysis of detected conversation loops"""
    loop_detected: bool = False
    loop_type: LoopType = LoopType.NONE
    severity: float = 0.0  # 0.0-1.0
    affected_topics: List[str] = field(default_factory=list)
    consecutive_pattern_count: int = 0
    recommended_action: str = ""
    confidence: float = 0.0


@dataclass
class Topic:
    """Individual topic configuration for re-engagement"""
    topic_id: str
    category: TopicCategory
    keywords: List[str] = field(default_factory=list)

    # Injection strategies
    entry_lines: List[str] = field(default_factory=list)
    preferred_paths: List[RoutingPath] = field(default_factory=list)

    # Constraints
    relationship_stage: str = "any"  # early, developing, established, any
    min_energy_level: EnergyLevel = EnergyLevel.NONE
    max_energy_level: EnergyLevel = EnergyLevel.INTENSE

    # Tracking
    last_used: Optional[float] = None
    times_used: int = 0
    success_rate: float = 0.5
    freshness_score: float = 1.0


@dataclass
class FlowSwitch:
    """Flow switching decision"""
    should_switch: bool = False
    current_mode: str = ""
    target_mode: str = ""
    recommended_paths: List[RoutingPath] = field(default_factory=list)
    explanation: str = ""
    confidence: float = 0.0


@dataclass
class TrendAnalysis:
    """Engagement trend analysis"""
    trend_direction: str = "stable"  # rising, stable, falling
    trend_velocity: float = 0.0  # -1.0 to +1.0
    trend_confidence: float = 0.0  # 0.0-1.0
    is_critical: bool = False


@dataclass
class ReengagementAttempt:
    """Record of a re-engagement attempt for learning"""
    timestamp: float
    pre_engagement_score: float
    topic_used: Topic
    strategy_used: str
    forced_path: RoutingPath
    loop_type: LoopType

    # Measured after 5 messages
    post_engagement_score: float = 0.0
    engagement_delta: float = 0.0
    success: bool = False
    user_response_quality: float = 0.0
    measured: bool = False


@dataclass
class ReengagementDecision:
    """Decision to re-engage"""
    should_reengage: bool = False
    reason: str = ""
    urgency: str = "normal"  # low, normal, high, critical
    recommended_category: Optional[TopicCategory] = None
    recommended_strategy: str = ""
    confidence: float = 0.0
