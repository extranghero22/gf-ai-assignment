"""
Conversation context and related types
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import time
from energy_types import EnergySignature
from engagement_types import EngagementMetrics, LoopAnalysis

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

    # Engagement monitoring fields
    engagement_metrics: Optional[EngagementMetrics] = None
    engagement_history: List[float] = field(default_factory=list)  # Last 20 engagement scores
    loop_detections: List[LoopAnalysis] = field(default_factory=list)  # Recent loop analyses
    last_re_engagement: Optional[float] = None  # Timestamp of last re-engagement attempt
