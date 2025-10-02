"""
Test the regex fix for the "nothing to repeat at position 7" error
"""

import re

def test_regex_patterns():
    """Test the fixed greeting patterns"""
    
    # Fixed patterns
    simple_greetings_patterns = [
        r'\bhi\b', r'\bhello\b', r'\bhey\b', 
        r'\bgood morning\b', r'\bgood night\b', r'\bhow are you\b'
    ]
    
    test_strings = [
        'hey',
        'hey there', 
        'hey!',
        'The hey of the morning',
        'hi',
        'hello',
        'good morning',
        'tell me'
    ]
    
    print("Testing Fixed Regex Patterns")
    print("=" * 40)
    
    for test_string in test_strings:
        print(f"Testing: '{test_string}'")
        
        for pattern in simple_greetings_patterns:
            try:
                match = re.search(pattern, test_string.lower())
                if match:
                    print(f"  OK Pattern '{pattern}' matches")
                    break
            except re.error as e:
                print(f"  ERROR Pattern '{pattern}' ERROR: {e}")
        
        if not any(re.search(p, test_string.lower()) for p in simple_greetings_patterns):
            print(f"  No matches found")
        
        print()
    
    print("OK All patterns tested successfully - no regex errors!")

if __name__ == "__main__":
    test_regex_patterns()
