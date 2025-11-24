"""
Conversation Memory System - Persistent storage for conversation history
Saves and loads conversations to/from JSON files for context continuity
"""

import json
import os
import time
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class ConversationMessage:
    """Single message in conversation history"""
    role: str  # 'user' or 'agent'
    content: str
    timestamp: float
    energy_level: Optional[str] = None
    emotion: Optional[str] = None
    is_ghost_message: bool = False
    is_script_message: bool = False


@dataclass
class ConversationHistory:
    """Full conversation history with metadata"""
    session_id: str
    created_at: str
    updated_at: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    total_messages: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": self.messages,
            "summary": self.summary,
            "total_messages": self.total_messages
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationHistory':
        return cls(
            session_id=data.get("session_id", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            messages=data.get("messages", []),
            summary=data.get("summary", ""),
            total_messages=data.get("total_messages", 0)
        )


class ConversationMemory:
    """
    Manages persistent conversation storage.
    Saves conversations to JSON and loads them as context for new sessions.
    """

    def __init__(self, storage_dir: str = "conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        # Main conversation file (accumulates all history)
        self.main_history_file = self.storage_dir / "conversation_history.json"

        # Current session data
        self.current_history: Optional[ConversationHistory] = None
        self.max_context_messages = 50  # Max messages to include in AI context
        self.auto_save_enabled = True

    def start_session(self, session_id: str) -> ConversationHistory:
        """Start a new session, loading existing history if available"""
        # Load existing history or create new
        existing = self.load_history()

        if existing:
            # Continue from existing history
            self.current_history = existing
            self.current_history.session_id = session_id
            self.current_history.updated_at = datetime.now().isoformat()
            print(f"Loaded {len(existing.messages)} messages from previous conversations")
        else:
            # Create new history
            self.current_history = ConversationHistory(
                session_id=session_id,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                messages=[],
                summary="",
                total_messages=0
            )
            print("Starting fresh conversation history")

        return self.current_history

    def add_message(self, role: str, content: str,
                    energy_level: str = None, emotion: str = None,
                    is_ghost_message: bool = False, is_script_message: bool = False):
        """Add a message to the current conversation"""
        if not self.current_history:
            print("Warning: No active session, message not saved")
            return

        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "energy_level": energy_level,
            "emotion": emotion,
            "is_ghost_message": is_ghost_message,
            "is_script_message": is_script_message
        }

        self.current_history.messages.append(message)
        self.current_history.total_messages += 1
        self.current_history.updated_at = datetime.now().isoformat()

        # Auto-save after each message
        if self.auto_save_enabled:
            self.save_history()

    def get_context_messages(self, max_messages: int = None) -> List[Dict[str, Any]]:
        """Get recent messages for AI context"""
        if not self.current_history:
            return []

        limit = max_messages or self.max_context_messages
        return self.current_history.messages[-limit:]

    def get_context_string(self, max_messages: int = None) -> str:
        """Get conversation context as a formatted string for AI prompt"""
        messages = self.get_context_messages(max_messages)

        if not messages:
            return "No previous conversation history."

        context_lines = []
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Hyunnie"
            content = msg["content"]
            context_lines.append(f"{role}: {content}")

        return "\n".join(context_lines)

    def save_history(self, filepath: str = None):
        """Save current conversation to JSON file"""
        if not self.current_history:
            return

        save_path = Path(filepath) if filepath else self.main_history_file

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_history.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"Conversation saved: {len(self.current_history.messages)} messages")
        except Exception as e:
            print(f"Error saving conversation: {e}")

    def load_history(self, filepath: str = None) -> Optional[ConversationHistory]:
        """Load conversation from JSON file"""
        load_path = Path(filepath) if filepath else self.main_history_file

        if not load_path.exists():
            return None

        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ConversationHistory.from_dict(data)
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return None

    def clear_history(self):
        """Clear all conversation history"""
        if self.main_history_file.exists():
            os.remove(self.main_history_file)

        self.current_history = None
        print("Conversation history cleared")

    def export_session(self, session_id: str = None) -> str:
        """Export current session to a separate file"""
        if not self.current_history:
            return None

        sid = session_id or self.current_history.session_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{sid}_{timestamp}.json"
        filepath = self.storage_dir / filename

        self.save_history(str(filepath))
        return str(filepath)

    def get_summary(self) -> str:
        """Get a summary of the conversation history"""
        if not self.current_history:
            return "No conversation history"

        total = self.current_history.total_messages
        user_msgs = sum(1 for m in self.current_history.messages if m["role"] == "user")
        agent_msgs = total - user_msgs

        return f"Total messages: {total} (User: {user_msgs}, Hyunnie: {agent_msgs})"

    def generate_context_summary(self, max_length: int = 500) -> str:
        """
        Generate a brief summary of older conversation for context.
        Useful when conversation is too long to include fully.
        """
        if not self.current_history or len(self.current_history.messages) < 10:
            return ""

        # Get older messages (beyond the recent context window)
        older_messages = self.current_history.messages[:-self.max_context_messages]

        if not older_messages:
            return ""

        # Simple summary: extract key topics mentioned
        topics = []
        for msg in older_messages:
            content = msg.get("content", "").lower()
            # Could be enhanced with actual NLP/LLM summarization
            if len(content) > 50:
                topics.append(content[:100] + "...")

        summary = f"Earlier in the conversation ({len(older_messages)} messages ago): "
        summary += " | ".join(topics[:5])  # First 5 topics

        return summary[:max_length]


# Global instance for easy access
_memory_instance: Optional[ConversationMemory] = None

def get_conversation_memory() -> ConversationMemory:
    """Get or create the global ConversationMemory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory()
    return _memory_instance
