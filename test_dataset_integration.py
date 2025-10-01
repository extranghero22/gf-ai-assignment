"""
Test script for dataset integration with girlfriend agent
"""

import asyncio
import os
from dataset_loader import DatasetLoader
from girlfriend_agent import EnergyAwareGirlfriendAgent
from energy_analyzer import LLMEnergyAnalyzer
from conversation_context import ConversationContext

async def test_dataset_integration():
    """Test the dataset integration with sample conversations"""
    
    print("Testing Dataset Integration...")
    
    # Initialize components
    print("Loading dataset...")
    dataset_loader = DatasetLoader()
    
    print("Initializing energy analyzer...")
    energy_analyzer = LLMEnergyAnalyzer()
    
    print("Initializing girlfriend agent...")
    agent = EnergyAwareGirlfriendAgent(energy_analyzer=energy_analyzer)
    
    # Test dataset loading
    print(f"Dataset loaded with {len(dataset_loader.examples)} examples")
    
    # Test example retrieval
    test_messages = [
        "hi",
        "i am horny",
        "i am feeling stressed",
        "i love you",
        "good morning"
    ]
    
    print("\nTesting example retrieval:")
    for message in test_messages:
        examples = dataset_loader.get_relevant_examples(message, num_examples=3)
        print(f"\nMessage: '{message}'")
        print(f"Found {len(examples)} relevant examples:")
        for i, example in enumerate(examples, 1):
            user_msg = example['messages'][0]['content']
            assistant_msg = example['messages'][1]['content']
            print(f"  {i}. User: {user_msg}")
            print(f"     Assistant: {assistant_msg[:50]}...")
    
    # Test prompt building with examples
    print("\nTesting prompt building with examples:")
    context = ConversationContext()
    context.messages = []
    context.energy_history = []
    
    # Test with a sample message
    test_message = "hi baby"
    print(f"\nTesting with message: '{test_message}'")
    
    try:
        # This will test the prompt building (without actually calling Gemini)
        prompt = await agent._build_enhanced_prompt(
            context=context,
            user_energy=await energy_analyzer.analyze_message_energy(test_message),
            user_message=test_message,
            safety_status="green"
        )
        
        print("Prompt built successfully!")
        print(f"Prompt length: {len(prompt)} characters")
        
        # Check if examples are included
        if "EXAMPLE CONVERSATIONS:" in prompt:
            print("Examples found in prompt!")
        else:
            print("No examples found in prompt")
            
        # Show a snippet of the prompt
        print("\nPrompt snippet:")
        lines = prompt.split('\n')
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            print(f"{i+1:2d}: {line}")
        if len(lines) > 20:
            print(f"... ({len(lines) - 20} more lines)")
            
    except Exception as e:
        print(f"Error testing prompt building: {e}")
    
    print("\nDataset integration test completed!")

if __name__ == "__main__":
    # Set up environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not set. Some tests may fail.")
    
    # Run the test
    asyncio.run(test_dataset_integration())
