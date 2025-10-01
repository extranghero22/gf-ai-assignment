"""
Interactive demo of the multi-turn conversation system
"""

import asyncio
import os
from conversation_script import MultiTurnConversationManager

async def demo():
    """Run an interactive demo"""
    
    print("="*70)
    print("GIRLFRIEND AI MULTI-TURN CONVERSATION DEMO")
    print("="*70)
    print()
    print("This demo shows how the AI can send multiple messages")
    print("and wait for your responses between each one.")
    print()
    print("Example conversation flow:")
    print("1. Agent: 'hey baby! can i ask you a question?'")
    print("2. You: 'sure'")
    print("3. Agent: 'are u sure?'")
    print("4. You: 'yes'")
    print("5. Agent: 'promise u won't tell anyone?'")
    print("6. You: 'i promise'")
    print("7. Agent: 'okkkii i went to the store today'")
    print("8. You: 'tell me'")
    print("9. Agent: 'can i tell you more?'")
    print()
    print("The AI will detect if you want to continue or stop the conversation.")
    print("Try saying 'no my dog died im not in the mood' to see stop detection!")
    print()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY not set. Demo may not work properly.")
        print()
    
    input("Press Enter to start the demo...")
    
    # Create conversation manager
    manager = MultiTurnConversationManager()
    
    # Run the demo script
    demo_script = [
        "hey baby! can i ask you a question?",
        "are u sure?",
        "promise u won't tell anyone?",
        "okkkii i went to the store today",
        "can i tell you more?"
    ]
    
    print("\n" + "="*70)
    print("STARTING DEMO CONVERSATION")
    print("="*70)
    
    success = await manager.script_manager.run_script_sequence(demo_script)
    
    print("\n" + "="*70)
    if success:
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("The AI successfully sent multiple messages and waited for your responses.")
    else:
        print("DEMO INTERRUPTED")
        print("The AI detected that you wanted to stop the conversation.")
    print("="*70)
    
    print("\nKey features demonstrated:")
    print("✓ Multi-turn conversation flow")
    print("✓ User input between agent messages")
    print("✓ Context-aware response detection")
    print("✓ Automatic conversation stopping")
    print("✓ Few-shot learning from dataset")

if __name__ == "__main__":
    asyncio.run(demo())
