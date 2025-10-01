"""
Simple conversation test to demonstrate dataset integration
"""

import asyncio
import os
from girlfriend_agent import EnergyAwareGirlfriendAgent
from energy_analyzer import LLMEnergyAnalyzer
from conversation_context import ConversationContext

async def test_conversation():
    """Test a simple conversation with the dataset-enhanced agent"""
    
    print("Testing conversation with dataset integration...")
    
    # Initialize components
    energy_analyzer = LLMEnergyAnalyzer()
    agent = EnergyAwareGirlfriendAgent(energy_analyzer=energy_analyzer)
    
    # Create conversation context
    context = ConversationContext()
    context.messages = []
    context.energy_history = []
    context.safety_status = "green"
    
    # Test messages
    test_messages = [
        "hi",
        "how are you?",
        "i am feeling a bit lonely",
        "i love you"
    ]
    
    print("\nStarting conversation...")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTurn {i}:")
        print(f"User: {message}")
        
        try:
            # Generate response
            response, response_energy = await agent.generate_response(
                context=context,
                user_message=message,
                safety_status="green"
            )
            
            print(f"AI: {response}")
            
            # Update context
            context.messages.append({"role": "user", "content": message})
            context.messages.append({"role": "assistant", "content": response})
            context.current_energy = response_energy
            context.energy_history.append(response_energy)
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Conversation test completed!")

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not set. Test may fail.")
    
    asyncio.run(test_conversation())
