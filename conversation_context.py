"""
Conversation context and related types
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import time
from energy_types import EnergySignature

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
