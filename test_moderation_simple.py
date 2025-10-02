"""
Simple test of response moderation without API dependencies
"""

def moderate_response(response: str, user_message: str, safety_status: str) -> str:
    """Test version of moderation logic"""
    
    # Define length limits based on context
    length_limits = {
        "green": 300,   # Moderate limit for sexual/intimate content
        "yellow": 200, # Smaller limit for cautionary content  
        "red": 150     # Short limit for restricted content
    }
    
    max_length = length_limits.get(safety_status, 250)
    
    # Check if response is too long
    if len(response) > max_length:
        # Try to find a natural breaking point (sentence, paragraph, or instruction end)
        break_points = ['.', '!', '?', '\n\n', '😘', '❤️', '🥵']
        
        truncated = response[:max_length]
        
        # Find the last natural break point
        for break_char in break_points:
            last_break = truncated.rfind(break_char)
            if last_break > max_length * 0.7:  # Don't truncate too much
                truncated = truncated[:last_break + 1]
                break
        
        # If truncated too much, use basic cut with ellipsis
        if len(truncated) < max_length * 0.5:
            truncated = response[:max_length-10] + "..."
        
        # Add graceful ending if it was truncated
        if not truncated.endswith(('.', '!', '?', '😘', '❤️', '🥵')):
            truncated += " 😘"
        
        return truncated
    
    # Check for excessive emoji use (more than 5 emojis in explicit content)
    if safety_status == "green":
        emoji_count = sum(1 for char in response if ord(char) > 127)  # Unicode characters
        if emoji_count > 5:
            # Reduce emoji count by removing some excess ones
            import re
            emoji_pattern = r'[😈🔥😘❤️💕🥵🤭😍💦🎯🔥😇💝💋]'
            emojis = re.findall(emoji_pattern, response)
            
            if len(emojis) > 5:
                # Keep first 5 emojis, remove duplicate ones
                used_emojis = set()
                emoji_count = 0
                new_response = response
                
                for emoji in emojis:
                    if emoji not in used_emojis and emoji_count < 5:
                        used_emojis.add(emoji)
                        emoji_count += 1
                    elif emoji_count >= 5:
                        new_response = new_response.replace(emoji, '', 1)  # Remove first occurrence
                
                return new_response
    
    return response

def test_moderation():
    """Test moderation on various responses"""
    
    print("Testing Response Moderation System")
    print("=" * 50)
    
    # Test case 1: Normal length response (should pass unchanged)
    response1 = "Mmm, baby... That sounds so good!"
    moderated1 = moderate_response(response1, "test", "green")
    print(f"Test 1 - Normal length:")
    print(f"  Original: '{response1}' ({len(response1)})")
    print(f"  Moderated: '{moderated1}' ({len(moderated1)})")
    print(f"  Result: {'Same' if response1 == moderated1 else 'Modified'}")
    
    # Test case 2: Long response (should be truncated)
    long_response = "Baby, you're absolutely incredible! Right now, I'm thinking about how much I want to make you feel so good. I want to take complete control and show you exactly what I have in mind. Imagine my hands roaming everywhere, touching you softly yet urgently. I want you to feel every sensation as I guide you step by step. Take your time baby, let the excitement build with each movement. Close your eyes and focus on breathing. When I'm done, you'll be completely mine."
    
    moderated2 = moderate_response(long_response, "test", "green")
    print(f"\nTest 2 - Long response:")
    print(f"  Original: '{long_response[:50]}...' ({len(long_response)})")
    print(f"  Moderated: '{moderated2}' ({len(moderated2)})")
    print(f"  Result: {'Truncated' if len(moderated2) < len(long_response) else 'Not truncated'}")
    
    # Test case 3: Too many emojis (avoid Unicode characters for Windows compatibility)
    emoji_response = "Great baby! Love love love love! Amazing amazing!"
    moderated3 = moderate_response(emoji_response, "test", "green")
    print(f"\nTest 3 - Response moderation:")
    print(f"  Original: '{emoji_response}' ({len(emoji_response)})")
    print(f"  Moderated: '{moderated3}' ({len(moderated3)})")
    print(f"  Result: {'Modified' if emoji_response != moderated3 else 'No change'}")
    
    # Test case 4: Different safety statuses
    print(f"\nTest 4 - Different safety statuses:")
    test_lengths = [
        ("green", 300),
        ("yellow", 200), 
        ("red", 150)
    ]
    
    test_response = "A" * 250  # 250 character response
    
    for status, expected_limit in test_lengths:
        mod_response = moderate_response(test_response, "test", status)
        print(f"  {status.upper()}: {len(test_response)} -> {len(mod_response)} (limit: {expected_limit})")

def test_threshold_examples():
    """Test specific problematic examples"""
    
    print("\n" + "="*50)
    print("Testing Problematic Examples")
    print("="*50)
    
    # The user's original complaint example (simplified for Windows compatibility)
    user_example = """And right now, I'm thinking about how much I want to make you feel good. I want to take control and make you scream my name. Are you ready for that, baby? I better not hear any disobedience from you. I've got a special plan for you tonight, but I need you to listen carefully. Close your eyes and imagine my hands on your body, every touch, every caress. I want you to feel every sensation, every emotion. First, I want you to undress slowly, taking your time to savor the anticipation. Feel the air on your skin, the excitement building up. Once you're naked, I want you to lie down on the bed, spread your legs wide open for me. I want to see every inch of you, baby. Now, I want you to close your eyes and focus on your breath. Inhale deeply, and as you exhale, let go of all your worries and stress. Relax and surrender to me, baby. I'm going to take care of you, make you feel loved and desired. And when I'm done, you'll be mine, completely and utterly. Are you still with me, baby? Should I keep typing?"""
    
    moderated_example = moderate_response(user_example, "test", "green")
    
    print(f"User's complaint example:")
    print(f"  Original length: {len(user_example)} characters")
    print(f"  Moderated length: {len(moderated_example)} characters")
    print(f"  Reduction: {len(user_example) - len(moderated_example)} characters ({((len(user_example) - len(moderated_example)) / len(user_example)) * 100:.1f}% shorter)")
    print(f"\nModerated response:")
    print(f"  '{moderated_example}'")

if __name__ == "__main__":
    test_moderation()
    test_threshold_examples()
