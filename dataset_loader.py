"""
Dataset loader for few-shot learning
"""

import json
import random
import os
from typing import List, Dict, Any

class DatasetLoader:
    """Load and retrieve examples from the girlfriend dataset"""
    
    def __init__(self, dataset_path='girlfriend_dataset_clean.jsonl'):
        self.dataset_path = dataset_path
        self.examples = []
        self.load_dataset()
    
    def load_dataset(self):
        """Load the dataset from file"""
        if not os.path.exists(self.dataset_path):
            print(f"Warning: Dataset file {self.dataset_path} not found")
            return
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        self.examples.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        print(f"Loaded {len(self.examples)} examples from dataset")
    
    def get_relevant_examples(self, user_message: str, num_examples: int = 5) -> List[Dict[str, Any]]:
        """Get relevant examples based on user message"""
        if not self.examples:
            return []
        
        user_lower = user_message.lower()
        relevant = []
        
        # Find examples with matching keywords
        for example in self.examples:
            user_content = example['messages'][0]['content'].lower()
            # Simple keyword matching
            matching_words = sum(1 for word in user_lower.split() if word in user_content)
            if matching_words > 0:
                relevant.append((matching_words, example))
        
        # Sort by relevance and take top examples
        relevant.sort(key=lambda x: x[0], reverse=True)
        relevant_examples = [ex[1] for ex in relevant[:num_examples]]
        
        # If not enough relevant examples, add random ones
        if len(relevant_examples) < num_examples:
            remaining = num_examples - len(relevant_examples)
            available = [ex for ex in self.examples if ex not in relevant_examples]
            if available:
                relevant_examples.extend(random.sample(available, min(remaining, len(available))))
        
        return relevant_examples
    
    def format_examples_for_prompt(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples for inclusion in the prompt"""
        if not examples:
            return ""
        
        formatted = "EXAMPLE CONVERSATIONS:\n\n"
        for i, example in enumerate(examples, 1):
            user_msg = example['messages'][0]['content']
            assistant_msg = example['messages'][1]['content']
            formatted += f"Example {i}:\n"
            formatted += f"User: {user_msg}\n"
            formatted += f"You: {assistant_msg}\n\n"
        
        return formatted
    
    def get_random_examples(self, num_examples: int = 3) -> List[Dict[str, Any]]:
        """Get random examples for general conversation patterns"""
        if not self.examples:
            return []
        
        return random.sample(self.examples, min(num_examples, len(self.examples)))
    
    def get_examples_by_category(self, category: str, num_examples: int = 3) -> List[Dict[str, Any]]:
        """Get examples by category (greeting, sexual, emotional, etc.)"""
        if not self.examples:
            return []
        
        # Simple keyword-based categorization
        category_keywords = {
            'greeting': ['hi', 'hello', 'hey', 'good morning', 'good night'],
            'sexual': ['horny', 'hard', 'cum', 'touch', 'kiss', 'fuck'],
            'emotional': ['sad', 'happy', 'stressed', 'lonely', 'love', 'miss'],
            'casual': ['doing', 'work', 'study', 'tired', 'bored', 'hungry'],
            'intimate': ['close', 'cuddle', 'hold', 'safe', 'peaceful']
        }
        
        if category not in category_keywords:
            return self.get_random_examples(num_examples)
        
        keywords = category_keywords[category]
        relevant = []
        
        for example in self.examples:
            user_content = example['messages'][0]['content'].lower()
            if any(keyword in user_content for keyword in keywords):
                relevant.append(example)
        
        if not relevant:
            return self.get_random_examples(num_examples)
        
        return random.sample(relevant, min(num_examples, len(relevant)))
