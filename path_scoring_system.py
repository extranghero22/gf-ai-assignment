"""
Multi-Path Scoring System for Message Routing
Scores all routing paths and selects using weighted randomness to prevent overuse
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
from enum import Enum
import random

from routing_types import RoutingPath
from energy_types import EnergySignature, EnergyLevel, EnergyType


@dataclass
class PathScore:
    """Comprehensive score for a single routing path"""
    path: RoutingPath
    base_score: float = 0.0                      # LLM-generated appropriateness (0-100)
    context_modifier: float = 0.0                # Conversation history bonus/penalty
    frequency_penalty: float = 0.0               # Overuse penalty
    personality_bias: float = 0.0                # Hyunnie mood/preference
    compatibility_score: float = 0.0             # Compatible with previous path?
    energy_alignment: float = 0.0                # Matches energy signature?
    relationship_stage_modifier: float = 0.0     # Early vs established
    final_score: float = 0.0                     # Weighted total
    reasoning: str = ""                          # LLM explanation


class PathFrequencyTracker:
    """Tracks path usage and calculates overuse penalties"""

    def __init__(self):
        self.session_path_counts: Dict[str, int] = defaultdict(int)
        self.recent_paths: List[str] = []
        self.max_recent_paths = 10

    def calculate_frequency_penalty(self, path: str) -> float:
        """
        Returns penalty score (0-100) based on recent usage.
        Higher penalty = path used too much recently.

        Args:
            path: Path string (e.g., "PATH_E")

        Returns:
            Penalty value (0 = no penalty, 60 = severe penalty)
        """
        recent_usage = self.recent_paths.count(path)

        # Penalty tiers based on recent usage percentage
        if recent_usage >= 4:    # 40%+ of recent messages - SEVERE
            return 60.0
        elif recent_usage == 3:  # 30% - HIGH
            return 40.0
        elif recent_usage == 2:  # 20% - MODERATE
            return 20.0
        elif recent_usage == 1:  # 10% - MILD
            return 5.0
        else:                    # 0% - NO PENALTY
            return 0.0

    def record_path_usage(self, path: str):
        """Record that this path was used"""
        self.session_path_counts[path] += 1
        self.recent_paths.append(path)
        if len(self.recent_paths) > self.max_recent_paths:
            self.recent_paths.pop(0)

    def get_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for all paths"""
        return dict(self.session_path_counts)


class PathCompatibilityMatrix:
    """Defines which paths work well together for smooth conversation flow"""

    def __init__(self):
        # Define compatibility rules for each path
        self.compatibility_rules = {
            "PATH_A": {
                "good_after": ["PATH_A", "PATH_I", "PATH_F"],  # Natural flow
                "avoid_after": ["PATH_E", "PATH_C"],           # Jarring transition
            },
            "PATH_B": {
                "good_after": ["PATH_A", "PATH_I"],
                "avoid_after": ["PATH_B", "PATH_E"],           # Don't spam confusion
            },
            "PATH_C": {
                "good_after": ["PATH_A", "PATH_I"],
                "avoid_after": ["PATH_C", "PATH_E"],           # Don't spam deflection
            },
            "PATH_D": {
                "good_after": ["PATH_D", "PATH_I"],            # Maintain tension
                "avoid_after": ["PATH_E", "PATH_F"],           # Contradictory energy
            },
            "PATH_E": {
                "good_after": ["PATH_A", "PATH_I"],            # Follow up dramatic moment
                "avoid_after": ["PATH_E", "PATH_C", "PATH_D"], # Don't spam self-focus
            },
            "PATH_F": {
                "good_after": ["PATH_A", "PATH_F", "PATH_L"],
                "avoid_after": ["PATH_D", "PATH_E"],           # Contradictory tone
            },
            "PATH_G": {
                "good_after": ["PATH_A", "PATH_F"],
                "avoid_after": ["PATH_D", "PATH_E"],
            },
            "PATH_I": {
                "good_after": ["PATH_A", "PATH_I", "PATH_D"],  # Playful flow
                "avoid_after": ["PATH_E", "PATH_F", "PATH_L"], # Contradictory tone
            },
            "PATH_L": {
                "good_after": ["PATH_A", "PATH_F"],
                "avoid_after": ["PATH_D", "PATH_I", "PATH_E"], # Contradictory tone
            },
            "PATH_M": {
                "good_after": ["PATH_A", "PATH_C"],
                "avoid_after": ["PATH_E", "PATH_L"],           # Contradictory tone
            },
        }

    def calculate_compatibility_score(self, current_path: str, previous_path: Optional[str]) -> float:
        """
        Returns bonus/penalty based on path compatibility.

        Args:
            current_path: Path being considered
            previous_path: Previously used path (or None)

        Returns:
            Score 0-100 (50 = neutral, 80 = good match, 20 = poor match)
        """
        if not previous_path:
            return 50.0  # Neutral for first message

        rules = self.compatibility_rules.get(current_path, {})

        if previous_path in rules.get("good_after", []):
            return 80.0  # +30 bonus for good flow
        elif previous_path in rules.get("avoid_after", []):
            return 20.0  # -30 penalty for jarring transition
        else:
            return 50.0  # Neutral


