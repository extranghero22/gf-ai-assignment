"""
Human-like polish transformer for AI responses
Adds natural imperfections and casual language to make responses feel more authentic
Enhanced with Hyunnie-specific personality patterns
"""

import random
import re
from typing import Dict, List, Tuple
from hyunnie_persona import HyunniePersona


class HumanPolishTransformer:
    """Applies human-like polish to AI responses to make them feel more natural"""

    def __init__(self):
        # Common typo patterns (casual texting style) - Enhanced with Hyunnie's style
        self.typo_patterns = {
            'you': ['u'],
            'your': ['ur'],
            'you are': ["you're", "ur"],
            'because': ['bc', 'cuz'],
            'about': ['abt'],
            'just': ['jus'],
            'really': ['rly'],
            'probably': ['prob', 'prolly'],
            'going to': ['gonna'],
            'want to': ['wanna'],
            'got to': ['gotta'],
            'kind of': ['kinda'],
            'sort of': ['sorta'],
            'out of': ['outta'],
            'a lot': ['alot'],  # Common mistake
            'don\'t know': ['dunno', 'idk'],
        }

        # Filler words to add occasionally - Use Hyunnie's filler words
        self.filler_words = HyunniePersona.LANGUAGE_PATTERNS['filler_words']

        # Overly formal phrases to replace
        self.formal_replacements = {
            'I would like to': 'i wanna',
            'I am going to': "i'm gonna",
            'I do not': "i don't",
            'cannot': "can't",
            'will not': "won't",
            'should not': "shouldn't",
            'could not': "couldn't",
            'would not': "wouldn't",
            'I would': "i'd",
            'I will': "i'll",
            'I have': "i've",
        }

    def apply_polish(self, text: str, context: Dict) -> str:
        """
        Apply human-like polish transformations to make text feel more natural

        Args:
            text: The AI-generated response to polish
            context: Context dict with routing_path, safety_status, response_length

        Returns:
            Polished text with natural imperfections
        """
        # Skip transformation for certain contexts
        if self._should_skip_polish(context):
            return text

        polished = text

        # 1. Remove formal phrases (make it casual)
        polished = self._remove_formal_phrases(polished)

        # 2. Apply lowercase preference (except I, proper nouns)
        polished = self._apply_lowercase(polished)

        # 3. Add occasional typos (2-3% of applicable words)
        polished = self._add_typos(polished, probability=0.025)

        # 4. Add filler words very occasionally (5% of sentences)
        polished = self._add_filler_words(polished, probability=0.05)

        # 5. Add Hyunnie's pet names occasionally (if not already present)
        polished = self._add_pet_names(polished, probability=0.15)

        return polished

    def _should_skip_polish(self, context: Dict) -> bool:
        """Determine if polish should be skipped for this response"""
        # Skip for PATH_D (minimal responses like "nice 💪")
        if context.get('routing_path') == 'PATH_D':
            return True

        # Skip for red safety status (crisis responses need to be clear)
        if context.get('safety_status') == 'red':
            return True

        # Skip for very short responses (already casual enough)
        response_length = context.get('response_length', 0)
        if response_length < 15:
            return True

        return False

    def _apply_lowercase(self, text: str) -> str:
        """
        Apply lowercase preference for casual texting feel
        Keep: "I", "I'm", "I'll", etc., proper nouns, emojis
        """
        # Don't lowercase if it's already lowercase or very short
        if text.islower() or len(text) < 10:
            return text

        # Split into words
        words = text.split()
        result = []

        for i, word in enumerate(words):
            # Keep "I" and contractions with I uppercase
            if word in ['I', "I'm", "I'll", "I've", "I'd"]:
                result.append(word)
            # Keep first word of sentence capitalized (after ., !, ?)
            elif i > 0 and words[i-1][-1] in '.!?' and len(word) > 1:
                result.append(word)
            # Lowercase other words that are capitalized
            elif word[0].isupper() and not any(char in word for char in '😀😁😂🤣😃😄😅😆😊😉'):
                # Keep if it looks like a proper noun (all caps or mid-sentence capital)
                if word.isupper() and len(word) > 1:
                    result.append(word)  # Keep acronyms
                elif i == 0:
                    # First word - lowercase it for casual feel
                    result.append(word.lower())
                else:
                    result.append(word.lower())
            else:
                result.append(word)

        return ' '.join(result)

    def _add_typos(self, text: str, probability: float = 0.025) -> str:
        """
        Add occasional typos to make text feel more human
        Only affects specific words with casual alternatives
        """
        for formal, casual_options in self.typo_patterns.items():
            # Case-insensitive search
            pattern = re.compile(r'\b' + re.escape(formal) + r'\b', re.IGNORECASE)

            def replace_with_probability(match):
                # Only replace with probability chance
                if random.random() < probability:
                    return random.choice(casual_options)
                return match.group(0)

            text = pattern.sub(replace_with_probability, text)

        return text

    def _remove_formal_phrases(self, text: str) -> str:
        """Replace overly formal phrases with casual alternatives"""
        for formal, casual in self.formal_replacements.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(formal), re.IGNORECASE)
            text = pattern.sub(casual, text)

        return text

    def _add_filler_words(self, text: str, probability: float = 0.05) -> str:
        """
        Add occasional filler words to make text feel more conversational
        Very sparingly - only at sentence starts
        """
        # Split into sentences
        sentences = re.split(r'([.!?]\s+)', text)
        result = []

        for i, part in enumerate(sentences):
            # Only add to actual sentences (not punctuation)
            if i % 2 == 0 and len(part.strip()) > 10:
                # 5% chance to add filler
                if random.random() < probability:
                    filler = random.choice(self.filler_words)
                    # Add at start of sentence
                    part = f"{filler} {part}"

            result.append(part)

        return ''.join(result)

    def _add_pet_names(self, text: str, probability: float = 0.15) -> str:
        """
        Add Hyunnie's pet names occasionally if not already present
        Adds them at the end or middle of sentences naturally
        """
        pet_names = HyunniePersona.LANGUAGE_PATTERNS['pet_names_for_fan']

        # Check if text already contains a pet name
        text_lower = text.lower()
        if any(pet_name in text_lower for pet_name in pet_names):
            return text  # Already has a pet name

        # Small chance to add pet name
        if random.random() < probability:
            pet_name = random.choice(pet_names)

            # Add at the end with comma or at the beginning
            if random.random() < 0.5:
                # Add at end: "how are you doing" → "how are you doing babe"
                text = text.rstrip('.!?') + f" {pet_name}" + (text[-1] if text and text[-1] in '.!?' else '')
            else:
                # Add at beginning: "how are you" → "babe how are you"
                text = f"{pet_name} {text}"

        return text
