"""
Test script for multi-turn conversation system
"""

import asyncio
import os
from conversation_script import MultiTurnConversationManager

async def test_multi_turn_conversation():
    """Test the multi-turn conversation system"""
    
    print("Testing Multi-Turn Conversation System...")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not set. Test may fail.")
    
    # Create conversation manager
    manager = MultiTurnConversationManager()
    
    # Test script sequence
    print("\n" + "="*60)
    print("TESTING SCRIPT SEQUENCE")
    print("="*60)
    
    test_script = [
        "hey baby! can i ask you a question?",
        "are u sure?",
        "promise u won't tell anyone?",
        "okkkii i went to the store today",
        "can i tell you more?"
    ]
    
    # Mock user responses for testing
    test_responses = [
        "sure",
        "yes",
        "i promise",
        "tell me",
        "yes please"
    ]
    
    async def mock_input():
        if test_responses:
            response = test_responses.pop(0)
            print(f"You: {response}")
            return response
        return ""
    
    success = await manager.script_manager.run_script_sequence(
        test_script, 
        user_input_callback=mock_input
    )
    
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")
    
    # Test stop detection
    print("\n" + "="*60)
    print("TESTING STOP DETECTION")
    print("="*60)
    
    stop_script = [
        "hey baby! can i ask you a question?",
        "are u sure?",
        "promise u won't tell anyone?"
    ]
    
    stop_responses = [
        "sure",
        "no my dog died im not in the mood"
    ]
    
    async def mock_stop_input():
        if stop_responses:
            response = stop_responses.pop(0)
            print(f"You: {response}")
            return response
        return ""
    
    success = await manager.script_manager.run_script_sequence(
        stop_script,
        user_input_callback=mock_stop_input
    )
    
    print(f"\nStop test result: {'STOPPED CORRECTLY' if not success else 'FAILED TO STOP'}")

if __name__ == "__main__":
    asyncio.run(test_multi_turn_conversation())
