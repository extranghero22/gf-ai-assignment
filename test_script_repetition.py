# Test script repetition detection
"""
Test the script repetition detection functionality
"""

from ai_error_logger import log_conversation_disconnect

def simulate_conversation_scenario():
    """Simulate the exact scenario from the user's conversation"""
    
    # Create the conversation context that matches the user's issue
    context_messages = [
        {"role": "agent", "content": "Let's pack our bags and head there as soon as possible. I can already feel the sun on our skin and the sand between our toes. Are you ready for this little adventure? Let's make it happen, shall we?", "timestamp": "11:39:23"},
        {"role": "user", "content": "Yess!! Lets goo", "timestamp": "11:39:52"},
        {"role": "agent", "content": "Oh, I'm so excited, baby!", "timestamp": "11:40:05"},
        {"role": "agent", "content": "I can't wait to feel the sun on our skin and the sand between our toes.", "timestamp": "11:40:06"},  # REPETITIVE
        {"role": "agent", "content": "Let's pack our bags and head to that secluded beach right away. Are you ready for this little adventure? I know it's going to be amazing?", "timestamp": "11:40:09"}  # MAJOR REPETITION
    ]
    
    # Simulate checking the last message for script repetition
    recent_ai_messages = [
        msg.get('content', '') for msg in context_messages[-6:]
        if msg.get('role') == 'assistant'
    ]
    
    ai_response = context_messages[-1]['content']  # The problematic repeating message
    
    print("Testing Script Repetition Detection")
    print("=" * 50)
    
    print("AI Messages in conversation:")
    for i, msg in enumerate(recent_ai_messages):
        print(f"{i+1}. {msg[:60]}...")
    
    print(f"\nAnalyzing REPETITIVE response:")
    print(f"Message: '{ai_response}'")
    
    # Test the detection logic
    current_words = set(ai_response.lower().split())
    
    for j, prev_msg in enumerate(recent_ai_messages[:-1]):
        prev_words = set(prev_msg.lower().split())
        common_words = len(current_words & prev_words)
        overlap_ratio = common_words / len(current_words) if len(current_words) > 0 else 0
        
        print(f"\nComparison with message {j+1}:")
        print(f"  Shared words: {common_words}")
        print(f"  Overlap ratio: {overlap_ratio:.2%}")
        
        if len(current_words | prev_words) > 10 and overlap_ratio > 0.5:
            print(f"  ERROR REPETITION DETECTED!")
            return True
    
    print("  OK No repetition detected")
    return False

def test_repetition_thresholds():
    """Test different levels of repetition"""
    
    print("\n" + "="*50)
    print("Testing Repetition Thresholds")
    print("="*50)
    
    test_cases = [
        {
            "name": "Exact repetition",
            "msg1": "Let's pack our bags and head to that secluded beach right away",
            "msg2": "Let's pack our bags and head to that secluded beach right away", 
            "expected": True
        },
        {
            "name": "Heavy similarity",
            "msg1": "I can feel the sun on our skin and sand between our toes",
            "msg2": "Let's pack our bags and head to that secluded beach right away. I can already feel the sun on our skin",
            "expected": True
        },
        {
            "name": "Light similarity",
            "msg1": "This is about going to the beach for vacation",
            "msg2": "Let's pack our bags and head to that secluded beach right away",
            "expected": False
        },
        {
            "name": "Normal conversation",
            "msg1": "How are you feeling today",
            "msg2": "What would you like to do tonight",
            "expected": False
        }
    ]
    
    for case in test_cases:
        print(f"\nTesting: {case['name']}")
        
        current_words = set(case['msg2'].lower().split())
        prev_words = set(case['msg1'].lower().split())
        
        common_words = len(current_words & prev_words)
        overlap_ratio = common_words / len(current_words) if len(current_words) > 0 else 0
        total_words = len(current_words | prev_words)
        
        detected = (total_words > 10 and overlap_ratio > 0.5)
        
        print(f"  Overlap: {overlap_ratio:.1%} ({common_words} words)")
        print(f"  Total words: {total_words}")
        print(f"  Detected: {detected}")
        print(f"  Expected: {case['expected']}")
        
        if detected == case['expected']:
            print("  OK CORRECT")
        else:
            print("  ERROR WRONG")

if __name__ == "__main__":
    detected = simulate_conversation_scenario()
    
    print(f"\nSCENARIO RESULT:")
    if detected:
        print("OK Script repetition detection: WORKING")
        print("The AI would have logged this as a HIGH severity disconnect")
    else:
        print("ERROR Script repetition detection: NOT WORKING")
    
    test_repetition_thresholds()
