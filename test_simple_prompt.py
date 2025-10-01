"""
Test with a very simple prompt to isolate the safety issue
"""

import asyncio
import os
import google.generativeai as genai
from girlfriend_agent import EnergyAwareGirlfriendAgent
from energy_analyzer import LLMEnergyAnalyzer
from conversation_context import ConversationContext

async def test_simple_prompt():
    """Test with a minimal prompt to see if Gemini works at all"""
    
    print("Testing simple prompt...")
    
    # Initialize Gemini directly
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-pro-preview-03-25")
    
    # Test 1: Very simple prompt
    simple_prompt = """You are a caring girlfriend. Respond to this message: "hi" """
    
    print("Test 1: Simple prompt")
    try:
        response = model.generate_content(simple_prompt)
        if response.candidates:
            print(f"Success: {response.text}")
        else:
            print("Blocked - no candidates")
            if hasattr(response, 'prompt_feedback'):
                print(f"Block reason: {response.prompt_feedback}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: With "mommy" term
    mommy_prompt = """You are a caring girlfriend who calls yourself "mommy". Respond to this message: "hi" """
    
    print("\nTest 2: With mommy term")
    try:
        response = model.generate_content(mommy_prompt)
        if response.candidates:
            print(f"Success: {response.text}")
        else:
            print("Blocked - no candidates")
            if hasattr(response, 'prompt_feedback'):
                print(f"Block reason: {response.prompt_feedback}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: With examples
    examples_prompt = """You are a caring girlfriend. Here are some examples:

User: hi
You: hey baby! how are you?

User: hello  
You: hi there sweetheart!

Now respond to: "hi" """
    
    print("\nTest 3: With examples")
    try:
        response = model.generate_content(examples_prompt)
        if response.candidates:
            print(f"Success: {response.text}")
        else:
            print("Blocked - no candidates")
            if hasattr(response, 'prompt_feedback'):
                print(f"Block reason: {response.prompt_feedback}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not set.")
    
    asyncio.run(test_simple_prompt())
