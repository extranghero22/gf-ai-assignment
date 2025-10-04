"""
Test the response moderation system
"""

from girlfriend_agent import EnergyAwareGirlfriendAgent

def test_response_moderation():
    """Test that response moderation works correctly"""
    
    print("Testing Response Moderation System")
    print("=" * 40)
    
    # Create agent instance
    agent = EnergyAwareGirlfriendAgent()
    
    # Create test responses of different lengths
    test_cases = [
        {
            "response": "Mmm, baby... 😘 That sounds so good ❤️ Let me tell you what I'm thinking... 😈",
            "context": "short_normal",
            "expected_length": 80,
            "safety_status": "green"
        },
        {
            "response": "Oh baby, you make me so wet! 😈 I want to make you feel so good right now... Let me guide you step by step. First, close your eyes and breathe deeply. Feel that arousal building inside you like electricity running through your veins. 🥵 I want you to imagine my hands everywhere, touching you so softly yet so urgently... ❤️",
            "context": "medium_long", 
            "expected_length": 250,
            "safety_status": "green"
        },
        {
            "response": "Baby, you're absolutely irresistible! 😈 Right now, I'm thinking about how much I want to make you feel incredible. I want to take complete control and show you exactly how much you mean to me. Let me tell you what I have in mind... Imagine my hands roaming your body, every single touch designed to drive you wild with desire. 🥵 I want you to undress slowly, feeling the anticipation build with each movement. Take your time, baby... Let the excitement wash over you. Once you're ready, lie down for me. Spread your legs wide open so I can see every beautiful inch of you. 😘 Close your eyes and focus on your breathing. Inhale deeply and let go of all stress and worry. Just surrender completely to me, baby. I'm going to take such good care of you tonight, making sure you feel loved, desired, and absolutely incredible. When I'm done with you, you'll be completely mine - every shiver, every moan, every plea will be because of me. ❤️🥵 Are you still with me, baby? Tell me what you're thinking... 😈",
            "context": "extremely_long",
            "expected_length": "should_be_truncated_to_300",
            "safety_status": "green"
        },
        {
            "response": "🥵😈❤️💕🥰😘🤭💦😍❤️🥵 Amazing baby! You're so incredible! 😈",
            "context": "too_many_emojis",
            "expected_length": "should_reduce_emojis",
            "safety_status": "green"  
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['context']}")
        print(f"Original response: '{test_case['response']}'")
        
        moderated = agent._moderate_response(
            test_case['response'], 
            "test message", 
            test_case['safety_status']
        )
        
        print(f"Moderated response: '{moderated}'")
        print(f"Original length: {len(test_case['response'])}")
        print(f"Moderated length: {len(moderated)}")
        print(f"Expected behavior: {test_case.get('expected_length', 'keep_as_is')}")
        
        # Check if moderation was applied
        if moderated != test_case['response']:
            print("✅ Response was moderated")
        else:
            print("➖ No moderation needed")

def test_length_thresholds():
    """Test specific length thresholds"""
    
    print("\n" + "="*50)
    print("Testing Length Thresholds")
    print("="*50)
    
    agent = EnergyAwareGirlfriendAgent()
    
    # Test different safety statuses
    safety_levels = ["green", "yellow", "red"]
    expected_limits = [300, 200, 150]
    
    for status, limit in zip(safety_levels, expected_limits):
        print(f"\nSafety Status: {status.upper()} (Limit: {limit} chars)")
        
        # Create a response slightly over the limit
        long_response = "Baby! " * (limit // 6) + "This is way too long!" 
        
        moderated = agent._moderate_response(long_response, "test", status)
        
        print(f"Original: {len(long_response)} chars")
        print(f"Moderated: {len(moderated)} chars")
        
        if len(moderated) <= limit:
            print("✅ Within limit")
        else:
            print("❌ Exceeded limit")

if __name__ == "__main__":
    test_response_moderation()
    test_length_thresholds()
