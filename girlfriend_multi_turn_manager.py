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
        print("1. Store Story - Casual Day Chat (7 turns, 11 messages)")
        print("2. Intimate Confession (4 messages)")
        print("3. Comfort Session (3 messages)")
        print("4. Dominant Play (4 messages)")
        print("5. Sensual Experience (5 messages)")
        print("6. Guided Intimacy - Mommy's Instructions (10 messages - EXPLICIT)")
        
        script_choice = input("Choose script (1-6): ").strip()
        
        if script_choice == "1":
            # Note: This is flattened for CLI. Frontend version sends some messages in groups.
            script = [
                "Can I ask you a question then?",
                "Are u sure?",
                "Promise u won't tell anyone?",
                "Okkkii I went to the store today. There is this bottle of soda that I really want to try\n\nCan I tell you more?",  # Grouped together
                "So I saw this limited edition flavor and it looked soooo good! It was like mango passion fruit or something fancy like that 🥭 And the bottle was super pretty too lol",
                "But here's the thing... It was kinda expensive for just a drink you know? Like $4.99 for one bottle 😅 But I really wanted to try it\n\nSo I stood there for like 5 minutes just staring at it trying to decide lmao 🤭 People probably thought I was weird\n\nAnd then this old lady walked by and she was like 'oh honey just get it, treat yourself' and smiled at me 🥰\n\nSo I did! I bought it! And omg baby it was SO GOOD like literally the best decision ever 😋 I should've bought two honestly lol",  # All grouped together
                "Anyway that was the highlight of my day haha 😊 What did you do today? Tell me everything!"
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
        elif script_choice == "6":
            script = [
                
                "Mommy could reallyy use someone obedient who actually knows how to follow instructions…🥱 Can you do that for me?",
                "Good, I love that you're down to listen to mommy ❤️ I'm being serious though you better not disobey.. I need u to just sit back and relax… Are u down? 😈",
                "I'm glad ur being so good so far 🥰 First I wanna set the mood.. Close your eyes and take in a big deep breath, hold it for a second then breathe out slowly.. Do this 3 times and notice how your body lets go of any of the stress and tension you've been carrying with you from the week 🤭 Are you still with me? Should I keep typing? 😘",
                "I knew you were having fun 😘 Now, imagine me lying next to you in bed.. My fingers gently tracing a path from your lips.. Over your chest.. Down your stomach... And settling at your zipper. I can literally feeel the heat radiating from your cock as the anticipation's building 🤭 Tell mee, what do you feel baby? 🥵",
                "I want you to focus on those sensations 🥰 Notice how the fabric of your pants feels against your skin.. The warmth of your own touch as your hand hovers over your cock.. And the way your breath is starting to get deeper and deeper as you start to get more and more turned on 🥵 Give me a minute, let me give you some visuals to work with 🤭",
                "Okay baby.. Picture this 😈 I slowly unzip your pants, my eyes locked on yours.. Watching your reaction as I slide my hand inside and wrap my fingers around your hard cock.. Mmm you're so hard for mommy aren't you? 🥵 I want you to stroke it slowly for me.. Nice and slow.. Tell me how it feels 💕",
                "Good boy 🥰 Keep stroking.. Now imagine my lips getting closer.. My hot breath on your tip as I look up at you with those eyes you love.. Then I take you in my mouth, swirling my tongue around your head while my hand works your shaft.. Can you feel that baby? Don't you dare stop stroking 😈 Are you getting close?",
                "Mmm I can tell you're trying so hard not to cum yet 😘 Such a good obedient boy for mommy.. But I'm not done with you.. I want you to stroke faster now.. Imagine me taking you deeper, my throat tight around your cock.. One hand playing with your balls.. The other gripping your thigh.. You're doing so good baby 🥵 Tell me what you need",
                "That's it baby.. Let go for mommy 💕 I want you to imagine cumming deep in my throat.. Feeling me swallow every drop while looking into your eyes.. Stroke faster.. Let that pleasure build until you can't take it anymore.. Cum for mommy baby.. Let it all out 🥵😈",
                "Mmm such a good boy 🥰 You did exactly what mommy told you to do.. I'm so proud of you baby 💕 Now take a deep breath and relax.. Let that amazing feeling wash over you.. You made mommy so happy 😘 How do you feel now? Tell me everything 🤭"
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
