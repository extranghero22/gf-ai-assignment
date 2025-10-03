"""
Test script for automatic sexual script triggering
This demonstrates how the app automatically detects sexual energy and triggers the guided intimacy script
"""

import asyncio
from enhanced_main import EnhancedMultiAgentConversation

async def test_auto_sexual_trigger():
    """Test automatic sexual script triggering"""
    
    print("="*60)
    print("TESTING AUTOMATIC SEXUAL SCRIPT TRIGGERING")
    print("="*60)
    print()
    print("This test will simulate a conversation where the user expresses")
    print("sexual interest, and the app should automatically detect it and")
    print("trigger the guided intimacy script.")
    print()
    print("="*60)
    print()
    
    # Create conversation system
    conversation = EnhancedMultiAgentConversation()
    
    # Start session
    await conversation.start_new_session()
    
    # Test messages that should trigger sexual script
    test_messages = [
        "Hey baby, I'm feeling really horny right now",
        "I want you so bad",
        "I'm so turned on thinking about you"
    ]
    
    print("\n" + "="*60)
    print("TEST SCENARIOS:")
    print("="*60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n\nTest {i}: User says: '{message}'")
        print("-" * 60)
        
        # Process the message
        await conversation.process_user_response(message)
        
        # Check if sexual flag was detected
        if conversation.energy_flags.get("status") == "sexual":
            print(f"\n✅ SUCCESS: Sexual energy detected!")
            print(f"   Reason: {conversation.energy_flags.get('reason')}")
            print(f"\n🔥 The guided intimacy script should have been triggered automatically!")
            break
        else:
            print(f"\n❌ Sexual energy not detected. Status: {conversation.energy_flags.get('status')}")
            print(f"   Will try next test message...")
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    print("\n🚀 Starting automatic sexual script trigger test...\n")
    asyncio.run(test_auto_sexual_trigger())

