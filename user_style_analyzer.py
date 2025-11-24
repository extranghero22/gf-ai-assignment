"""
User Style Analyzer - Analyzes user's typing patterns to mirror their style
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import Counter


@dataclass
class UserStyleProfile:
    """Profile of user's typing style"""
    # Message length preferences
    avg_message_length: float = 50.0
    prefers_short_messages: bool = False  # < 30 chars average
    prefers_long_messages: bool = False   # > 100 chars average

    # Capitalization
    uses_all_lowercase: bool = False
    uses_all_caps: bool = False
    uses_normal_caps: bool = True

    # Punctuation patterns
    uses_ellipsis: bool = False          # "..."
    uses_multiple_punctuation: bool = False  # "!!" or "??"
    punctuation_counts: Dict[str, int] = field(default_factory=dict)

    # Emoji usage
    uses_emojis: bool = False
    emoji_frequency: float = 0.0  # 0.0 to 1.0
    common_emojis: List[str] = field(default_factory=list)

    # Common abbreviations
    uses_abbreviations: bool = False
    common_abbreviations: List[str] = field(default_factory=list)

    # Message splitting preference
    sends_multiple_short: bool = False  # User sends many short messages

    # Total messages analyzed
    messages_analyzed: int = 0


class UserStyleAnalyzer:
    """
    Analyzes user's typing patterns and builds a style profile.
    Used to mirror user's style in AI responses.
    """

    def __init__(self):
        self.profile = UserStyleProfile()
        self.message_lengths: List[int] = []
        self.all_punctuation: List[str] = []
        self.all_emojis: List[str] = []
        self.caps_styles: List[str] = []  # 'lower', 'upper', 'normal'

        # Common texting abbreviations to detect
        self.abbreviation_patterns = {
            r'\bu\b': 'u',           # you -> u
            r'\brn\b': 'rn',         # right now
            r'\bngl\b': 'ngl',       # not gonna lie
            r'\btbh\b': 'tbh',       # to be honest
            r'\bidk\b': 'idk',       # i don't know
            r'\blol\b': 'lol',       # laugh out loud
            r'\blmao\b': 'lmao',     # laughing my ass off
            r'\bomg\b': 'omg',       # oh my god
            r'\bwtf\b': 'wtf',       # what the f
            r'\bbtw\b': 'btw',       # by the way
            r'\bwbu\b': 'wbu',       # what about you
            r'\bhbu\b': 'hbu',       # how about you
            r'\bimo\b': 'imo',       # in my opinion
            r'\bfr\b': 'fr',         # for real
            r'\bik\b': 'ik',         # i know
            r'\bty\b': 'ty',         # thank you
            r'\bpls\b': 'pls',       # please
            r'\bplz\b': 'plz',       # please
            r'\bthx\b': 'thx',       # thanks
            r'\bk\b': 'k',           # ok/okay
            r'\bya\b': 'ya',         # yeah/yes
            r'\byea\b': 'yea',       # yeah
            r'\bbc\b': 'bc',         # because
            r'\bcuz\b': 'cuz',       # because
            r'\bwanna\b': 'wanna',   # want to
            r'\bgonna\b': 'gonna',   # going to
            r'\bgotta\b': 'gotta',   # got to
            r'\bkinda\b': 'kinda',   # kind of
            r'\bsorta\b': 'sorta',   # sort of
        }

        # Emoji regex pattern
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002600-\U000026FF"  # misc symbols
            "\U00002700-\U000027BF"  # dingbats
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
            "]+",
            flags=re.UNICODE
        )

    def analyze_message(self, message: str) -> None:
        """Analyze a single user message and update the style profile"""
        if not message or not message.strip():
            return

        message = message.strip()
        self.profile.messages_analyzed += 1

        # Analyze message length
        self.message_lengths.append(len(message))

        # Analyze capitalization
        self._analyze_capitalization(message)

        # Analyze punctuation
        self._analyze_punctuation(message)

        # Analyze emojis
        self._analyze_emojis(message)

        # Analyze abbreviations
        self._analyze_abbreviations(message)

        # Update aggregate profile
        self._update_profile()

    def _analyze_capitalization(self, message: str) -> None:
        """Analyze capitalization style"""
        # Remove emojis and punctuation for caps analysis
        text_only = re.sub(self.emoji_pattern, '', message)
        text_only = re.sub(r'[^\w\s]', '', text_only)

        if not text_only.strip():
            return

        # Check capitalization style
        if text_only == text_only.lower():
            self.caps_styles.append('lower')
        elif text_only == text_only.upper() and len(text_only) > 3:
            self.caps_styles.append('upper')
        else:
            self.caps_styles.append('normal')

    def _analyze_punctuation(self, message: str) -> None:
        """Analyze punctuation patterns"""
        # Check for ellipsis
        if '...' in message:
            self.all_punctuation.append('...')

        # Check for multiple exclamation marks
        if re.search(r'!{2,}', message):
            self.all_punctuation.append('!!')

        # Check for multiple question marks
        if re.search(r'\?{2,}', message):
            self.all_punctuation.append('??')

        # Check for mixed punctuation
        if re.search(r'[!?]{2,}', message):
            self.all_punctuation.append('!?')

    def _analyze_emojis(self, message: str) -> None:
        """Analyze emoji usage"""
        emojis = self.emoji_pattern.findall(message)
        if emojis:
            self.all_emojis.extend(emojis)

    def _analyze_abbreviations(self, message: str) -> None:
        """Analyze abbreviation usage"""
        message_lower = message.lower()
        for pattern, abbrev in self.abbreviation_patterns.items():
            if re.search(pattern, message_lower):
                if abbrev not in self.profile.common_abbreviations:
                    self.profile.common_abbreviations.append(abbrev)

    def _update_profile(self) -> None:
        """Update the aggregate style profile"""
        if not self.message_lengths:
            return

        # Update message length preferences
        self.profile.avg_message_length = sum(self.message_lengths) / len(self.message_lengths)
        self.profile.prefers_short_messages = self.profile.avg_message_length < 30
        self.profile.prefers_long_messages = self.profile.avg_message_length > 100

        # Update capitalization preferences
        if self.caps_styles:
            caps_counter = Counter(self.caps_styles)
            most_common = caps_counter.most_common(1)[0][0]
            self.profile.uses_all_lowercase = most_common == 'lower'
            self.profile.uses_all_caps = most_common == 'upper'
            self.profile.uses_normal_caps = most_common == 'normal'

        # Update punctuation preferences
        if self.all_punctuation:
            punct_counter = Counter(self.all_punctuation)
            self.profile.punctuation_counts = dict(punct_counter)
            self.profile.uses_ellipsis = '...' in punct_counter
            self.profile.uses_multiple_punctuation = '!!' in punct_counter or '??' in punct_counter

        # Update emoji preferences
        total_messages = len(self.message_lengths)
        messages_with_emojis = len([1 for e in self.all_emojis if e])  # Rough estimate
        self.profile.uses_emojis = len(self.all_emojis) > 0
        self.profile.emoji_frequency = min(1.0, len(self.all_emojis) / max(1, total_messages))
        if self.all_emojis:
            emoji_counter = Counter(self.all_emojis)
            self.profile.common_emojis = [e for e, _ in emoji_counter.most_common(5)]

        # Update abbreviation preferences
        self.profile.uses_abbreviations = len(self.profile.common_abbreviations) > 0

    def get_style_profile(self) -> UserStyleProfile:
        """Get the current style profile"""
        return self.profile

    def get_style_summary(self) -> Dict:
        """Get a summary of the user's style for debugging/logging"""
        return {
            "messages_analyzed": self.profile.messages_analyzed,
            "avg_length": round(self.profile.avg_message_length, 1),
            "caps_style": "lowercase" if self.profile.uses_all_lowercase else ("CAPS" if self.profile.uses_all_caps else "Normal"),
            "uses_ellipsis": self.profile.uses_ellipsis,
            "uses_emojis": self.profile.uses_emojis,
            "emoji_frequency": round(self.profile.emoji_frequency, 2),
            "abbreviations": self.profile.common_abbreviations[:5],
            "prefers_short": self.profile.prefers_short_messages
        }

    def apply_style_to_text(self, text: str) -> str:
        """Apply user's style to a text (for AI response)"""
        if self.profile.messages_analyzed < 3:
            # Not enough data to apply style
            return text

        result = text

        # Apply capitalization style
        if self.profile.uses_all_lowercase:
            result = result.lower()
        elif self.profile.uses_all_caps:
            result = result.upper()

        # Apply punctuation style
        if self.profile.uses_ellipsis:
            # Replace some periods with ellipsis
            result = re.sub(r'\.(\s|$)', '...\\1', result, count=1)

        if self.profile.uses_multiple_punctuation:
            # Intensify some punctuation
            result = re.sub(r'!(\s|$)', '!!\\1', result, count=1)
            result = re.sub(r'\?(\s|$)', '??\\1', result, count=1)

        return result

    def should_shorten_response(self) -> bool:
        """Check if AI should send shorter responses to match user"""
        return self.profile.prefers_short_messages and self.profile.messages_analyzed >= 3

    def get_target_length(self) -> int:
        """Get target response length based on user's style"""
        if self.profile.messages_analyzed < 3:
            return 100  # Default

        # Mirror user's length preference with some flexibility
        target = int(self.profile.avg_message_length * 1.5)  # AI can be slightly longer
        return max(20, min(target, 200))  # Clamp between 20 and 200

    def reset(self) -> None:
        """Reset the analyzer"""
        self.profile = UserStyleProfile()
        self.message_lengths = []
        self.all_punctuation = []
        self.all_emojis = []
        self.caps_styles = []


# Global instance
_analyzer_instance: Optional[UserStyleAnalyzer] = None

def get_user_style_analyzer() -> UserStyleAnalyzer:
    """Get or create the global UserStyleAnalyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = UserStyleAnalyzer()
    return _analyzer_instance
