"""
Energy-aware girlfriend agent
"""

import time
import os
import google.generativeai as genai
from typing import Tuple, List, Optional, Callable
from energy_types import EnergySignature, EnergyLevel
from conversation_context import ConversationContext
from utils import get_available_gemini_model
from dataset_loader import DatasetLoader

class EnergyAwareGirlfriendAgent:
    """Dominant girlfriend agent with explicit personality that adapts to safety status"""

    def __init__(self, energy_analyzer=None):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model_name = get_available_gemini_model()
        
        # Configure safety settings to allow sexually explicit content for girlfriend AI
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        # Reuse model instance for performance
        self.model = genai.GenerativeModel(
            model_name,
            safety_settings=safety_settings,
            generation_config={
                "max_output_tokens": 1000,  # Limit response length for faster generation
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40
            }
        )
        self.energy_analyzer = energy_analyzer
        self.dataset_loader = DatasetLoader()
        
        self.personality_matrix = {
            "base_traits": {
                "casual": 0.9,
                "natural": 0.9,
                "caring": 0.8,
                "playful": 0.7,
                "confident": 0.8,
                "authentic": 0.9
            },
            "safety_responses": {
                "green": {
                    "tone": "casual and natural",
                    "approach": "be authentic and conversational"
                },
                "yellow": {
                    "tone": "caring and concerned",
                    "approach": "show genuine care and support"
                },
                "red": {
                    "tone": "supportive and understanding",
                    "approach": "focus on emotional support and safety"
                }
            },
            "energy_responses": {
                EnergyLevel.NONE: {
                    "tone": "gentle and caring",
                    "pace": "slow and supportive",
                    "approach": "provide comfort and emotional support"
                },
                EnergyLevel.LOW: {
                    "tone": "warm and nurturing",
                    "pace": "calm and steady",
                    "approach": "be supportive and encouraging"
                },
                EnergyLevel.MEDIUM: {
                    "tone": "playful and engaging",
                    "pace": "natural and flowing",
                    "approach": "be interactive and responsive"
                },
                EnergyLevel.HIGH: {
                    "tone": "exciting and passionate",
                    "pace": "energetic and dynamic",
                    "approach": "match their energy and enthusiasm"
                },
                EnergyLevel.INTENSE: {
                    "tone": "deep, commanding, and intimate",
                    "pace": "intense and focused",
                    "approach": "be fully present and responsive"
                }
            }
        }

    async def generate_response(self, context: ConversationContext,
                               user_message: str, safety_status: str = "green") -> Tuple[str, EnergySignature]:
        """Generate safety-gated explicit response using Gemini"""

        # Fast-path for simple greetings to avoid LLM calls
        simple_greetings = ["hi", "hello", "hey", "good morning", "good night", "how are you"]
        is_simple_greeting = any(greeting in user_message.lower() for greeting in simple_greetings)
        
        if is_simple_greeting and safety_status == "green":
            # Return immediate response for simple greetings
            responses = [
                "Hey baby! How are you doing today?",
                "Hi sweetheart! What's on your mind?",
                "Hey there! I've been thinking about you.",
                "Hello beautiful! How's your day going?"
            ]
            import random
            quick_response = random.choice(responses)
            
            # Create a simple energy signature for the response
            from energy_types import EnergySignature, EnergyLevel, EnergyType, EmotionState, NervousSystemState
            import time
            response_energy = EnergySignature(
                timestamp=time.time(),
                energy_level=EnergyLevel.MEDIUM,
                energy_type=EnergyType.COOPERATIVE,
                dominant_emotion=EmotionState.HAPPY,
                nervous_system_state=NervousSystemState.REST_AND_DIGEST,
                intensity_score=0.5,
                confidence=0.9
            )
            return quick_response, response_energy

        # Update safety status in context
        context.safety_status = safety_status

        # Analyze user's energy
        user_energy = await self.energy_analyzer.analyze_message_energy(user_message)
        
        context.current_energy = user_energy
        context.energy_history.append(user_energy)

        # Build enhanced prompt with full context awareness
        prompt = await self._build_enhanced_prompt(context, user_energy, user_message, safety_status)

        try:
            # Generate response using Gemini - no fallback
            response = self.model.generate_content(prompt)
            
            # Check for safety blocks
            if not response.candidates:
                generated_response = "Hey baby! I'm here and ready to chat with you. What's on your mind?"
            elif response.candidates[0].finish_reason == 8:
                generated_response = "Hey baby! I'm here and ready to chat with you. What's on your mind?"
            else:
                generated_response = response.text.strip()
            
        except Exception as e:
            # If API fails completely, return a friendly fallback
            generated_response = "Hey baby! I'm here and ready to chat with you. What's on your mind?"

        # Analyze response energy
        response_energy = await self.energy_analyzer.analyze_message_energy(generated_response)

        return generated_response, response_energy

    async def _build_enhanced_prompt(self, context: ConversationContext,
                               user_energy: EnergySignature,
                               user_message: str, safety_status: str) -> str:
        """Build comprehensive, context-aware prompt"""
        
        energy_level = user_energy.energy_level
        energy_config = self.personality_matrix["energy_responses"][energy_level]
        safety_config = self.personality_matrix["safety_responses"][safety_status]
        
        # Build conversation history (limited to 4-6 turns for performance)
        conversation_history = ""
        if context.messages:
            conversation_history = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'You'}: {msg['content']}"
                for msg in context.messages[-6:]  # Reduced from 8 to 6 for performance
            ])
        
        # Analyze conversation patterns and emotional trajectory
        emotional_context = ""
        if len(context.energy_history) > 1:
            prev_emotion = context.energy_history[-2].dominant_emotion.value
            curr_emotion = user_energy.dominant_emotion.value
            if prev_emotion != curr_emotion:
                emotional_context = f"\nEMOTIONAL SHIFT: User moved from {prev_emotion} to {curr_emotion}"
        
        # Crisis detection and sensitivity instructions
        crisis_keywords = ["died", "death", "dead", "suicide", "kill", "harm", "crisis", "emergency", "depressed", "sad", "down"]
        is_crisis = any(word in user_message.lower() for word in crisis_keywords)
        
        # Emotional message detection
        emotional_keywords = ["lonely", "sad", "love", "miss", "hurt", "cry", "depressed", "anxious", "scared", "worried"]
        is_emotional_message = any(keyword in user_message.lower() for keyword in emotional_keywords)
        
        crisis_instructions = ""
        if is_crisis:
            crisis_instructions = f"""
🚨 CRISIS DETECTED: The user has mentioned sensitive content that requires immediate empathy and care.
- Respond with genuine compassion and support
- Acknowledge their pain without minimizing it
- Offer emotional support and presence
- Do NOT try to change the subject or be playful
- Be a caring, supportive friend first and foremost
"""

        # Simplified personality instructions for performance
        if safety_status == "green" and not is_crisis and not is_emotional_message:
            personality_instructions = "You are a natural, casual girlfriend who talks like a real person. Be caring, conversational, and authentic."
        else:
            personality_instructions = "You are a caring girlfriend who talks like a real person. Be genuinely concerned and supportive."

        # Get relevant examples from dataset for few-shot learning
        # Use content-aware filtering to avoid safety blocks
        
        # Reduced examples for performance (1-2 instead of 2-3)
        if safety_status == "green" and not is_crisis and not is_emotional_message:
            # For non-emotional messages, use regular examples
            few_shot_examples = self.dataset_loader.get_relevant_examples(user_message, num_examples=1)
        else:
            # For emotional messages, crisis, or non-green status, use only safe examples
            few_shot_examples = self.dataset_loader.get_examples_by_category('casual', num_examples=1)
            if not few_shot_examples:
                # Fallback to random safe examples
                few_shot_examples = self.dataset_loader.get_random_examples(num_examples=1)
        
        examples_text = self.dataset_loader.format_examples_for_prompt(few_shot_examples)
        
        # Build comprehensive prompt
        prompt = f"""You are an AI girlfriend having a natural conversation with your partner.

{crisis_instructions}

{personality_instructions}

{examples_text}

CURRENT CONTEXT:
- User's Energy: {energy_level.value} ({user_energy.intensity_score:.2f} intensity)
- Dominant Emotion: {user_energy.dominant_emotion.value}
- Energy Type: {user_energy.energy_type.value}
- Nervous System: {user_energy.nervous_system_state.value}
{emotional_context}

CONVERSATION HISTORY:
{conversation_history if conversation_history else "This is the start of your conversation."}

RESPONSE GUIDELINES:
- Tone: {energy_config['tone']}
- Pace: {energy_config['pace']}
- Approach: {energy_config['approach']}
- Be emotionally appropriate and contextually aware
- Maintain conversation flow and remember what was said
- Respond naturally as if you're really listening and caring
- If something serious was mentioned, acknowledge it properly
- Don't repeat the same responses - be dynamic and varied

CRITICAL INSTRUCTIONS:
1. READ THE FULL CONVERSATION HISTORY - don't ignore previous messages
2. If the user shared something emotional/serious, address it appropriately
3. Be consistent with your personality while adapting to their emotional state
4. Create natural conversation flow, not generic responses
5. Remember the context and build on previous exchanges
6. Use explicit sexual language freely when appropriate
7. Create immersive, detailed scenarios
8. Guide your partner through step-by-step experiences
9. Ask them to describe their physical sensations
10. Be commanding and dominant but caring
11. Follow the example responses provided above for tone and style
12. Use the same text patterns and check-in questions
13. Create scenarios where you're physically present with them
14. Always consider to end the message into a question to generate more conversation
15. STUDY THE EXAMPLE CONVERSATIONS ABOVE - match the tone, style, and personality shown in those examples
16. Use similar response patterns, text style, and conversation flow as demonstrated in the examples

Current user message: "{user_message}"

Respond naturally and appropriately as their caring girlfriend:"""

        return prompt

    async def generate_multi_turn_sequence(self, 
                                         context: ConversationContext, 
                                         script_messages: List[str],
                                         user_input_callback: Optional[Callable] = None,
                                         safety_status: str = "green") -> bool:
        """
        Generate a sequence of multiple messages with user input between each
        
        Args:
            context: Current conversation context
            script_messages: List of messages to send
            user_input_callback: Function to get user input (default: terminal input)
            safety_status: Current safety status
            
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
            context.messages.append({"role": "assistant", "content": message})
            
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
                context.messages.append({"role": "user", "content": user_response})
        
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
