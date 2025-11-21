"""
Message Splitter Agent - Splits responses into multiple messages for realistic texting
Mimics natural texting behavior where people send multiple shorter messages instead of one long one
"""

import re
import random
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class MessageChunk:
    """A single message chunk with timing information"""
    content: str
    delay_before: float  # Seconds to wait before sending this chunk


class MessageSplitterAgent:
    """Splits long responses into multiple messages to simulate natural texting"""

    def __init__(self):
        # Splitting rules
        self.max_single_message_length = 100  # Characters
        self.min_chunk_length = 10  # Don't create tiny chunks

        # Typing speed simulation (characters per second)
        self.typing_speed_min = 15  # Slow typing
        self.typing_speed_max = 30  # Fast typing

        # Base delays between messages (seconds)
        self.base_delay_min = 0.3
        self.base_delay_max = 1.2

    def split_message(self, message: str, routing_path: str = None) -> List[MessageChunk]:
        """
        Split a message into multiple chunks for natural texting feel

        Args:
            message: The polished response to potentially split
            routing_path: The routing path (PATH_D should never be split)

        Returns:
            List of MessageChunk objects with content and timing
        """

        # Never split PATH_D (minimal responses like "nice 💪")
        if routing_path == "PATH_D":
            return [MessageChunk(content=message, delay_before=0.0)]

        # Don't split very short messages
        if len(message) <= self.max_single_message_length:
            return [MessageChunk(content=message, delay_before=0.0)]

        # Split the message intelligently
        chunks = self._split_intelligently(message)

        # Add timing delays to each chunk
        message_chunks = []
        for i, chunk_text in enumerate(chunks):
            if i == 0:
                # First chunk has no delay
                delay = 0.0
            else:
                # Calculate realistic typing delay based on previous chunk length
                delay = self._calculate_typing_delay(chunks[i-1])

            message_chunks.append(MessageChunk(
                content=chunk_text,
                delay_before=delay
            ))

        return message_chunks

    def _split_intelligently(self, message: str) -> List[str]:
        """
        Split message at natural break points (sentences, phrases)

        Strategy:
        1. Try to split at sentence boundaries (. ! ?)
        2. If sentences are too long, split at phrase boundaries (, ... -)
        3. Keep emojis with their sentence
        """

        chunks = []

        # First, try splitting at sentence boundaries
        sentences = re.split(r'([.!?]+\s*)', message)

        current_chunk = ""
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i+1] if i+1 < len(sentences) else ""

            full_sentence = sentence + punctuation

            # If adding this sentence keeps chunk under limit, add it
            if len(current_chunk + full_sentence) <= self.max_single_message_length:
                current_chunk += full_sentence
            else:
                # Current chunk is getting too long
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = full_sentence

        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        # If we still have chunks that are too long, split at phrases
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.max_single_message_length:
                # Split at commas or "..."
                phrase_chunks = self._split_at_phrases(chunk)
                final_chunks.extend(phrase_chunks)
            else:
                final_chunks.append(chunk)

        return final_chunks if final_chunks else [message]

    def _split_at_phrases(self, text: str) -> List[str]:
        """Split long text at phrase boundaries (commas, ellipsis, dashes)"""

        # Split at phrase boundaries
        phrases = re.split(r'(,\s*|\.\.\.\s*|-\s+)', text)

        chunks = []
        current_chunk = ""

        for i in range(0, len(phrases), 2):
            phrase = phrases[i]
            separator = phrases[i+1] if i+1 < len(phrases) else ""

            full_phrase = phrase + separator

            if len(current_chunk + full_phrase) <= self.max_single_message_length:
                current_chunk += full_phrase
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = full_phrase

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    def _calculate_typing_delay(self, previous_chunk: str) -> float:
        """
        Calculate realistic typing delay based on previous chunk length
        Simulates: read previous message + think + type next message
        """

        # Base delay (thinking time)
        base_delay = random.uniform(self.base_delay_min, self.base_delay_max)

        # Typing time (based on chunk length)
        chunk_length = len(previous_chunk)
        typing_speed = random.uniform(self.typing_speed_min, self.typing_speed_max)
        typing_time = chunk_length / typing_speed

        # Total delay (capped at reasonable maximum)
        total_delay = min(base_delay + (typing_time * 0.5), 3.0)

        return round(total_delay, 2)

    def format_chunks_for_display(self, chunks: List[MessageChunk]) -> str:
        """
        Format chunks for display/logging purposes
        Shows how messages will be sent with timing
        """

        if len(chunks) == 1:
            return chunks[0].content

        formatted = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                formatted.append(f"[Message 1]: {chunk.content}")
            else:
                formatted.append(f"[Message {i+1}] (after {chunk.delay_before}s): {chunk.content}")

        return "\n".join(formatted)
