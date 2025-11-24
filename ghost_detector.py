"""
Ghost Detection System - Auto-messages when user stops responding
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Optional, List, Callable
from enum import Enum


class GhostMessageType(Enum):
    """Types of ghost messages based on escalation level"""
    GENTLE = "gentle"      # First check-in
    CURIOUS = "curious"    # Second message
    PLAYFUL = "playful"    # Third/final message


@dataclass
class GhostDetectionConfig:
    """Configuration for ghost detection"""
    timeout_seconds: int = 60           # 1 minute for testing
    max_ghost_messages: int = 3         # Don't spam more than 3
    check_interval_seconds: int = 10    # How often to check
    escalation_delays: List[int] = field(default_factory=lambda: [60, 90, 120])  # Delays between messages


@dataclass
class GhostState:
    """Tracks ghost detection state for a session"""
    last_user_activity: float = 0.0
    ghost_messages_sent: int = 0
    last_ghost_message_time: float = 0.0
    is_ghosting: bool = False


class GhostDetector:
    """
    Detects when user stops responding and triggers auto-messages.
    Messages are generated through the girlfriend agent for personality consistency.
    """

    def __init__(self, config: Optional[GhostDetectionConfig] = None):
        self.config = config or GhostDetectionConfig()
        self.state = GhostState()
        self._running = False
        self._timer_thread: Optional[threading.Thread] = None
        self._on_ghost_detected: Optional[Callable] = None
        self._lock = threading.Lock()

    def set_ghost_callback(self, callback: Callable):
        """Set the callback function to call when ghost is detected"""
        self._on_ghost_detected = callback

    def update_user_activity(self):
        """Call this when user sends a message"""
        with self._lock:
            self.state.last_user_activity = time.time()
            self.state.is_ghosting = False
            # Reset ghost message count when user responds
            self.state.ghost_messages_sent = 0
            self.state.last_ghost_message_time = 0.0

    def get_ghost_prompt(self) -> tuple[str, GhostMessageType]:
        """
        Get the prompt for girlfriend agent based on escalation level.
        Dont use any emojis. Just use words.
        Returns (prompt, message_type)
        """
        level = self.state.ghost_messages_sent

        if level == 0:
            return (
                "The user hasn't responded in a while. Generate a SHORT, casual check-in message. "
                "Be natural. Keep it under 10 words. "
                "Don't be dramatic, just a simple check-in.",
                GhostMessageType.GENTLE
            )
        elif level == 1:
            return (
                "The user still hasn't responded after your first check-in. Generate a slightly more "
                "curious message wondering where they went. Keep it casual and short.",
                GhostMessageType.CURIOUS
            )
        else:
            return (
                "The user has been gone for a while now. Generate a playful/pouty message about being "
                "left on read. Be dramatic and a little bit pouty/angry. Keep it short.",
                GhostMessageType.PLAYFUL
            )

    def should_send_ghost_message(self) -> bool:
        """Check if we should send a ghost message now"""
        with self._lock:
            # Don't send if no user activity recorded yet
            if self.state.last_user_activity == 0:
                return False

            # Don't send if we've hit max messages
            if self.state.ghost_messages_sent >= self.config.max_ghost_messages:
                return False

            current_time = time.time()
            time_since_user = current_time - self.state.last_user_activity

            # Get the appropriate delay for this message level
            level = self.state.ghost_messages_sent
            if level < len(self.config.escalation_delays):
                required_delay = self.config.escalation_delays[level]
            else:
                required_delay = self.config.escalation_delays[-1]

            # For subsequent messages, check time since last ghost message
            if self.state.ghost_messages_sent > 0:
                time_since_ghost = current_time - self.state.last_ghost_message_time
                # Need at least 30 seconds between ghost messages
                if time_since_ghost < 30:
                    return False

            # Check if enough time has passed since user activity
            if time_since_user >= required_delay:
                return True

            return False

    def mark_ghost_message_sent(self):
        """Call this after sending a ghost message"""
        with self._lock:
            self.state.ghost_messages_sent += 1
            self.state.last_ghost_message_time = time.time()
            self.state.is_ghosting = True

    def reset(self):
        """Reset ghost detection state (call on session end/start)"""
        with self._lock:
            self.state = GhostState()

    def get_status(self) -> dict:
        """Get current ghost detection status"""
        with self._lock:
            current_time = time.time()
            time_since_user = current_time - self.state.last_user_activity if self.state.last_user_activity > 0 else 0

            return {
                "is_ghosting": self.state.is_ghosting,
                "ghost_messages_sent": self.state.ghost_messages_sent,
                "seconds_since_user": int(time_since_user),
                "max_messages": self.config.max_ghost_messages,
                "timeout_seconds": self.config.timeout_seconds
            }
