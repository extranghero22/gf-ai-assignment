"""
Test script for multi-turn conversation with the girlfriend agent
"""

import asyncio
import os
from girlfriend_agent import EnergyAwareGirlfriendAgent
from energy_analyzer import LLMEnergyAnalyzer
from conversation_context import ConversationContext

async def test_girlfriend_multi_turn():
    """Test the multi-turn conversation system with the girlfriend agent"""
    
    print("Testing Girlfriend Agent Multi-Turn Conversation...")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not set. Test may fail.")
    
    # Create girlfriend agent
    energy_analyzer = LLMEnergyAnalyzer()
    agent = EnergyAwareGirlfriendAgent(energy_analyzer=energy_analyzer)
    
    # Create conversation context
    context = ConversationContext()
    context.messages = []
    context.energy_history = []
    context.safety_status = "green"
    
    # Test script sequence
    print("\n" + "="*60)
    print("TESTING GIRLFRIEND AGENT SCRIPT SEQUENCE")
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
    
    success = await agent.generate_multi_turn_sequence(
        context=context,
        script_messages=test_script,
        user_input_callback=mock_input,
        safety_status="green"
    )
    
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")
    
    # Test stop detection
    print("\n" + "="*60)
    print("TESTING STOP DETECTION")
    print("="*60)
    
    # Reset context for stop test
    context.messages = []
    context.energy_history = []
    context.safety_status = "green"
    
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
    
    success = await agent.generate_multi_turn_sequence(
        context=context,
        script_messages=stop_script,
        user_input_callback=mock_stop_input,
        safety_status="green"
    )
    
    print(f"\nStop test result: {'STOPPED CORRECTLY' if not success else 'FAILED TO STOP'}")

if __name__ == "__main__":
    asyncio.run(test_girlfriend_multi_turn())
