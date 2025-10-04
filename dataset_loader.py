"""
Simple DatasetLoader for loading examples from girlfriend dataset files
"""

import json
import random
from typing import List, Dict, Any, Optional


class DatasetLoader:
    """Simple dataset loader for girlfriend conversation examples"""
    
    def __init__(self):
        self.examples = []
        self._load_dataset()
    
    def _load_dataset(self):
        """Load dataset from JSONL files"""
        try:
            # Try loading the clean dataset first
            with open('girlfriend_dataset_clean.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            example = json.loads(line.strip())
                            if isinstance(example, dict) and 'messages' in example:
                                self.examples.append(example)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            # Fallback to regular dataset
            try:
                with open('girlfriend_dataset.jsonl', 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                example = json.loads(line.strip())
                                if isinstance(example, dict) and 'messages' in example:
                                    self.examples.append(example)
                            except json.JSONDecodeError:
                                continue
            except FileNotFoundError:
                print("Warning: No dataset file found, using empty examples")
                self.examples = []
    
    def get_examples_by_category(self, category: str, num_examples: int = 3) -> List[Dict]:
        """Get examples by category"""
        # Since we don't have category tags, return random examples
        return self.get_random_examples(num_examples)
    
    def get_random_examples(self, num_examples: int = 3) -> List[Dict]:
        """Get random examples from dataset"""
        if not self.examples:
            return []
        
        return random.sample(self.examples, min(num_examples, len(self.examples)))
    
    def get_relevant_examples(self, user_message: str, num_examples: int = 3) -> List[Dict]:
        """Get examples relevant to user message"""
        # Simple keyword matching - could be improved
        user_lower = user_message.lower()
        
        # Keywords for different types of conversations
        sexual_keywords = ['horny', 'sexy', 'touch', 'kiss', 'love', 'need', 'want', 'feel']
        emotional_keywords = ['sad', 'lonely', 'miss', 'hurt', 'upset', 'worried']
        casual_keywords = ['hey', 'hi', 'what', 'how', 'doing', 'up', 'sup']
        
        relevant_examples = []
        
        # Try to find examples that match message content
        for example in self.examples:
            example_text = ' '.join([msg.get('content', '') for msg in example.get('messages', [])]).lower()
            
            if len(relevant_examples) >= num_examples:
                break
                
            # Check for keyword matches
            if any(word in user_lower for word in sexual_keywords) and any(word in example_text for word in sexual_keywords):
                relevant_examples.append(example)
            elif any(word in user_lower for word in emotional_keywords) and any(word in example_text for word in emotional_keywords):
                relevant_examples.append(example)
            elif any(word in user_lower for word in casual_keywords) and any(word in example_text for word in casual_keywords):
                relevant_examples.append(example)
        
        # If not enough relevant examples found, add random ones
        if len(relevant_examples) < num_examples:
            remaining_needed = num_examples - len(relevant_examples)
            random_examples = self.get_random_examples(remaining_needed)
            relevant_examples.extend(random_examples)
        
        return relevant_examples[:num_examples]
    
    def format_examples_for_prompt(self, examples: List[Dict]) -> str:
        """Format examples for use in prompts"""
        if not examples:
            return "No previous examples available."
        
        formatted_examples = []
        
        for example in examples:
            messages = example.get('messages', [])
            if not messages:
                continue
                
            conversation_parts = []
            for msg in messages:
                role = msg.get('role', '')
                content = msg.get('content', '')
                
                if role == 'user':
                    conversation_parts.append(f"User: {content}")
                elif role == 'assistant':
                    conversation_parts.append(f"You: {content}")
            
            if conversation_parts:
                formatted_examples.append('\n'.join(conversation_parts))
        
        return "\n\n".join(formatted_examples) if formatted_examples else "No examples available."
