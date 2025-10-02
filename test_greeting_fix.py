"""
Test the greeting pattern fix
"""

import re

def test_greeting_detection():
    """Test the improved greeting detection logic"""
    
    # Patterns for fast path
    simple_greetings_patterns = [
        r'\bhi\b', r'\bhello\b', r'\bhey\b', 
        r'\bgood morning\b', r'\bgood night\b', r'\bhow are you\b'
    ]
    
    test_cases = [
        # Should trigger fast path
        'hi',
        'hello', 
        'hey',
        'hey there',
        'hi buddy',
        'hello beautiful',
        
        # Should NOT trigger fast path
        'Oh really? Tell me what you think',
        'Tell me about your day',
        'What should I tell mommy',
        'Hello, how was your day? Something interesting happened.',
        'Hey there! I was thinking about what you said earlier.'
    ]
    
    print("Testing Fast Greeting Detection Fix")
    print("=" * 50)
    
    for message in test_cases:
        # Original logic
        simple_greetings = ["hi", "hello", "hey", "good morning", "good night", "how are you"]
        original_bug = any(greeting in message.lower() for greeting in simple_greetings)
        
        # New logic
        is_simple_greeting = any(
            re.search(pattern, message.lower()) 
            for pattern in simple_greetings_patterns
        ) and len(message.split()) <= 3
        
        print(f"Message: '{message}'")
        print(f"  Old logic (buggy): {original_bug}")
        print(f"  New logic (fixed): {is_simple_greeting}")
        print(f"  Word count: {len(message.split())}")
        
        if original_bug != is_simple_greeting:
            print(f"  -> FIXED!")
        print()

def test_specific_user_scenario():
    """Test the exact scenario from the user's conversation"""
    
    print("Testing User's Specific Scenario")
    print("=" * 40)
    
    messages = [
        "Heyy!",
        "Oh really? Tell me what you think"
    ]
    
    simple_greeting_patterns = [
        r'\bhi\b', r'\bhello\b', r'\bhey\b', 
        r'\bgood morning\b', r'\bgood night\b', r'\bhow are you\b'
    ]
    
    for message in messages:
        # Check if it would trigger fast path with new logic
        is_simple_greeting = any(
            re.search(pattern, message.lower()) 
            for pattern in simple_greeting_patterns
        ) and len(message.split()) <= 3
        
        print(f"Message: '{message}'")
        print(f"  Would use fast greeting: {is_simple_greeting}")
        print(f"  Would get contextual response: {not is_simple_greeting}")
        print()

if __name__ == "__main__":
    test_greeting_detection()
    test_specific_user_scenario()
