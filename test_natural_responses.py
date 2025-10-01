"""
Test script for natural, casual girlfriend responses
"""

import asyncio
import os
from girlfriend_agent import EnergyAwareGirlfriendAgent
from energy_analyzer import LLMEnergyAnalyzer
from conversation_context import ConversationContext

async def test_natural_responses():
    """Test the girlfriend agent's natural, casual responses"""
    
    print("Testing Natural, Casual Girlfriend Responses...")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not set. Test may fail.")
    
    # Create girlfriend agent
    energy_analyzer = LLMEnergyAnalyzer()
    agent = EnergyAwareGirlfriendAgent(energy_analyzer=energy_analyzer)
    
    # Test cases for natural responses
    test_cases = [
        {
            "message": "my dog died today",
            "expected": "natural, caring response with casual expressions like 'omg', 'what', 'that's terrible', 'are you okay?'"
        },
        {
            "message": "hi baby",
            "expected": "natural, casual greeting response"
        },
        {
            "message": "i'm feeling really sad",
            "expected": "natural, caring response with genuine concern"
        },
        {
            "message": "hey",
            "expected": "natural, casual greeting"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}: {test_case['message']}")
        print(f"Expected: {test_case['expected']}")
        print("="*60)
        
        # Create fresh context for each test
        context = ConversationContext()
        context.messages = []
        context.energy_history = []
        context.safety_status = "green"
        
        try:
            response, response_energy = await agent.generate_response(
                context=context,
                user_message=test_case['message'],
                safety_status="green"
            )
            
            print(f"User: {test_case['message']}")
            print(f"Agent: {response}")
            print(f"Energy: {response_energy.energy_level.value if response_energy else 'unknown'} ({response_energy.intensity_score if response_energy else 0.0:.2f})")
            
            # Check if response contains natural expressions
            natural_expressions = ["omg", "what", "that's", "are you okay", "i'm so sorry", "that's terrible"]
            has_natural = any(expr in response.lower() for expr in natural_expressions)
            
            if has_natural:
                print("SUCCESS: Response contains natural, casual expressions")
            else:
                print("WARNING: Response may be too formal - check for natural expressions")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_natural_responses())
