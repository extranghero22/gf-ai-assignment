"""
Typing simulation system for realistic multi-message conversations
"""

import re
import asyncio
import random
from typing import List, Tuple, Optional, Callable

class TypingSimulator:
    """Simulates realistic typing patterns for multi-message conversations"""
    
    def __init__(self):
        # Typing speed variations (words per minute)
        self.fast_typing = 60  # Fast typing
        self.normal_typing = 40  # Normal typing
        self.slow_typing = 25  # Slow/thoughtful typing
        
        # Message splitting patterns
        self.sentence_endings = ['.', '!', '?', '...']
        self.thought_breaks = [',', ';', ' - ', '...']
        self.natural_pauses = ['um', 'uh', 'well', 'so', 'like', 'you know']
    
    def split_message_into_typing_sequence(self, message: str) -> List[str]:
        """
        Split a single message into multiple messages that simulate typing
        
        Args:
            message: The full message to split
            
        Returns:
            List of message parts that simulate typing
        """
        # Clean the message
        message = message.strip()
        
        # Split by sentences first
        sentences = self._split_by_sentences(message)
        
        # If no sentences found, try to split by natural breaks
        if not sentences or len(sentences) == 1:
            sentences = self._split_by_natural_breaks(message)
        
        # Further split long sentences
        parts = []
        for sentence in sentences:
            if len(sentence) > 50:  # Lower threshold for splitting
                sub_parts = self._split_long_sentence(sentence)
                parts.extend(sub_parts)
            else:
                parts.append(sentence)
        
        # Add typing indicators and natural pauses
        typing_sequence = self._add_typing_indicators(parts)
        
        return typing_sequence
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentences"""
        # Split by sentence endings but keep the punctuation
        pattern = r'([.!?]+)'
        parts = re.split(pattern, text)
        
        sentences = []
        current_sentence = ""
        
        for part in parts:
            if part.strip():
                if part in self.sentence_endings:
                    current_sentence += part
                    if current_sentence.strip():
                        sentences.append(current_sentence.strip())
                        current_sentence = ""
                else:
                    current_sentence += part
        
        # Add any remaining text
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        return sentences
    
    def _split_by_natural_breaks(self, text: str) -> List[str]:
        """Split text by natural break points like ellipses, commas, etc."""
        # Look for natural break points
        break_points = []
        
        # Find ellipses and multiple periods (more specific)
        for i in range(len(text) - 2):
            if text[i:i+3] == '...' or (text[i] == '.' and text[i+1] == '.' and i > 0):
                break_points.append(i + 3)
        
        # Find commas and other natural breaks
        for i, char in enumerate(text):
            if char in [',', ';'] and i > 0:  # Don't split at the very beginning
                break_points.append(i + 1)
        
        # Sort and deduplicate break points
        break_points = sorted(list(set(break_points)))
        
        # Split at break points
        parts = []
        start = 0
        
        for break_point in break_points:
            if break_point - start > 10:  # Only split if part is long enough
                part = text[start:break_point].strip()
                if part:
                    parts.append(part)
                start = break_point
        
        # Add remaining text
        if start < len(text):
            remaining = text[start:].strip()
            if remaining:
                parts.append(remaining)
        
        return parts if parts else [text]
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split long sentences at natural break points"""
        # Look for natural break points
        break_points = []
        
        # Find commas, semicolons, dashes
        for i, char in enumerate(sentence):
            if char in [',', ';'] or (char == '-' and i > 0 and i < len(sentence) - 1):
                break_points.append(i)
        
        # Find conjunctions
        conjunctions = [' and ', ' but ', ' so ', ' because ', ' or ', ' yet ']
        for conj in conjunctions:
            start = 0
            while True:
                pos = sentence.lower().find(conj, start)
                if pos == -1:
                    break
                break_points.append(pos + len(conj))
                start = pos + 1
        
        # Sort break points
        break_points.sort()
        
        # Split at break points
        parts = []
        start = 0
        
        for break_point in break_points:
            if break_point - start > 20:  # Only split if part is long enough
                part = sentence[start:break_point].strip()
                if part:
                    parts.append(part)
                start = break_point
        
        # Add remaining part
        if start < len(sentence):
            remaining = sentence[start:].strip()
            if remaining:
                parts.append(remaining)
        
        return parts if parts else [sentence]
    
    def _add_typing_indicators(self, parts: List[str]) -> List[str]:
        """Add typing indicators and natural pauses"""
        typing_sequence = []
        
        for i, part in enumerate(parts):
            # Skip empty or very short parts (just punctuation)
            if not part.strip() or len(part.strip()) <= 2 and part.strip() in ['.', '..', '...', '!', '?']:
                continue
                
            # Add the message part
            typing_sequence.append(part)
            
            # Add typing indicators for continuation (except last part)
            if i < len(parts) - 1:
                # Use more natural typing indicators, avoid standalone punctuation
                indicators = [
                    "typing...",
                    "one sec...",
                    "hold on...",
                    "let me think...",
                    "um...",
                    "well...",
                    "so..."
                ]
                
                # Choose indicator based on context
                if "?" in part:
                    indicator = random.choice(["thinking...", "let me think...", "um..."])
                elif "!" in part:
                    indicator = random.choice(["excited...", "omg...", "wow..."])
                elif len(part) < 20:
                    indicator = random.choice(["um...", "well...", "so..."])
                else:
                    indicator = random.choice(indicators)
                
                typing_sequence.append(indicator)
        
        return typing_sequence
    
    async def simulate_typing_sequence(self, 
                                     message: str, 
                                     message_callback: Optional[Callable] = None,
                                     delay_range: Tuple[float, float] = (0.5, 2.0)) -> List[str]:
        """
        Simulate typing a message with realistic delays
        
        Args:
            message: The full message to type
            message_callback: Function to call for each message part
            delay_range: Range of delays between messages (min, max) in seconds
            
        Returns:
            List of all message parts that were "typed"
        """
        # Split message into typing sequence
        typing_sequence = self.split_message_into_typing_sequence(message)
        
        typed_messages = []
        
        for i, part in enumerate(typing_sequence):
            # Add the message part
            typed_messages.append(part)
            
            # Call callback if provided
            if message_callback:
                await message_callback(part, i, len(typing_sequence))
            
            # Add delay between messages (except for the last one)
            if i < len(typing_sequence) - 1:
                # Calculate delay based on message length and type
                delay = self._calculate_typing_delay(part, delay_range)
                await asyncio.sleep(delay)
        
        return typed_messages
    
    def _calculate_typing_delay(self, message: str, delay_range: Tuple[float, float]) -> float:
        """Calculate realistic typing delay based on message content"""
        base_delay = random.uniform(delay_range[0], delay_range[1])
        
        # Adjust delay based on message characteristics
        if len(message) > 50:
            base_delay *= 1.2  # Longer messages take more time
        
        if "?" in message:
            base_delay *= 1.5  # Questions take time to think about
        
        if "!" in message:
            base_delay *= 0.8  # Exclamations are faster
        
        if "..." in message:
            base_delay *= 1.3  # Ellipses indicate thinking
        
        # Add some randomness
        base_delay *= random.uniform(0.8, 1.2)
        
        return max(0.3, min(3.0, base_delay))  # Clamp between 0.3 and 3.0 seconds

