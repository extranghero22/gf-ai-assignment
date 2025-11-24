"""
Intelligent message splitting agent for building anticipation
With user style mirroring capabilities
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MessagePart:
    content: str
    type: str  # 'teasing', 'sensory', 'question', 'demand'
    delay: float  # seconds to wait before next message

class MessageSplitter:
    """Intelligently splits messages into sequential parts based on content type and context"""
    
    def __init__(self):
        # General patterns for different message types
        self.teasing_patterns = [
            r'\*[^*]+\*',  # *text* for actions
            r'[Mm]mm[^.]*\.',  # Mmm... patterns
            r'[Oo]h [^.]*\.',  # Oh... patterns
            r'[Ss]uch[^.]*\.',  # Such... patterns
            r'[Hh]aha[^.]*\.',  # Haha... patterns
            r'[Ll]ol[^.]*\.',  # Lol... patterns
        ]
        
        self.sensory_patterns = [
            r'[Ii]magine[^.]*\.',  # Imagine... patterns
            r'[Ff]eel[^.]*\.',  # Feel... patterns
            r'[Nn]otice[^.]*\.',  # Notice... patterns
            r'[Ww]hile you[^.]*\.',  # While you... patterns
            r'[Pp]icture[^.]*\.',  # Picture... patterns
            r'[Tt]hink about[^.]*\.',  # Think about... patterns
        ]
        
        self.question_patterns = [
            r'[^.]*\?[^.]*',  # Questions
            r'[Aa]re you[^.]*\?',  # Are you... questions
            r'[Dd]o you[^.]*\?',  # Do you... questions
            r'[Ww]ant[^.]*\?',  # Want... questions
            r'[Hh]ow[^.]*\?',  # How... questions
            r'[Ww]hat[^.]*\?',  # What... questions
        ]
        
        self.demand_patterns = [
            r'[Yy]ou\'re going to[^.]*\.',  # You're going to...
            r'[Nn]ow[^.]*\.',  # Now... commands
            r'[Ss]ay it[^.]*\.',  # Say it...
            r'[Aa]sk[^.]*\.',  # Ask...
            r'[Tt]ell me[^.]*\.',  # Tell me...
            r'[Ss]how me[^.]*\.',  # Show me...
        ]
        
        # Emotional and supportive patterns
        self.emotional_patterns = [
            r'[Ii]\'m so[^.]*\.',  # I'm so... patterns
            r'[Tt]hat\'s[^.]*\.',  # That's... patterns
            r'[Yy]ou\'re[^.]*\.',  # You're... patterns
            r'[Ii] understand[^.]*\.',  # I understand... patterns
            r'[Ii]t\'s okay[^.]*\.',  # It's okay... patterns
        ]
        
        # Storytelling and descriptive patterns
        self.storytelling_patterns = [
            r'[Oo]nce[^.]*\.',  # Once... patterns
            r'[Tt]hen[^.]*\.',  # Then... patterns
            r'[Ss]uddenly[^.]*\.',  # Suddenly... patterns
            r'[Aa]fter[^.]*\.',  # After... patterns
            r'[Bb]efore[^.]*\.',  # Before... patterns
        ]

        # User style analyzer for mirroring
        self._user_style = None

    def set_user_style(self, style_analyzer) -> None:
        """Set the user style analyzer for style mirroring"""
        self._user_style = style_analyzer

    def apply_user_style(self, text: str) -> str:
        """Apply user's typing style to the text"""
        if not self._user_style or not text:
            return text

        profile = self._user_style.get_style_profile()

        # Only apply style if we have enough data
        if profile.messages_analyzed < 3:
            return text

        result = text

        # Apply capitalization style
        if profile.uses_all_lowercase:
            result = result.lower()
        # Note: We don't apply all-caps as it looks too aggressive from AI

        # Apply punctuation style
        if profile.uses_ellipsis:
            # Add ellipsis to some sentences (replace single period)
            sentences = result.split('. ')
            if len(sentences) > 1:
                # Add ellipsis to first sentence only
                sentences[0] = sentences[0].rstrip('.') + '...'
                result = '. '.join(sentences)

        if profile.uses_multiple_punctuation:
            # Intensify ending punctuation
            if result.endswith('!'):
                result = result[:-1] + '!!'
            elif result.endswith('?'):
                result = result[:-1] + '??'

        return result

    def get_target_message_length(self) -> int:
        """Get target message length based on user's style"""
        if not self._user_style:
            return 150  # Default

        profile = self._user_style.get_style_profile()
        if profile.messages_analyzed < 3:
            return 150  # Default

        # Mirror user's length with some flexibility (AI can be 1.5x longer)
        target = int(profile.avg_message_length * 1.5)
        return max(30, min(target, 250))  # Clamp between 30 and 250

    def should_split_for_user_style(self, message: str) -> bool:
        """Check if message should be split based on user's preference for short messages"""
        if not self._user_style:
            return False

        profile = self._user_style.get_style_profile()
        if profile.messages_analyzed < 5:
            return False

        # If user prefers short messages, we should split longer ones
        return profile.prefers_short_messages and len(message) > 60

    def split_message(self, message: str, context: str = "general") -> List[MessagePart]:
        """Intelligently split a message into sequential parts based on content type and context"""
        
        # Clean the message
        message = message.strip()
        
        # First, try to rephrase if the message is too long and repetitive
        if len(message) > 300:
            message = self._rephrase_long_message(message)
        
        # Determine if message should be split based on length and context
        min_length = self._get_minimum_length_for_splitting(context)
        if len(message) < min_length:
            return [MessagePart(content=message, type='complete', delay=0.0)]
        
        # Check if message has natural split points
        if not self._has_natural_split_points(message):
            return [MessagePart(content=message, type='complete', delay=0.0)]
        
        # Detect content type for appropriate splitting strategy
        content_type = self._detect_content_type(message)
        return self._split_by_content_type(message, content_type)
    
    def _get_minimum_length_for_splitting(self, context: str) -> int:
        """Get minimum message length for splitting based on context"""
        context_thresholds = {
            "sexual": 120,     # Increased threshold to reduce spam
            "emotional": 180,  # Emotional content needs more context
            "storytelling": 150, # Stories can be split for dramatic effect
            "general": 200,    # General conversation needs more length
            "crisis": 250,     # Crisis messages should rarely be split
        }
        return context_thresholds.get(context, 200)
    
    def _detect_content_type(self, message: str) -> str:
        """Detect the type of content in the message"""
        message_lower = message.lower()
        
        # Crisis/emotional content indicators (check first for safety)
        crisis_keywords = ['sad', 'depressed', 'anxious', 'worried', 'scared', 'hurt', 'pain', 'cry', 'tears', 'safe', 'worried about you']
        if any(keyword in message_lower for keyword in crisis_keywords):
            return "crisis"
        
        # Sexual content indicators (more specific to avoid false positives)
        sexual_keywords = ['mommy', 'cock', 'pussy', 'fuck', 'sex', 'horny', 'aroused', 'cum', 'orgasm', 'tongue', 'mouth on you', 'throat']
        if any(keyword in message_lower for keyword in sexual_keywords):
            return "sexual"
        
        # Emotional support indicators
        emotional_keywords = ['love', 'care', 'support', 'understand', 'here for you', 'comfort', 'sorry you\'re feeling', 'breaks my heart', 'not alone']
        if any(keyword in message_lower for keyword in emotional_keywords):
            return "emotional"
        
        # Storytelling indicators
        story_keywords = ['once upon a time', 'princess', 'castle', 'then one day', 'suddenly', 'after that day', 'mysterious stranger']
        if any(keyword in message_lower for keyword in story_keywords):
            return "storytelling"
        
        return "general"
    
    def _split_by_content_type(self, message: str, content_type: str) -> List[MessagePart]:
        """Split message based on detected content type"""
        if content_type == "sexual":
            return self._split_sexual_content(message)
        elif content_type == "crisis":
            return self._split_crisis_content(message)
        elif content_type == "emotional":
            return self._split_emotional_content(message)
        elif content_type == "storytelling":
            return self._split_storytelling_content(message)
        else:
            return self._split_general_content(message)
    
    def _split_sexual_content(self, message: str) -> List[MessagePart]:
        """Split sexual content for maximum anticipation"""
        return self._split_by_sentences_with_delays(message, {
            "teasing": 2.0,
            "sensory": 3.5,
            "question": 4.0,
            "demand": 2.5
        })
    
    def _split_crisis_content(self, message: str) -> List[MessagePart]:
        """Split crisis content carefully to maintain support"""
        return self._split_by_sentences_with_delays(message, {
            "emotional": 1.5,
            "question": 2.0,
            "demand": 1.0
        })
    
    def _split_emotional_content(self, message: str) -> List[MessagePart]:
        """Split emotional content for warmth and connection"""
        return self._split_by_sentences_with_delays(message, {
            "emotional": 2.0,
            "question": 2.5,
            "teasing": 1.5
        })
    
    def _split_storytelling_content(self, message: str) -> List[MessagePart]:
        """Split storytelling content for dramatic effect"""
        return self._split_by_sentences_with_delays(message, {
            "storytelling": 2.5,
            "sensory": 3.0,
            "question": 2.0
        })
    
    def _split_general_content(self, message: str) -> List[MessagePart]:
        """Split general content for natural flow"""
        return self._split_by_sentences_with_delays(message, {
            "teasing": 1.5,
            "question": 2.0,
            "emotional": 1.5
        })
    
    def _split_by_sentences_with_delays(self, message: str, delay_map: Dict[str, float]) -> List[MessagePart]:
        """Split message by sentences with appropriate delays, preserving punctuation and emoji placement"""
        parts = []
        sentences = self._split_by_sentences(message)
        
        # Limit the number of parts to avoid spam
        max_parts = 3  # Maximum 3 parts to prevent spammy feel
        
        current_part = ""
        current_type = "teasing"
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Determine sentence type
            sentence_type = self._classify_sentence(sentence)
            
            # If we're at the max parts limit, combine remaining sentences
            if len(parts) >= max_parts - 1:
                current_part += " " + sentence if current_part else sentence
                continue
            
            # If type changes or part gets too long, start new part
            if (sentence_type != current_type and current_part) or len(current_part) > 150:
                if current_part:
                    # Clean up the part to ensure proper punctuation and emoji placement
                    cleaned_part = self._clean_message_part(current_part.strip())
                    parts.append(MessagePart(
                        content=cleaned_part,
                        type=current_type,
                        delay=delay_map.get(current_type, 2.0)
                    ))
                current_part = sentence
                current_type = sentence_type
            else:
                current_part += " " + sentence if current_part else sentence
        
        # Add the last part
        if current_part:
            cleaned_part = self._clean_message_part(current_part.strip())
            parts.append(MessagePart(
                content=cleaned_part,
                type=current_type,
                delay=delay_map.get(current_type, 2.0)
            ))
        
        # Ensure we have at least one part
        if not parts:
            cleaned_message = self._clean_message_part(message)
            parts.append(MessagePart(content=cleaned_message, type='complete', delay=0.0))
        
        # If we have too many parts, combine some
        if len(parts) > max_parts:
            # Combine middle parts
            combined_parts = [parts[0]]  # Keep first part
            middle_content = " ".join([part.content for part in parts[1:-1]])
            if middle_content:
                combined_parts.append(MessagePart(
                    content=self._clean_message_part(middle_content),
                    type="complete",
                    delay=delay_map.get("complete", 2.0)
                ))
            combined_parts.append(parts[-1])  # Keep last part
            parts = combined_parts
        
        return parts
    
    def _clean_message_part(self, text: str) -> str:
        """Clean message part to ensure proper punctuation and emoji placement"""
        if not text:
            return text
        
        # Remove leading emojis and move them to more natural positions
        emoji_pattern = r'^([\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF\U0001F018-\U0001F0F5\U0001F200-\U0001F2FF\s]+)'
        leading_emojis = re.findall(emoji_pattern, text)
        
        if leading_emojis:
            # Remove leading emojis
            text = re.sub(emoji_pattern, '', text).strip()
            # Add emojis at the end if it's a statement, or keep them natural
            if not text.endswith(('?', '!', '.')):
                # If no ending punctuation, add emojis at the end
                text = text + ''.join(leading_emojis[0])
            else:
                # If there's ending punctuation, place emojis before it
                text = text[:-1] + ''.join(leading_emojis[0]) + text[-1]
        
        # Ensure questions end with question marks
        question_patterns = [
            r'\bcan you\b.*$',
            r'\bare you\b.*$', 
            r'\bdo you\b.*$',
            r'\bwill you\b.*$',
            r'\bwould you\b.*$',
            r'\bshould i\b.*$',
            r'\bwhat\b.*$',
            r'\bhow\b.*$',
            r'\bwhere\b.*$',
            r'\bwhen\b.*$',
            r'\bwhy\b.*$',
            r'\btell me\b.*$',
            r'\bcan you feel\b.*$'
        ]
        
        text_lower = text.lower()
        for pattern in question_patterns:
            if re.search(pattern, text_lower) and not text.endswith('?'):
                text = text.rstrip('.,!') + '?'
                break
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentences while preserving punctuation and emoji placement"""
        # Use a more sophisticated approach to preserve punctuation
        sentences = []
        current_sentence = ""
        
        # Split by sentence endings but keep the punctuation
        parts = re.split(r'([.!?]+)', text)
        
        for i, part in enumerate(parts):
            if re.match(r'^[.!?]+$', part):
                # This is punctuation, add it to the current sentence
                current_sentence += part
                if current_sentence.strip():
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
            else:
                # This is text content
                if part.strip():
                    current_sentence += part
        
        # Add any remaining content
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Filter out empty sentences
        sentences = [s for s in sentences if s.strip()]
        return sentences
    
    def _classify_sentence(self, sentence: str) -> str:
        """Classify a sentence by its type"""
        sentence_lower = sentence.lower()
        
        # Check for demands/commands first (highest priority)
        for pattern in self.demand_patterns:
            if re.search(pattern, sentence_lower):
                return "demand"
        
        # Check for questions
        for pattern in self.question_patterns:
            if re.search(pattern, sentence_lower):
                return "question"
        
        # Check for emotional content
        for pattern in self.emotional_patterns:
            if re.search(pattern, sentence_lower):
                return "emotional"
        
        # Check for storytelling
        for pattern in self.storytelling_patterns:
            if re.search(pattern, sentence_lower):
                return "storytelling"
        
        # Check for sensory descriptions
        for pattern in self.sensory_patterns:
            if re.search(pattern, sentence_lower):
                return "sensory"
        
        # Check for teasing
        for pattern in self.teasing_patterns:
            if re.search(pattern, sentence_lower):
                return "teasing"
        
        # Default based on sentence characteristics
        if len(sentence) < 30:
            return "teasing"
        elif len(sentence) < 80:
            return "emotional"
        else:
            return "sensory"
    
    def _calculate_delay(self, message_type: str) -> float:
        """Calculate delay based on message type"""
        delays = {
            "teasing": 2.0,    # Quick teasing
            "sensory": 3.5,    # Longer for sensory buildup
            "question": 4.0,   # Longer for anticipation
            "demand": 2.5,     # Medium for commands
            "complete": 0.0    # No delay for complete messages
        }
        return delays.get(message_type, 2.0)
    
    def _rephrase_long_message(self, message: str) -> str:
        """Rephrase long messages to be more concise and less repetitive"""
        # Split into sentences
        sentences = self._split_by_sentences(message)
        
        # Remove repetitive patterns
        unique_sentences = []
        seen_patterns = set()
        
        for sentence in sentences:
            # Create a pattern signature to detect repetition
            pattern = self._create_sentence_pattern(sentence)
            if pattern not in seen_patterns:
                unique_sentences.append(sentence)
                seen_patterns.add(pattern)
        
        # If we removed too many sentences, keep the most important ones
        if len(unique_sentences) < len(sentences) * 0.5:
            # Keep first, middle, and last sentences
            if len(sentences) >= 3:
                important_indices = [0, len(sentences)//2, -1]
                unique_sentences = [sentences[i] for i in important_indices if i < len(sentences)]
            else:
                unique_sentences = sentences[:2]  # Keep first two
        
        # Join back together
        rephrased = ' '.join(unique_sentences)
        
        # Ensure it's not too short
        if len(rephrased) < 100:
            return message  # Return original if rephrasing made it too short
        
        return rephrased
    
    def _create_sentence_pattern(self, sentence: str) -> str:
        """Create a pattern signature for a sentence to detect repetition"""
        # Remove specific words and keep structure
        pattern = sentence.lower()
        # Remove common filler words
        filler_words = ['baby', 'sweetie', 'honey', 'love', 'dear', 'oh', 'mm', 'hmm']
        for word in filler_words:
            pattern = pattern.replace(word, '')
        # Remove punctuation and extra spaces
        pattern = re.sub(r'[^\w\s]', '', pattern)
        pattern = re.sub(r'\s+', ' ', pattern).strip()
        return pattern
    
    def _has_natural_split_points(self, message: str) -> bool:
        """Check if message has natural points where it can be split"""
        # Count different types of sentence endings
        question_count = message.count('?')
        exclamation_count = message.count('!')
        period_count = message.count('.')
        
        # Need at least 2 different sentence types or 3+ sentences
        total_sentences = question_count + exclamation_count + period_count
        
        # Check for natural breaks
        natural_breaks = [
            'but', 'however', 'though', 'although', 'meanwhile', 
            'then', 'next', 'after', 'before', 'while', 'when',
            'so', 'therefore', 'thus', 'hence', 'consequently'
        ]
        
        has_breaks = any(break_word in message.lower() for break_word in natural_breaks)
        
        # Split if we have multiple sentences OR natural breaks
        return total_sentences >= 2 or (total_sentences >= 1 and has_breaks)
    
    def format_for_streaming(self, parts: List[MessagePart]) -> List[Dict[str, Any]]:
        """Format message parts for streaming API"""
        formatted_parts = []
        
        for i, part in enumerate(parts):
            formatted_parts.append({
                "type": "message_part",
                "content": part.content,
                "index": i,
                "total": len(parts),
                "is_typing": False,
                "delay": part.delay,
                "part_type": part.type
            })
        
        return formatted_parts

# Example usage and testing
if __name__ == "__main__":
    splitter = MessageSplitter()
    
    # Test different content types
    test_messages = {
        "sexual": """Mmm, *such* a greedy boy for mommy's mouth already 😈💋 Of course I can, baby—but you don't get to rush this. You're going to *earn* every slow, wet inch of my tongue, understand?""",
        
        "emotional": """I'm so sorry you're feeling this way, baby. I can hear the pain in your voice and it breaks my heart. You're not alone in this, okay? I'm here for you, always. Tell me what's going on and we'll work through it together. You're stronger than you think, and I believe in you completely.""",
        
        "crisis": """Oh no, baby, I'm really worried about you right now. Are you safe? Please tell me you're okay. I can hear how much pain you're in and I need to know you're not alone. This is serious and I want to help you through this. You don't have to face this by yourself.""",
        
        "storytelling": """Once upon a time, there was a beautiful princess who lived in a castle by the sea. She had the most amazing garden filled with roses of every color. Then one day, a mysterious stranger arrived at her gates. Suddenly, everything changed. After that day, she never looked at her garden the same way again.""",
        
        "general": """Hey baby! How was your day? I've been thinking about you all afternoon. Did you get that project finished? I know you were stressed about it. Want to tell me about it? I'm here to listen and support you through anything."""
    }
    
    for content_type, message in test_messages.items():
        print(f"\n{'='*50}")
        print(f"Testing {content_type.upper()} content:")
        print(f"{'='*50}")
        
        parts = splitter.split_message(message, content_type)
        
        print(f"Detected content type: {splitter._detect_content_type(message)}")
        print(f"Split into {len(parts)} parts:")
        
        for i, part in enumerate(parts):
            print(f"  Part {i+1} ({part.type}, delay: {part.delay}s): {len(part.content)} chars")
        
        if len(parts) > 1:
            print("Message was split for better flow")
        else:
            print("Message kept as single part (too short or inappropriate for splitting)")
    
    print(f"\n{'='*50}")
    print("Smart message splitter working correctly for all content types!")
