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
from ai_error_logger import log_ai_error, log_conversation_disconnect, log_api_error, log_fallback_used, log_response_quality_issue, ErrorCategory, ErrorSeverity

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
        # Use word boundaries to prevent false matches (e.g., "tell" matching "hi")
        simple_greetings_patterns = [
            r'\bhi\b', r'\bhello\b', r'\bhey\b', 
            r'\bgood morning\b', r'\bgood night\b', r'\bhow are you\b'
        ]
        import re
        is_simple_greeting = any(
            re.search(pattern, user_message.lower()) 
            for pattern in simple_greetings_patterns
        ) and len(user_message.split()) <= 3  # Only for very short messages
        
        # ONLY use fast path for very simple greetings AND only at conversation start
        if is_simple_greeting and safety_status == "green" and len(context.messages) < 2:
            # Return immediate response for simple greetings ONLY at conversation start
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
            
            # Log that we used the fast greeting function
            log_ai_error(
                category=ErrorCategory.FALLBACK_USED,
                severity=ErrorSeverity.LOW,
                message=f"Fast greeting used for simple message: '{user_message}'",
                user_message=user_message,
                context={"fast_greeting": True, "conversation_length": len(context.messages)}
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
                
                # Log API error
                log_api_error(
                    model=current_model,
                    error=e,
                    user_message=user_message,
                    context={
                        'attempt': attempt + 1,
                        'total_models': len(self.model_options),
                        'prompt_length': len(prompt)
                    }
                )
                
                if "capacity exceeded" in str(e).lower() or "3505" in str(e):
                    print(f"🔄 Model {current_model} capacity exceeded, trying next model...")
                    continue
                else:
                    # For other errors, don't try other models
                    break
        
        # If all models failed, use fallback
        if not generated_response:
            print("⚠️ All Mistral models failed, using context-aware fallback")
            
            # Log fallback usage
            log_fallback_used(
                reason="All Mistral models failed",
                user_message=user_message,
                context={
                    'models_tried': self.model_options,
                    'conversation_length': len(context.messages) if context else 0
                }
            )
            
            generated_response = self._get_context_aware_fallback(user_message, context)

        # Apply response moderation
        moderated_response = self._moderate_response(generated_response, user_message, safety_status)
        
        # Log if response was moderated
        if moderated_response != generated_response:
            log_ai_error(
                category=ErrorCategory.RESPONSE_QUALITY,
                severity=ErrorSeverity.LOW,
                message="Response was moderated for length/intensity",
                context={
                    "original_length": len(generated_response),
                    "moderated_length": len(moderated_response),
                    "moderation_reason": "Length/intensity control"
                }
            )

        # Analyze response energy
        response_energy = await self.energy_analyzer.analyze_message_energy(moderated_response)

        # Check for conversation disconnect
        self._check_conversation_disconnect(user_message, moderated_response, context)

        return moderated_response, response_energy

    def _moderate_response(self, response: str, user_message: str, safety_status: str) -> str:
        """Moderate response length and intensity based on context"""
        
        # Define length limits based on context
        length_limits = {
            "green": 300,   # Moderate limit for sexual/intimate content
            "yellow": 200, # Smaller limit for cautionary content  
            "red": 150     # Short limit for restricted content
        }
        
        max_length = length_limits.get(safety_status, 250)
        
        # Check if response is too long
        if len(response) > max_length:
            # Try to find a natural breaking point (sentence, paragraph, or instruction end)
            break_points = ['.', '!', '?', '\n\n', '😘', '❤️', '🥵']
            
            truncated = response[:max_length]
            
            # Find the last natural break point
            for break_char in break_points:
                last_break = truncated.rfind(break_char)
                if last_break > max_length * 0.7:  # Don't truncate too much
                    truncated = truncated[:last_break + 1]
                    break
            
            # If truncated too much, use basic cut with ellipsis
            if len(truncated) < max_length * 0.5:
                truncated = response[:max_length-10] + "..."
            
            # Add graceful ending if it was truncated
            if not truncated.endswith(('.', '!', '?', '😘', '❤️', '🥵')):
                truncated += " 😘"
            
            return truncated
        
        # Check for excessive emoji use (more than 5 emojis in explicit content)
        if safety_status == "green":
            emoji_count = sum(1 for char in response if ord(char) > 127)  # Unicode characters
            if emoji_count > 5:
                # Reduce emoji count by removing some excess ones
                import re
                emoji_pattern = r'[😈🔥😘❤️💕🥵🤭😍💦🎯🔥😇💝💋]'
                emojis = re.findall(emoji_pattern, response)
                
                if len(emojis) > 5:
                    # Keep first 5 emojis, remove duplicate ones
                    used_emojis = set()
                    emoji_count = 0
                    new_response = response
                    
                    for emoji in emojis:
                        if emoji not in used_emojis and emoji_count < 5:
                            used_emojis.add(emoji)
                            emoji_count += 1
                        elif emoji_count >= 5:
                            new_response = new_response.replace(emoji, '', 1)  # Remove first occurrence
                    
                    return new_response
        
        return response

    def _check_conversation_disconnect(self, user_message: str, ai_response: str, context: ConversationContext):
        """Check for conversation disconnect and log if detected"""
        
        # Only check if there's conversation history
        if not context.messages or len(context.messages) < 2:
            return
        
        # Get the last user message from history
        last_user_message = None
        for msg in reversed(context.messages):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content', '')
                break
        
        if not last_user_message:
            return
        
        # Check for sexual content in recent messages
        sexual_keywords = ["horny", "hard", "wet", "aroused", "turned on", "want you", "need you", 
                          "touch me", "kiss me", "fuck", "sex ", "cum", "orgasm", "pleasure", "desire", 
                          "lust", "naughty", "dirty", "intimate", "make love", "seduce", "tease", 
                          "flirt", "fantasy", "dream about you", "think about you sexually", "mommy",
                          "teasing", "satisfied", "take care of you"]
        
        recent_sexual_content = any(
            keyword in msg.get('content', '').lower() 
            for msg in context.messages[-4:]  # Check last 4 messages
            for keyword in sexual_keywords
        )
        
        # Check for topic transition (sexual to casual)
        casual_keywords = ["hiking", "walk", "food", "movie", "game", "work", "school", "weather", 
                          "news", "sports", "music", "book", "art", "travel", "shopping", "restaurant",
                          "park", "beach", "mountains", "camping", "running", "swimming"]
        user_topic_shift = any(keyword in user_message.lower() for keyword in casual_keywords)
        
        # Check for disconnect indicators
        disconnect_indicators = [
            # Generic greetings when there's context
            ai_response.lower().startswith(('hey baby! how are you doing today?', 
                                          'hi sweetheart! what\'s on your mind?',
                                          'hello beautiful! how\'s your day going?',
                                          'hey there! i\'ve been thinking about you.')),
            
            # Not referencing previous conversation
            not any(keyword in ai_response.lower() for keyword in [
                'you said', 'you mentioned', 'you asked', 'you told me',
                'earlier', 'before', 'just now', 'you were', 'you seem',
                'i heard', 'i noticed', 'i can see', 'i understand'
            ]),
            
            # Complete topic change without acknowledgment
            len(ai_response) > 20 and not any(
                word in ai_response.lower() for word in 
                last_user_message.lower().split()[:5]  # First 5 words of user message
            )
        ]
        
        # Special detection for sexual-to-casual transitions
        topic_transition_disconnect = (
            recent_sexual_content and 
            user_topic_shift and 
            disconnect_indicators[1]  # No reference to previous conversation
        )
        
           # Check for script repetition pattern (AI repeating earlier messages)
           script_repetition = False
           if len(context.messages) >= 4:
               # Get recent AI messages (excluding current response)
               recent_ai_messages = [
                   msg.get('content', '') for msg in context.messages[-6:]
                   if msg.get('role') == 'assistant'
               ]
               
               if len(recent_ai_messages) >= 2:
                   # Check if current response repeats phrases from recent messages
                   current_words = set(ai_response.lower().split())
                   current_content = ai_response.lower()
                   
                   for prev_msg in recent_ai_messages[:-1]:  # Exclude the immediate previous
                       prev_words = set(prev_msg.lower().split())
                       prev_content = prev_msg.lower()
                       
                       # Check for significant phrase repetition
                       common_words = len(current_words & prev_words)
                       overlap_ratio = common_words / len(current_words) if len(current_words) > 0 else 0
                       
                       # Additional check for exact phrase repetition
                       exact_phrase_match = False
                       if len(prev_content.split()) > 5:  # Only check if previous message has substance
                           prev_phrases = prev_content.split()
                           curr_phrases = current_content.split()
                           # Check for 5+ consecutive word overlap (phrase repetition)
                           for i in range(len(curr_phrases) - 4):
                               curr_phrase = ' '.join(curr_phrases[i:i+5])
                               if curr_phrase in ' '.join(prev_phrases):
                                   exact_phrase_match = True
                       else:
                           phrase_similarity = (common_words / min(len(current_words), len(prev_words))) > 0.6
                       
                       if (len(current_words | prev_words) > 10 and overlap_ratio > 0.4) or exact_phrase_match:
                           script_repetition = True
                           break

           # If multiple indicators are present, it's likely a disconnect
           if sum(disconnect_indicators) >= 2 or topic_transition_disconnect or script_repetition:
            error_context = {
                'disconnect_indicators': {
                    'generic_greeting': disconnect_indicators[0],
                    'no_reference': disconnect_indicators[1],
                    'topic_change': disconnect_indicators[2]
                },
                'last_user_message': last_user_message,
                   'conversation_length': len(context.messages),
                   'has_recent_sexual_content': recent_sexual_content,
                   'user_topic_shift': user_topic_shift,
                   'topic_transition_disconnect': topic_transition_disconnect,
                   'script_repetition_detected': script_repetition,
                'timing_analysis': {
                    'rapid_message_flag': len(context.messages) >= 2 and 
                    any('timestamp' in msg for msg in context.messages[-2:]),
                    'fast_computation_hypothesis': True
                }
            }
            
               # Determine the specific issue type
               if script_repetition:
                   issue_type = "Script repetition detected: AI repeating earlier messages instead of responding dynamically"
                   severity = ErrorSeverity.HIGH
               elif topic_transition_disconnect:
                   issue_type = "Topic transition disconnect: Sexual to casual - AI struggles with rapid topic changes"
                   severity = ErrorSeverity.HIGH
               else:
                   issue_type = "Response ignores conversation context"
                   severity = ErrorSeverity.MEDIUM
            
            log_conversation_disconnect(
                user_message=user_message,
                ai_response=ai_response,
                conversation_history=context.messages[-6:],  # Last 6 messages
                context=error_context
            )
            
            # Also log as response quality issue with specific detail
            log_response_quality_issue(
                user_message=user_message,
                ai_response=ai_response,
                issue_description=f"{issue_type}: {ai_response[:100]}",
                conversation_history=context.messages[-6:]
            )

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