class MultiMessageGenerator:
    """Generates multiple messages that simulate natural conversation flow"""
    
    def __init__(self):
        self.typing_simulator = TypingSimulator()
    
    async def generate_typing_sequence(self, 
                                     full_message: str,
                                     message_callback: Optional[Callable] = None) -> List[str]:
        """
        Generate a sequence of messages that simulate typing
        
        Args:
            full_message: The complete message to break down
            message_callback: Function to call for each message part
            
        Returns:
            List of message parts
        """
        return await self.typing_simulator.simulate_typing_sequence(
            full_message, 
            message_callback
        )
    
    def create_conversation_flow(self, messages: List[str]) -> List[str]:
        """
        Create a natural conversation flow from multiple messages
        
        Args:
            messages: List of messages to create flow from
            
        Returns:
            List of messages with natural flow
        """
        flow = []
        
        for i, message in enumerate(messages):
            # Add the main message
            flow.append(message)
            
            # Add natural follow-ups or reactions
            if i < len(messages) - 1:  # Not the last message
                # Add natural reactions
                reactions = [
                    "you know?",
                    "right?",
                    "does that make sense?",
                    "what do you think?",
                    "are you with me?",
                    "you there?",
                    "still listening?",
                    "got it?",
                    "understand?",
                    "follow me?"
                ]
                
                # Choose reaction based on message content
                if "?" in message:
                    reaction = random.choice(["right?", "you know?", "does that make sense?"])
                elif "!" in message:
                    reaction = random.choice(["you there?", "still listening?", "got it?"])
                else:
                    reaction = random.choice(reactions)
                
                flow.append(reaction)
        
        return flow

# Example usage and testing
async def test_typing_simulation():
    """Test the typing simulation system"""
    
    print("Testing Typing Simulation System...")
    print("="*60)
    
    simulator = TypingSimulator()
    generator = MultiMessageGenerator()
    
    # Test message
    test_message = "Oh my god, baby... no. What? I'm so, so sorry. That is absolutely heartbreaking. I wish I could be there to just hold you right now. Are you at home? Please tell me you're not alone. I'm here, okay? Just talk to me."
    
    print(f"Original message: {test_message}")
    print("\nTyping sequence:")
    print("-" * 40)
    
    # Simulate typing
    async def message_callback(message_part, index, total):
        print(f"[{index+1}/{total}] {message_part}")
    
    typed_messages = await generator.generate_typing_sequence(
        test_message, 
        message_callback
    )
    
    print(f"\nTotal messages: {len(typed_messages)}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_typing_simulation())
