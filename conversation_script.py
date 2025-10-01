"""
Multi-turn conversation script system for girlfriend AI
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from girlfriend_agent import EnergyAwareGirlfriendAgent
from energy_analyzer import LLMEnergyAnalyzer
from conversation_context import ConversationContext

class ConversationScript:
    """Manages multi-turn conversation sequences"""
    
    def __init__(self, agent: EnergyAwareGirlfriendAgent):
        self.agent = agent
        self.context = ConversationContext()
        self.context.messages = []
        self.context.energy_history = []
        self.context.safety_status = "green"
        
    async def run_script_sequence(self, script_messages: List[str], 
                                 user_input_callback=None) -> bool:
        """
        Run a sequence of agent messages with user input between each
        
        Args:
            script_messages: List of messages the agent should send
            user_input_callback: Function to get user input (default: terminal input)
            
        Returns:
            bool: True if sequence completed, False if interrupted
        """
        if user_input_callback is None:
            user_input_callback = self._get_terminal_input
            
        print("\n" + "="*60)
        print("AGENT CONVERSATION SEQUENCE STARTED")
        print("="*60)
        
        for i, message in enumerate(script_messages):
            print(f"\n[Agent Message {i+1}/{len(script_messages)}]")
            print(f"Agent: {message}")
            
            # Add agent message to context
            self.context.messages.append({"role": "assistant", "content": message})
            
            # Get user response
            if i < len(script_messages) - 1:  # Don't ask for input after last message
                print("\nYour turn to respond:")
                user_response = await user_input_callback()
                
                if not user_response:
                    print("No input received, stopping sequence")
                    return False
                
                # Check if user wants to continue or stop
                should_continue = await self._analyze_user_response(user_response)
                if not should_continue:
                    print("User indicated they want to stop the conversation")
                    return False
                
                # Add user message to context
                self.context.messages.append({"role": "user", "content": user_response})
        
        print("\nConversation sequence completed successfully!")
        return True
    
    async def _analyze_user_response(self, user_response: str) -> bool:
        """
        Analyze user response to determine if conversation should continue
        
        Returns:
            bool: True to continue, False to stop
        """
        # Keywords that indicate the user wants to stop
        stop_keywords = [
            "stop", "no", "not in the mood", "don't want to", "can't", "won't",
            "died", "death", "sick", "hurt", "crisis", "emergency", "help",
            "depressed", "sad", "angry", "upset", "frustrated"
        ]
        
        user_lower = user_response.lower()
        
        # Check for stop indicators
        for keyword in stop_keywords:
            if keyword in user_lower:
                print(f"WARNING: Detected stop indicator: '{keyword}'")
                return False
        
        # Check for continue indicators
        continue_keywords = [
            "yes", "sure", "ok", "okay", "continue", "go on", "tell me",
            "please", "i want", "i'd like", "sounds good", "alright"
        ]
        
        for keyword in continue_keywords:
            if keyword in user_lower:
                print(f"Detected continue indicator: '{keyword}'")
                return True
        
        # Default to continue if unclear
        print("Ambiguous response, continuing conversation")
        return True
    
    async def _get_terminal_input(self) -> str:
        """Get user input from terminal"""
        try:
            return input("You: ").strip()
        except KeyboardInterrupt:
            print("\nConversation interrupted by user")
            return ""
        except EOFError:
            return ""

class MultiTurnConversationManager:
    """Manages multi-turn conversations with the girlfriend AI"""
    
    def __init__(self):
        self.energy_analyzer = LLMEnergyAnalyzer()
        self.agent = EnergyAwareGirlfriendAgent(energy_analyzer=self.energy_analyzer)
        self.script_manager = ConversationScript(self.agent)
    
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
        
        script_choice = input("Choose script (1-3): ").strip()
        
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
        else:
            print("Invalid script choice")
            return
        
        success = await self.script_manager.run_script_sequence(script)
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
    """Main function to run the multi-turn conversation system"""
    manager = MultiTurnConversationManager()
    await manager.start_conversation()

if __name__ == "__main__":
    asyncio.run(main())
