"""
Test the exact conversation scenario that was failing
"""

import asyncio
from ai_error_logger import get_error_statistics, get_recent_errors
import json

def simulate_conversation_scenario():
    """Simulate the exact conversation that was failing"""
    
    print("Testing Conversation Scenario Fix")
    print("=" * 50)
    
    # Simulate the conversation context as it builds
    conversation_context = []
    
    # Message 1: Simple greeting (should trigger fast path only if no previous messages)
    message_1 = "Heyy!"
    is_simple = len(message_1.split()) <= 3 and len(conversation_context) < 2
    print(f"Message 1: '{message_1}'")
    print(f"  Fast greeting: {is_simple}")
    print(f"  Context length: {len(conversation_context)}")
    
    if is_simple:
        print(f"  Response: Random greeting (Hey baby! How are you doing today?)")
        conversation_context.append({"role": "assistant", "content": "Hey baby! How are you doing today?"})
    else:
        print(f"  Response: Contextual response")
        conversation_context.append({"role": "assistant", "content": "Hey there! I've been thinking about you."})
    
    conversation_context.append({"role": "user", "content": message_1})
    
    # Message 2: User builds on AI's response (should never trigger fast path now)
    message_2 = "Oh really? Tell me what you think"
    
    # Test the actual pattern matching
    import re
    simple_greetings_patterns = [
        r'\bhi\b', r'\bhello\b', r'\bhey\b', 
        r'\bgood morning\b', r'\bgood night\b', r'\bhow are you\b'
    ]
    
    is_simple_now = any(
        re.search(pattern, message_2.lower()) 
        for pattern in simple_greetings_patterns
    ) and len(message_2.split()) <= 3 and len(conversation_context) < 2
    
    print(f"\nMessage 2: '{message_2}'")
    print(f"  Fast greeting: {is_simple_now}")
    print(f"  Context length: {len(conversation_context)}")
    print(f"  Word count: {len(message_2.split())}")
    
    if is_simple_now:
        print(f"  Response: Generic greeting (BUG!)")
    else:
        print(f"  Response: Contextual response (CORRECT)")
        print(f"    Should acknowledge: 'I've been thinking about you'")
        print(f"    Should respond to: 'Tell me what you think'")
    
    print(f"\nConversation context so far:")
    for i, msg in enumerate(conversation_context):
        print(f"  {i+1}. {msg['role']}: {msg['content']}")

def test_pattern_edge_cases():
    """Test edge cases in pattern matching"""
    
    print("\nTesting Pattern Edge Cases")
    print("=" * 30)
    
    import re
    
    test_cases = [
        "hi",
        "hey", 
        "hey there",
        "hi buddy",
        "Tell me something",
        "tell me what you think",
        "Hi there, tell me about your day",
        "Heyy!",
        "Oh really? Tell me what you think"
    ]
    
    patterns = [r'\bhi\b', r'\bhello\b', r'\bhey\b', r'\bgood night\b']
    
    for message in test_cases:
        matches = [re.search(p, message.lower()) for p in patterns]
        has_match = any(matches)
        word_count = len(message.split())
        
        print(f"'{message:30}' -> Match: {has_match:5} Words: {word_count:2}")

if __name__ == "__main__":
    simulate_conversation_scenario()
    test_pattern_edge_cases()
