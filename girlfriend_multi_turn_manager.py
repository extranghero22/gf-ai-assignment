"""
Multi-turn conversation manager for the girlfriend AI
"""

import asyncio
import os
from girlfriend_agent import EnergyAwareGirlfriendAgent
from energy_analyzer import LLMEnergyAnalyzer
from conversation_context import ConversationContext

class GirlfriendMultiTurnManager:
    """Manages multi-turn conversations with the girlfriend AI"""
    
    def __init__(self):
        self.energy_analyzer = LLMEnergyAnalyzer()
        self.agent = EnergyAwareGirlfriendAgent(energy_analyzer=self.energy_analyzer)
    
    async def start_conversation(self):
        """Start an interactive conversation with the girlfriend AI"""
        print("Welcome to the Girlfriend AI Multi-Turn Conversation System!")
        print("Type 'quit' or 'exit' to end the conversation")
        print("Type 'script' to run a predefined conversation sequence")
        print("Type 'chat' to start a free-form conversation")
        
        while True:
            print("\n" + "="*50)
            choice = input("Choose mode (script/chat/quit): ").strip().lower()
            
            if choice in ['quit', 'exit']:
                print("Goodbye!")
                break
            elif choice == 'script':
                await self._run_script_mode()
            elif choice == 'chat':
                await self._run_chat_mode()
            else:
                print("Invalid choice. Please enter 'script', 'chat', or 'quit'")
    
    async def _run_script_mode(self):
        """Run predefined conversation scripts"""
        print("\nAvailable conversation scripts:")
        print("1. Store Story (5 messages)")
        print("2. Intimate Confession (4 messages)")
        print("3. Comfort Session (3 messages)")
        print("4. Dominant Play (4 messages)")
        print("5. Sensual Experience (5 messages)")
        
        script_choice = input("Choose script (1-5): ").strip()
        
        if script_choice == "1":
            script = [
                "hey baby! can i ask you a question?",
                "are u sure?",
                "promise u won't tell anyone?",
                "okkkii i went to the store today",
                "can i tell you more?"
            ]
        elif script_choice == "2":
            script = [
                "baby, i need to tell you something important",
                "it's about how i feel about you",
                "i've been thinking about this for a while now",
                "i think i'm falling in love with you"
            ]
        elif script_choice == "3":
            script = [
                "hey sweetheart, how are you feeling?",
                "i can sense something's bothering you",
                "you know you can always talk to mommy about anything"
            ]
        elif script_choice == "4":
            script = [
                "baby, i want to play a little game with you",
                "are you ready to be a good boy for mommy?",
                "i need you to listen very carefully to what i say",
                "do you promise to do exactly as i tell you?"
            ]
        elif script_choice == "5":
            script = [
                "hey baby, i want to create something special for you",
                "close your eyes and imagine me lying next to you",
                "feel my fingers gently tracing patterns on your skin",
                "can you feel the warmth and connection between us?",
                "tell me what you're experiencing right now"
            ]
        else:
            print("Invalid script choice")
            return
        
        # Create conversation context
        context = ConversationContext()
        context.messages = []
        context.energy_history = []
        context.safety_status = "green"
        
        success = await self.agent.generate_multi_turn_sequence(
            context=context,
            script_messages=script,
            safety_status="green"
        )
        
        if success:
            print("Script completed successfully!")
        else:
            print("Script was interrupted")
    
    async def _run_chat_mode(self):
        """Run free-form conversation"""
        print("\nStarting free-form conversation...")
        print("The AI will send multiple messages and wait for your responses")
        
        context = ConversationContext()
        context.messages = []
        context.energy_history = []
        context.safety_status = "green"
        
        while True:
            # Generate AI response
            try:
                response, response_energy = await self.agent.generate_response(
                    context=context,
                    user_message="continue conversation",
                    safety_status="green"
                )
                
                print(f"\nAgent: {response}")
                context.messages.append({"role": "assistant", "content": response})
                
                # Get user response
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['quit', 'exit', 'stop']:
                    break
                
                context.messages.append({"role": "user", "content": user_input})
                
            except KeyboardInterrupt:
                print("\nConversation interrupted")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

async def main():
    """Main function to run the girlfriend multi-turn conversation system"""
    manager = GirlfriendMultiTurnManager()
    await manager.start_conversation()

if __name__ == "__main__":
    asyncio.run(main())
