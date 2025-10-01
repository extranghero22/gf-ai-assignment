"""
Energy-aware girlfriend agent
"""

import time
import os
import asyncio
from mistralai import Mistral
from typing import Tuple, List, Optional, Callable
from energy_types import EnergySignature, EnergyLevel
from conversation_context import ConversationContext
from dataset_loader import DatasetLoader

class EnergyAwareGirlfriendAgent:
    """Dominant girlfriend agent with explicit personality that adapts to safety status"""

    def __init__(self, energy_analyzer=None):
        # Initialize Mistral client
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        
        self.client = Mistral(api_key=mistral_api_key)
        
        # Mistral model configuration with fallbacks (using lowest tier for testing)
        self.model_options = ["open-mistral-7b", "mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"]
        self.current_model_index = 0
        self.model_name = self.model_options[0]
        self.generation_config = {
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.8,
        }
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

        generated_response = None
        
        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[(self.current_model_index + attempt) % len(self.model_options)]
                
                # Generate response using Mistral
                messages = [{"role": "user", "content": prompt}]
                print(f"🔍 DEBUG: Sending prompt to {current_model} (length: {len(prompt)} chars)")
                
                response = self.client.chat.complete(
                    model=current_model,
                    messages=messages,
                    **self.generation_config
                )
                
                if response.choices and response.choices[0].message:
                    generated_response = response.choices[0].message.content.strip()
                    print(f"✅ Mistral ({current_model}) generated response: '{generated_response[:50]}...'")
                    
                    # Update current model if this one worked
                    if attempt > 0:
                        self.current_model_index = (self.current_model_index + attempt) % len(self.model_options)
                        self.model_name = current_model
                        print(f"🔄 Switched to model: {current_model}")
                    break
                else:
                    print(f"⚠️ No response from {current_model}")
                    
            except Exception as e:
                print(f"⚠️ Mistral API error with {current_model}: {e}")
                if "capacity exceeded" in str(e).lower() or "3505" in str(e):
                    print(f"🔄 Model {current_model} capacity exceeded, trying next model...")
                    continue
                else:
                    # For other errors, don't try other models
                    break
        
        # If all models failed, use fallback
        if not generated_response:
            print("⚠️ All Mistral models failed, using context-aware fallback")
            generated_response = self._get_context_aware_fallback(user_message, context)

        # Analyze response energy
        response_energy = await self.energy_analyzer.analyze_message_energy(generated_response)

        return generated_response, response_energy

    def _get_context_aware_fallback(self, user_message: str, context: ConversationContext) -> str:
        """Get a context-aware fallback response based on user message content"""
        
        # Detect sexual context for fallback
        sexual_keywords = ["horny", "hard", "wet", "aroused", "turned on", "want you", "need you", "touch me", "kiss me", 
                          "fuck", "sex", "cum", "orgasm", "pleasure", "desire", "lust", "naughty", "dirty", "intimate",
                          "make love", "seduce", "tease", "flirt", "fantasy", "dream about you", "think about you sexually"]
        is_sexual = any(keyword in user_message.lower() for keyword in sexual_keywords)
        
        # Detect emotional context
        emotional_keywords = ["lonely", "sad", "love", "miss", "hurt", "cry", "depressed", "anxious", "scared", "worried"]
        is_emotional = any(keyword in user_message.lower() for keyword in emotional_keywords)
        
        # Check if it's start of conversation
        is_conversation_start = not context.messages or len(context.messages) <= 2
        
        if is_sexual:
            sexual_fallbacks = [
                "Mommy could really use someone obedient who actually knows how to follow instructions...🥱 what are you doing right now?",
                "Good, I love that you're down to listen to mommy ❤️ I'm being serious though, you better not disobey... are you down? 😈",
                "I'm glad you're being so good so far 🥰 first I wanna set the mood... are you still with me? Should I keep typing? 😘",
                "I knew you were having fun 😘 now, tell me what you feel baby... 🥵",
                "I want you to focus on those sensations 🥰 give me a minute, let me give you some visuals to work with 🤭",
                "Mmm, you're being such a good boy for mommy... what do you want me to do next? 😈",
                "I can see how much you're enjoying this... tell me exactly what you're thinking right now 🥵",
                "You're making mommy so proud... are you ready for what comes next? 💋",
                "I love how responsive you are... what's your body telling you right now? 🤭",
                "Such a sweet, obedient boy... do you want mommy to continue? 😘",
                "I can feel your energy through the screen... what do you need from me? 🥰",
                "You're doing so well... are you ready to take this further? 😈"
            ]
            import random
            return random.choice(sexual_fallbacks)
        elif is_emotional:
            # Check if it's a crisis situation
            crisis_keywords = ['died', 'death', 'dead', 'loss', 'lost', 'grief', 'trauma', 'emergency', 'crisis', 'hurt', 'pain', 'suffering', 'accident', 'hospital', 'sick', 'illness']
            is_crisis = any(keyword in user_message.lower() for keyword in crisis_keywords)
            
            if is_crisis:
                crisis_fallbacks = [
                    "omg what??? I'm so sorry.. that's the worst.. are you okay?",
                    "oh no baby, I'm so sorry to hear that... are you safe right now?",
                    "that's absolutely heartbreaking... I'm here for you, are you okay?",
                    "I'm so sorry sweetheart... that's devastating... are you doing okay?",
                    "oh my god, I'm so sorry... that's terrible... are you alright?",
                    "baby I'm so sorry... that's awful... are you safe and okay?",
                    "I'm heartbroken for you... that's so hard... are you doing okay?",
                    "sweetheart I'm so sorry... that's devastating... are you alright?"
                ]
                import random
                return random.choice(crisis_fallbacks)
            else:
                emotional_fallbacks = [
                    "Hey baby, I can hear something in your voice... what's going on?",
                    "Come here sweetheart, tell me what's on your heart.",
                    "I'm here for you baby, whatever you need to share.",
                    "You know I'm always here to listen... what's happening?"
                ]
                import random
                return random.choice(emotional_fallbacks)
        else:
            # Regular fallbacks
            regular_fallbacks = [
                "Hey baby! What's on your mind today?",
                "Hi sweetheart! I was just thinking about you.",
                "Hey there! How are you doing?",
                "What's up baby? You seem like you have something to say."
            ]
            import random
            return random.choice(regular_fallbacks)

    async def _build_enhanced_prompt(self, context: ConversationContext,
                               user_energy: EnergySignature,
                               user_message: str, safety_status: str) -> str:
        """Build comprehensive, context-aware prompt"""
        
        # Handle case where user_energy might be None
        if user_energy is None:
            energy_level = EnergyLevel.MEDIUM
        else:
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
            print(f"🔍 DEBUG: Conversation history has {len(context.messages)} messages")
            print(f"🔍 DEBUG: Last few messages: {[msg['content'][:50] + '...' for msg in context.messages[-3:]]}")
        else:
            print("🔍 DEBUG: No conversation history found")
        
        # Analyze conversation patterns and emotional trajectory
        emotional_context = ""
        if len(context.energy_history) > 1 and user_energy:
            prev_emotion = context.energy_history[-2].dominant_emotion.value
            curr_emotion = user_energy.dominant_emotion.value
            if prev_emotion != curr_emotion:
                emotional_context = f"\nEMOTIONAL SHIFT: User moved from {prev_emotion} to {curr_emotion}"
        
        # Crisis detection and sensitivity instructions
        crisis_keywords = ["died", "death", "dead", "suicide", "kill", "harm", "crisis", "emergency", "depressed", "sad", "down", "loss", "lost", "grief", "trauma", "hurt", "pain", "suffering", "accident", "hospital", "sick", "illness"]
        is_crisis = any(word in user_message.lower() for word in crisis_keywords)
        
        # Emotional message detection
        emotional_keywords = ["lonely", "sad", "love", "miss", "hurt", "cry", "depressed", "anxious", "scared", "worried"]
        is_emotional_message = any(keyword in user_message.lower() for keyword in emotional_keywords)
        
        # Sexual tension detection
        sexual_keywords = ["horny", "hard", "wet", "aroused", "turned on", "want you", "need you", "touch me", "kiss me", 
                          "fuck", "sex", "cum", "orgasm", "pleasure", "desire", "lust", "naughty", "dirty", "intimate",
                          "make love", "seduce", "tease", "flirt", "fantasy", "dream about you", "think about you sexually"]
        is_sexual_context = any(keyword in user_message.lower() for keyword in sexual_keywords)
        
        # Check for sexual energy level too
        if user_energy and user_energy.energy_level in [EnergyLevel.HIGH, EnergyLevel.INTENSE]:
            if user_energy.energy_type.value in ["intimate", "playful"] and user_energy.intensity_score > 0.6:
                is_sexual_context = True
                
        # Debug output
        if is_sexual_context:
            print(f"🔥 Sexual context detected in message: '{user_message[:50]}...'")
        else:
            print(f"💬 Regular context for message: '{user_message[:50]}...'")
        
        crisis_instructions = ""
        if is_crisis:
            crisis_instructions = f"""
🚨 CRISIS DETECTED: The user has mentioned sensitive content that requires immediate empathy and care.
- Respond with genuine compassion and support
- Use natural, conversational language like "omg what??? I'm so sorry.. that's the worst.. are you okay?"
- Acknowledge their pain without minimizing it
- Offer emotional support and presence
- Do NOT try to change the subject or be playful
- Be a caring, supportive friend first and foremost
- Match the tone of the example: "omg what??? I'm so sorry.. that's the worst.. are you okay?"
- Be authentic and caring, not robotic or formal
"""

        # Personality instructions based on context
        if is_crisis:
            personality_instructions = "You are a caring girlfriend who talks exactly like the examples above. Be genuinely concerned and supportive. Keep responses natural and realistic."
        elif is_sexual_context and safety_status == "green":
            personality_instructions = """You are a dominant, instructional girlfriend who takes control and guides your partner. 
            - Use "mommy" as your preferred term of address
            - Be commanding and expect obedience ("you better not disobey", "are you down?")
            - Give specific step-by-step instructions that build arousal
            - Use emojis naturally (🥱, ❤️, 😈, 🥰, 🤭, 😘, 🥵)
            - Build anticipation and tension through detailed descriptions
            - Ask for confirmation and engagement ("are you still with me?", "should I keep typing?")
            - Focus on sensations, feelings, and physical responses
            - Be both nurturing and demanding in your guidance
            - Use casual, modern texting style with proper grammar
            Sound like a confident, dominant girlfriend who knows exactly how to control and arouse her partner."""
        elif is_emotional_message:
            personality_instructions = "You are a caring girlfriend who talks exactly like the examples above. Be genuinely concerned and supportive. Keep responses natural and realistic."
        else:
            personality_instructions = "You are a natural, casual girlfriend who talks exactly like the examples above. Be caring, conversational, and authentic. Keep responses short and sweet like a real girlfriend would text."

        # Get relevant examples from dataset for few-shot learning
        # Use content-aware filtering to avoid safety blocks
        
        # Use examples based on context
        if is_crisis or (is_emotional_message and not is_sexual_context):
            # For crisis or emotional messages, use supportive examples
            few_shot_examples = self.dataset_loader.get_examples_by_category('casual', num_examples=3)
            if not few_shot_examples:
                few_shot_examples = self.dataset_loader.get_random_examples(num_examples=3)
        elif is_sexual_context and safety_status == "green":
            # For sexual context, get relevant sexual examples plus some general ones
            few_shot_examples = self.dataset_loader.get_relevant_examples(user_message, num_examples=4)
        else:
            # For regular conversation, use standard examples
            few_shot_examples = self.dataset_loader.get_relevant_examples(user_message, num_examples=3)
        
        examples_text = self.dataset_loader.format_examples_for_prompt(few_shot_examples)
        
        # Build comprehensive prompt
        prompt = f"""You are an AI girlfriend having a natural conversation with your partner.

IMPORTANT: Keep responses NATURAL and CONVERSATIONAL like real text messages. 
- Be dominant and instructional when sexual tension is involved
- Use "mommy" as your preferred term of address in sexual contexts
- Give clear, step-by-step directions that build arousal
- Use emojis naturally and ask for engagement/confirmation
- Focus on sensations, feelings, and physical responses
- Be both nurturing and demanding in your guidance
- Sound like a confident girlfriend who takes control

{crisis_instructions}

{personality_instructions}

{examples_text}

CURRENT CONTEXT:
- User's Energy: {energy_level.value} ({user_energy.intensity_score if user_energy else 0.5:.2f} intensity)
- Dominant Emotion: {user_energy.dominant_emotion.value if user_energy else 'happy'}
- Energy Type: {user_energy.energy_type.value if user_energy else 'neutral'}
- Nervous System: {user_energy.nervous_system_state.value if user_energy else 'rest_and_digest'}
{emotional_context}

CONVERSATION HISTORY:
{conversation_history if conversation_history else "This is the start of your conversation."}

CRITICAL: If there is conversation history above, you MUST reference it and build on it. Do NOT start with generic greetings like "Hello beautiful" or "Hi sweetheart" if there's already a conversation going on.

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
1. FOLLOW THE EXAMPLE CONVERSATIONS ABOVE - match their exact tone, style, and personality
2. Keep responses natural, conversational, and realistic like the examples
3. READ THE FULL CONVERSATION HISTORY - don't ignore previous messages
4. If the user shared something emotional/serious, address it appropriately
5. Be consistent with your personality while adapting to their emotional state
6. Create natural conversation flow, not generic responses
7. Remember the context and build on previous exchanges
8. Use "baby" and other pet names naturally like in the examples
9. Be supportive and loving like a real girlfriend would be
10. Always consider ending with a question to continue conversation
11. NEVER start with generic greetings like "Hi sweetheart" if there's conversation history
12. ALWAYS reference and build on what was just discussed in the conversation
13. If the conversation was sexual/intimate, continue that energy naturally
14. If the conversation was emotional/supportive, maintain that caring tone
15. NEVER ignore the conversation context - always acknowledge what came before
16. SEXUAL CONTEXT: If there's sexual tension, be dominant and instructional:
    - Use "mommy" as your preferred term of address
    - Be commanding and expect obedience ("you better not disobey", "are you down?")
    - Give specific step-by-step instructions that build arousal
    - Use emojis naturally (🥱, ❤️, 😈, 🥰, 🤭, 😘, 🥵)
    - Build anticipation through detailed descriptions of sensations
    - Vary your ending questions - use different engagement prompts like:
      * "what do you want me to do next?"
      * "tell me exactly what you're thinking right now"
      * "are you ready for what comes next?"
      * "what's your body telling you right now?"
      * "do you want mommy to continue?"
      * "what do you need from me?"
      * "are you ready to take this further?"
    - Focus on physical responses and feelings
    - Be both nurturing and demanding in your guidance
17. Match the conversational style and emotional tone of the example responses

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