class HyunniePersonalityState:
    """Tracks Hyunnie's current mood and personality biases"""

    def __init__(self):
        self.current_mood: str = "playful"  # playful, dramatic, vulnerable, confident
        self.playfulness_level: float = 0.7
        self.drama_level: float = 0.5
        self.confidence_level: float = 0.8

        # Mood-based path preferences
        self.mood_biases = {
            "playful": {
                "PATH_I": 90,  # Very aligned with playful teasing
                "PATH_A": 70,  # Normal responses work
                "PATH_D": 60,  # Brief responses for tension
                "PATH_E": 50,  # Less aligned
                "PATH_F": 40,
                "PATH_B": 45,
                "PATH_C": 45,
                "PATH_G": 65,  # Playful jealousy
                "PATH_L": 40,
                "PATH_M": 55,
            },
            "dramatic": {
                "PATH_E": 95,  # Very aligned with drama
                "PATH_F": 85,  # Emotional reactions
                "PATH_L": 70,  # Vulnerability
                "PATH_A": 50,
                "PATH_I": 60,
                "PATH_D": 30,  # Doesn't fit dramatic mood
                "PATH_B": 45,
                "PATH_C": 55,
                "PATH_G": 75,
                "PATH_M": 50,
            },
            "vulnerable": {
                "PATH_L": 90,  # Very aligned with vulnerability
                "PATH_F": 75,
                "PATH_A": 65,
                "PATH_E": 60,
                "PATH_I": 40,  # Less teasing when vulnerable
                "PATH_D": 35,
                "PATH_B": 50,
                "PATH_C": 45,
                "PATH_G": 70,  # Insecure jealousy
                "PATH_M": 55,
            },
            "confident": {
                "PATH_A": 85,  # Direct and clear
                "PATH_I": 85,  # Confident teasing
                "PATH_D": 65,  # Can be brief without worry
                "PATH_M": 80,  # Firm boundaries
                "PATH_E": 40,  # Less dramatic
                "PATH_F": 50,
                "PATH_B": 35,  # No confusion
                "PATH_C": 45,
                "PATH_G": 60,
                "PATH_L": 30,  # Less vulnerable
            },
        }

    def get_path_bias(self, path: str) -> float:
        """
        Returns bias score (0-100) based on current mood.

        Args:
            path: Path string (e.g., "PATH_I")

        Returns:
            Score indicating alignment with current mood
        """
        biases = self.mood_biases.get(self.current_mood, {})
        return biases.get(path, 50.0)

    def update_mood(self, energy_signature: EnergySignature, user_engagement: float):
        """
        Update Hyunnie's mood based on conversation dynamics.

        Args:
            energy_signature: Current energy signature from user
            user_engagement: Estimated user engagement (0.0-1.0)
        """
        # If user is highly engaged and playful, become more playful
        if user_engagement > 0.7 and energy_signature.energy_type == EnergyType.PLAYFUL:
            self.current_mood = "playful"
            self.playfulness_level = min(1.0, self.playfulness_level + 0.1)

        # If user is disengaged, become more dramatic to get attention
        elif user_engagement < 0.3:
            self.current_mood = "dramatic"
            self.drama_level = min(1.0, self.drama_level + 0.1)

        # If user is intimate or loving, become more vulnerable
        elif energy_signature.energy_type == EnergyType.INTIMATE:
            self.current_mood = "vulnerable"
            self.confidence_level = max(0.0, self.confidence_level - 0.05)

        # If user is combative, become more confident/firm
        elif energy_signature.energy_type == EnergyType.COMBATIVE:
            self.current_mood = "confident"
            self.confidence_level = min(1.0, self.confidence_level + 0.1)


class RelationshipStageTracker:
    """Tracks relationship stage and adjusts path preferences"""

    def __init__(self):
        self.message_count: int = 0
        self.intimacy_level: float = 0.0

        # Stage-based modifiers
        self.stage_modifiers = {
            "early": {  # 0-10 messages
                "PATH_A": 80,  # Safe, normal responses
                "PATH_I": 70,  # Light teasing OK
                "PATH_D": 60,
                "PATH_L": 30,  # Too vulnerable too soon
                "PATH_E": 60,  # Some drama OK
                "PATH_F": 50,
                "PATH_B": 55,
                "PATH_C": 50,
                "PATH_G": 50,  # Not possessive yet
                "PATH_M": 70,
            },
            "developing": {  # 10-50 messages
                "PATH_A": 75,
                "PATH_I": 80,  # More comfortable teasing
                "PATH_D": 65,
                "PATH_L": 60,  # Can show some vulnerability
                "PATH_E": 65,
                "PATH_F": 70,
                "PATH_B": 60,
                "PATH_C": 60,
                "PATH_G": 75,  # More possessive
                "PATH_M": 65,
            },
            "established": {  # 50+ messages
                "PATH_A": 70,
                "PATH_I": 80,
                "PATH_D": 70,
                "PATH_L": 80,  # Comfortable with vulnerability
                "PATH_E": 40,  # Less need for attention-seeking
                "PATH_F": 75,
                "PATH_B": 55,
                "PATH_C": 55,
                "PATH_G": 80,  # Very possessive
                "PATH_M": 70,
            },
        }

    def get_stage(self) -> str:
        """Determine current relationship stage"""
        if self.message_count < 10:
            return "early"
        elif self.message_count < 50:
            return "developing"
        else:
            return "established"

    def get_stage_modifier(self, path: str) -> float:
        """
        Returns modifier (0-100) based on relationship stage.

        Args:
            path: Path string

        Returns:
            Score indicating appropriateness for current stage
        """
        stage = self.get_stage()
        modifiers = self.stage_modifiers.get(stage, {})
        return modifiers.get(path, 50.0)

    def increment_message_count(self):
        """Increment message counter"""
        self.message_count += 1


class EnergyPathAlignment:
    """Maps energy signatures to path preferences"""

    def __init__(self):
        # Energy-path alignment scores
        self.alignment_matrix = {
            # (EnergyLevel, EnergyType): {path: score}
            (EnergyLevel.HIGH, EnergyType.PLAYFUL): {
                "PATH_I": 90, "PATH_A": 70, "PATH_D": 50, "PATH_E": 60,
                "PATH_F": 75, "PATH_B": 40, "PATH_C": 40, "PATH_G": 70,
                "PATH_L": 40, "PATH_M": 50,
            },
            (EnergyLevel.MEDIUM, EnergyType.NEUTRAL): {
                "PATH_A": 80, "PATH_D": 70, "PATH_E": 60, "PATH_I": 70,
                "PATH_F": 50, "PATH_B": 55, "PATH_C": 55, "PATH_G": 50,
                "PATH_L": 50, "PATH_M": 60,
            },
            (EnergyLevel.LOW, EnergyType.COOPERATIVE): {
                "PATH_A": 85, "PATH_F": 70, "PATH_L": 75, "PATH_E": 55,
                "PATH_I": 45, "PATH_D": 40, "PATH_B": 50, "PATH_C": 50,
                "PATH_G": 45, "PATH_M": 60,
            },
            (EnergyLevel.HIGH, EnergyType.INTIMATE): {
                "PATH_A": 80, "PATH_F": 85, "PATH_L": 70, "PATH_I": 75,
                "PATH_E": 60, "PATH_D": 50, "PATH_B": 30, "PATH_C": 35,
                "PATH_G": 80, "PATH_M": 50,
            },
            (EnergyLevel.HIGH, EnergyType.COMBATIVE): {
                "PATH_M": 85, "PATH_G": 80, "PATH_I": 70, "PATH_A": 60,
                "PATH_F": 75, "PATH_D": 65, "PATH_B": 45, "PATH_C": 70,
                "PATH_L": 40, "PATH_E": 45,
            },
        }

    def calculate_alignment(self, path: str, energy_sig: EnergySignature) -> float:
        """
        Returns alignment score (0-100) between path and energy signature.

        Args:
            path: Path string
            energy_sig: Current energy signature

        Returns:
            Alignment score
        """
        key = (energy_sig.energy_level, energy_sig.energy_type)
        alignment_scores = self.alignment_matrix.get(key, {})

        # If exact match not found, use neutral default
        return alignment_scores.get(path, 50.0)


class PathSelector:
    """Selects final path using weighted randomness"""

    def select_path(self, path_scores: Dict[RoutingPath, PathScore]) -> tuple[RoutingPath, str]:
        """
        Select final path using weighted randomness.

        Strategy:
        1. Get top 3 paths by final_score
        2. If top path is 20+ points ahead: choose it (clear winner)
        3. Otherwise: weighted random selection from top 3

        Args:
            path_scores: Dict mapping paths to their PathScore objects

        Returns:
            Tuple of (chosen_path, selection_method)
        """
        # Sort paths by final score
        sorted_paths = sorted(
            path_scores.items(),
            key=lambda x: x[1].final_score,
            reverse=True
        )

        if not sorted_paths:
            # Fallback to PATH_A if no scores
            return (RoutingPath.RESPOND_NORMALLY, "fallback")

        top_path = sorted_paths[0]

        # Only one path scored
        if len(sorted_paths) == 1:
            return (top_path[0], "only_option")

        second_path = sorted_paths[1]

        # Clear winner (20+ point margin)
        if top_path[1].final_score - second_path[1].final_score > 20:
            return (top_path[0], "clear_winner")

        # Weighted random from top 3
        candidates = sorted_paths[:min(3, len(sorted_paths))]
        weights = [p[1].final_score for p in candidates]

        # Ensure all weights are positive
        min_weight = min(weights)
        if min_weight < 0:
            weights = [w - min_weight + 1 for w in weights]

        # Random selection
        chosen_path = random.choices(
            [c[0] for c in candidates],
            weights=weights
        )[0]

        return (chosen_path, "weighted_random")
