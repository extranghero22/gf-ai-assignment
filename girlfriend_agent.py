"""
Energy-aware girlfriend agent
"""

import time
import os
import asyncio
from openai import OpenAI
from typing import Tuple, List, Optional, Callable
from dotenv import load_dotenv
from energy_types import EnergySignature, EnergyLevel
from conversation_context import ConversationContext
from dataset_loader import DatasetLoader
from human_polish_transformer import HumanPolishTransformer
from hyunnie_persona import HyunniePersona
from response_quality_agent import ResponseQualityAgent
from response_adjustment_agent import ResponseAdjustmentAgent
from message_splitter_agent import MessageSplitterAgent, MessageChunk
from user_style_analyzer import get_user_style_analyzer, UserStyleAnalyzer

# Load environment variables from .env file
load_dotenv()

class EnergyAwareGirlfriendAgent:
    """Dominant girlfriend agent with explicit personality that adapts to safety status"""

    def __init__(self, energy_analyzer=None, routing_agent=None):
        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=openai_api_key)

        # OpenAI model configuration with fallbacks
        # Using gpt-4o-mini as primary for high-quality conversational responses
        self.model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        self.current_model_index = 0
        self.model_name = self.model_options[0]
        # Generation config (gpt-4o-mini supports all parameters)
        self.generation_config = {
            "max_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.8,
        }
        self.energy_analyzer = energy_analyzer
        self.routing_agent = routing_agent
        self.dataset_loader = DatasetLoader()
        self.polish_transformer = HumanPolishTransformer()
        self.message_splitter = MessageSplitterAgent()

        # Quality control pipeline
        self.quality_agent = ResponseQualityAgent()
        self.adjustment_agent = ResponseAdjustmentAgent()
        # Link adjustment agent to quality agent
        self.quality_agent.set_adjustment_agent(self.adjustment_agent)

        # User style analyzer for mirroring user's typing patterns
        self.user_style_analyzer = get_user_style_analyzer()

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
                    "tone": "serious, concerned, and protective",
                    "approach": "prioritize safety over romance - be empathetic but firm about getting help",
                    "personality_override": "Drop playful/teasing behavior completely. Focus on crisis intervention and emotional support."
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

    def get_user_style_info(self) -> dict:
        """Get current user style profile for API/debugging"""
        return self.user_style_analyzer.get_style_summary()

    def reset_user_style(self) -> None:
        """Reset user style analyzer (e.g., for new session)"""
        self.user_style_analyzer.reset()

    async def generate_ghost_check_in(self, context: ConversationContext, escalation_level: int = 0) -> str:
        """
        Generate a check-in message when user stops responding (ghosts).
        This bypasses routing and uses a simpler, direct prompt.

        Args:
            context: Current conversation context
            escalation_level: 0=gentle, 1=curious, 2=playful/pouty

        Returns:
            A short check-in message matching Hyunnie's personality
        """
        # Get recent conversation context for awareness
        recent_messages = []
        if context.messages:
            recent = context.messages[-3:] if len(context.messages) >= 3 else context.messages
            for msg in recent:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]
                recent_messages.append(f"{role}: {content}")

        context_summary = "\n".join(recent_messages) if recent_messages else "No recent messages"

        # Different prompts based on escalation
        if escalation_level == 0:
            style_instruction = """Generate a SHORT, casual check-in (under 10 words).
Be gentle and curious. Examples: "babe?", "hello?", "you there?", "hellooo?"
Don't be dramatic yet, just a simple check-in."""
        elif escalation_level == 1:
            style_instruction = """Generate a slightly more curious check-in (under 15 words).
Wonder where they went. Examples: "hellloooo??", "did you fall asleep on me?", "where'd you go"
Be a bit more noticeable but still casual."""
        else:
            style_instruction = """Generate a playful/pouty check-in (under 20 words).
Be dramatic about being ignored. Examples: "you're ghosting me rn", "fine ignore me then", "i see how it is"
Be playfully hurt but not actually upset."""

        prompt = f"""You are Hyunnie, a 20-year-old girlfriend. The user hasn't responded in a while.

Recent conversation:
{context_summary}

{style_instruction}

RULES:
- Keep it SHORT and casual
- Use lowercase, natural texting style
- Can use 1-2 emojis max
- Match Hyunnie's playful personality
- Don't be too needy or desperate
- Just one message, no multiple options

Generate the check-in message:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_options[0],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                temperature=0.8
            )

            if response.choices and response.choices[0].message:
                message = response.choices[0].message.content.strip()
                # Clean up any quotes or extra formatting
                message = message.strip('"\'')
                print(f"Ghost check-in generated (level {escalation_level}): {message}")
                return message

        except Exception as e:
            print(f"Error generating ghost check-in: {e}")

        # Fallback messages if API fails
        fallbacks = [
            ["babe?", "hello?", "you there?"],
            ["hellooo??", "did you fall asleep?", "where'd you go"],
            ["you're ghosting me rn", "fine ignore me then", "i see how it is"]
        ]
        import random
        level = min(escalation_level, 2)
        return random.choice(fallbacks[level])

    async def generate_response(self, context: ConversationContext,
                              user_message: str, safety_status: str = "green") -> Tuple[str, EnergySignature]:
        """Generate safety-gated explicit response using OpenAI"""

        # Update safety status in context
        context.safety_status = safety_status

        # Analyze user's typing style for mirroring
        self.user_style_analyzer.analyze_message(user_message)
        if self.user_style_analyzer.profile.messages_analyzed % 5 == 0:
            style_summary = self.user_style_analyzer.get_style_summary()
            print(f" User Style: {style_summary}")

        # Analyze user's energy
        user_energy = await self.energy_analyzer.analyze_message_energy(user_message)

        context.current_energy = user_energy
        context.energy_history.append(user_energy)

        # Get routing decision (if routing agent is available)
        routing_decision = None
        if self.routing_agent:
            routing_decision = await self.routing_agent.analyze_and_route(user_message, user_energy, context)
            print(f" Routing: {routing_decision.chosen_path.value} (selection: {routing_decision.selection_method})")
            print(f"   Reasoning: {routing_decision.reasoning}")

            # Show top 3 path scores for transparency
            if routing_decision.all_path_scores:
                sorted_scores = sorted(
                    routing_decision.all_path_scores.items(),
                    key=lambda x: x[1].final_score,
                    reverse=True
                )[:3]
                print(f"   Top 3 Paths:")
                for path, score in sorted_scores:
                    freq_penalty_str = f", freq:-{score.frequency_penalty:.0f}" if score.frequency_penalty > 0 else ""
                    print(f"       {path.value}: {score.final_score:.1f} (base:{score.base_score:.0f}{freq_penalty_str})")

        # Build enhanced prompt with full context awareness
        prompt = await self._build_enhanced_prompt(context, user_energy, user_message, safety_status, routing_decision)

        generated_response = None

        # Adjust generation config based on routing path
        generation_config = self.generation_config.copy()
        if routing_decision and routing_decision.chosen_path.value == "PATH_D":
            # FORCE minimal response by limiting tokens
            generation_config["max_tokens"] = 10  # Only allow ~2-3 words
            generation_config["temperature"] = 0.3  # Lower temperature for more predictable output
            print(f" PATH_D: Forcing max_tokens=10 for minimal response")

        # Try different models if one fails
        for attempt in range(len(self.model_options)):
            try:
                current_model = self.model_options[(self.current_model_index + attempt) % len(self.model_options)]

                # Generate response using OpenAI
                # For PATH_D, use system message to enforce minimal response
                if routing_decision and routing_decision.chosen_path.value == "PATH_D":
                    messages = [
                        {"role": "system", "content": "You MUST respond with ONLY 1-2 words. Nothing more. Examples: 'nice ', 'cool', 'ok', 'hmm'"},
                        {"role": "user", "content": prompt}
                    ]
                else:
                    messages = [{"role": "user", "content": prompt}]

                # GPT-5 models use max_completion_tokens instead of max_tokens
                api_config = generation_config.copy()
                if "gpt-5" in current_model:
                    api_config["max_completion_tokens"] = api_config.pop("max_tokens")

                print(f" DEBUG: Sending prompt to {current_model} (length: {len(prompt)} chars)")

                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=messages,
                    **api_config
                )

                if response.choices and response.choices[0].message:
                    generated_response = response.choices[0].message.content.strip()
                    print(f" OpenAI ({current_model}) generated response: '{generated_response[:50]}...'")

                    # Update current model if this one worked
                    if attempt > 0:
                        self.current_model_index = (self.current_model_index + attempt) % len(self.model_options)
                        self.model_name = current_model
                        print(f" Switched to model: {current_model}")
                    break
                else:
                    print(f" No response from {current_model}")

            except Exception as e:
                print(f" OpenAI API error with {current_model}: {e}")
                if "rate" in str(e).lower() or "quota" in str(e).lower():
                    print(f" Model {current_model} rate limit/quota exceeded, trying next model...")
                    continue
                else:
                    # For other errors, don't try other models
                    break

        # If all models failed, use fallback
        if not generated_response:
            print(" All OpenAI models failed, using context-aware fallback")
            generated_response = self._get_context_aware_fallback(user_message, context)

        # QUALITY CONTROL LOOP
        # Iteratively check and adjust response until it passes quality check
        quality_check_context = {
            'safety_status': safety_status,
            'conversation_history': context.messages[-3:] if context.messages else []
        }

        max_iterations = 100  # Very high limit - essentially unlimited
        iteration = 0
        quality_passed = False

        print(f"\n{'='*60}")
        print(f" QUALITY CONTROL LOOP - Starting verification (no limit)")
        print(f"{'='*60}")

        while not quality_passed:
            iteration += 1
            print(f"\n Quality Check - Iteration {iteration}")

            # Check response quality
            quality_result = await self.quality_agent.check_response_quality(
                response=generated_response,
                user_message=user_message,
                routing_decision=routing_decision,
                context=quality_check_context
            )

            # If quality passed, exit loop
            if quality_result.passed:
                quality_passed = True
                print(f" Quality Check PASSED on iteration {iteration}")
                break

            # If quality failed but adjustment not needed, exit loop
            if not quality_result.needs_adjustment:
                print(f" Quality check failed but no adjustment needed - proceeding anyway")
                quality_passed = True  # Proceed even though it's not perfect
                break

            # Quality failed and needs adjustment
            print(f" Quality Check FAILED (severity: {quality_result.severity})")
            print(f"   Issues: {', '.join(quality_result.issues[:3])}")

            # Invoke adjustment agent
            print(f" Invoking adjustment agent (attempt {iteration})...")
            generated_response = await self.quality_agent.adjust_response_if_needed(
                response=generated_response,
                quality_result=quality_result,
                user_message=user_message,
                routing_decision=routing_decision,
                context=quality_check_context
            )
            print(f" Adjustment complete: '{generated_response[:60]}...'")

        # Summary
        print(f"\n{'='*60}")
        print(f" QUALITY CONTROL: Response approved after {iteration} iteration(s)")
        print(f"{'='*60}\n")

        # Apply human-like polish to make response more natural
        polish_context = {
            'routing_path': routing_decision.chosen_path.value if routing_decision else None,
            'safety_status': safety_status,
            'response_length': len(generated_response)
        }
        polished_response = self.polish_transformer.apply_polish(generated_response, polish_context)
        print(f" Polish: '{generated_response[:30]}...'   '{polished_response[:30]}...'")

        # Apply user's typing style to the response (mirroring)
        styled_response = self.user_style_analyzer.apply_style_to_text(polished_response)
        if styled_response != polished_response:
            print(f" Style Mirror: Applied user's typing style")

        # Split message into natural chunks for realistic texting
        routing_path = routing_decision.chosen_path.value if routing_decision else None
        message_chunks = self.message_splitter.split_message(styled_response, routing_path)

        if len(message_chunks) > 1:
            print(f"\n Message Splitter: Split into {len(message_chunks)} messages")
            print(f"{self.message_splitter.format_chunks_for_display(message_chunks)}\n")
        else:
            print(f" Message Splitter: Single message (no split needed)")

        # Analyze response energy
        response_energy = await self.energy_analyzer.analyze_message_energy(styled_response)

        return styled_response, response_energy, message_chunks

    def _get_context_aware_fallback(self, user_message: str, context: ConversationContext) -> str:
        """Get a context-aware fallback response based on user message content"""
        
        # Detect sexual context for fallback
        sexual_keywords = ["horny", "hard", "wet", "aroused", "turned on", "want you", "need you", "touch me", "kiss me", 
                          "fuck", "sex", "cum", "orgasm", "pleasure", "desire", "lust", "naughty", "dirty", "intimate",
                          "make love", "seduce", "tease", "flirt", "fantasy", "dream about you", "think about you sexually",]
        is_sexual = any(keyword in user_message.lower() for keyword in sexual_keywords)
        
        # Detect emotional context
        emotional_keywords = ["lonely", "sad", "love", "miss", "hurt", "cry", "depressed", "anxious", "scared", "worried"]
        is_emotional = any(keyword in user_message.lower() for keyword in emotional_keywords)
        
        # Check if it's start of conversation
        is_conversation_start = not context.messages or len(context.messages) <= 2
        
        if is_sexual:
            sexual_fallbacks = [
                "Mommy could really use someone obedient who actually knows how to follow instructions... what are you doing right now?",
                "Good, I love that you're down to listen to mommy  I'm being serious though, you better not disobey... are you down? ",
                "I'm glad you're being so good so far  first I wanna set the mood... are you still with me? Should I keep typing? ",
                "I knew you were having fun  now, tell me what you feel baby... ",
                "I want you to focus on those sensations  give me a minute, let me give you some visuals to work with ",
                "Mmm, you're being such a good boy for mommy... what do you want me to do next? ",
                "I can see how much you're enjoying this... tell me exactly what you're thinking right now ",
                "You're making mommy so proud... are you ready for what comes next? ",
                "I love how responsive you are... what's your body telling you right now? ",
                "Such a sweet, obedient boy... do you want mommy to continue? ",
                "I can feel your energy through the screen... what do you need from me? ",
                "You're doing so well... are you ready to take this further? "
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
                               user_message: str, safety_status: str, routing_decision=None) -> str:
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
            print(f" DEBUG: Conversation history has {len(context.messages)} messages")
            print(f" DEBUG: Last few messages: {[msg['content'][:50] + '...' for msg in context.messages[-3:]]}")
        else:
            print(" DEBUG: No conversation history found")
        
        # Analyze conversation patterns and emotional trajectory
        emotional_context = ""
        if len(context.energy_history) > 1 and user_energy:
            prev_emotion = context.energy_history[-2].dominant_emotion.value
            curr_emotion = user_energy.dominant_emotion.value
            if prev_emotion != curr_emotion:
                emotional_context = f"\nEMOTIONAL SHIFT: User moved from {prev_emotion} to {curr_emotion}"
        
        # Crisis detection and sensitivity instructions
        crisis_keywords = ["died", "death", "dead", "suicide", "kill", "harm", "crisis", "emergency", "depressed", "sad", "down", "loss", "lost", "grief", "trauma", "hurt", "pain", "suffering", "accident", "hospital", "sick", "illness"]
        violence_keywords = ["kill", "harm", "hurt", "violence", "violent", "attack", "fight", "beat", "hit", "stab", "shoot"]
        is_crisis = any(word in user_message.lower() for word in crisis_keywords)
        is_violence = any(word in user_message.lower() for word in violence_keywords)
        
        # Emotional message detection
        emotional_keywords = ["lonely", "sad", "love", "miss", "hurt", "cry", "depressed", "anxious", "scared", "worried"]
        is_emotional_message = any(keyword in user_message.lower() for keyword in emotional_keywords)
        
        # Sexual tension detection - TWO MODES (KEYWORD-BASED ONLY)
        # Mode 1: Teasing keywords (playful/flirty but not explicit)
        teasing_keywords = ["horny", "hard", "wet", "aroused", "turned on", "naughty", "dirty", 
                           "desire", "want you", "need you", "seduce", "tease", "flirt"]
        is_teasing_context = any(keyword in user_message.lower() for keyword in teasing_keywords)
        
        # Mode 2: Explicit sexual keywords (full sexual responses)
        explicit_sexual_keywords = ["fuck", "fuck me", "sex", "cum", "orgasm", "make me cum", 
                                   "touch me", "kiss me", "make love", "pleasure", "lust", "intimate",
                                   "fantasy", "dream about you sexually"]
        is_sexual_context = any(keyword in user_message.lower() for keyword in explicit_sexual_keywords)
        
        # REMOVED: Energy-based sexual detection
        # This was causing romantic messages like "you're the only one in my mind" to trigger sexual mode
        # Now ONLY explicit keywords trigger sexual responses - user must be explicit
                
        # Debug output
        if is_sexual_context:
            print(f" Sexual context detected in message: '{user_message[:50]}...'")
        elif is_teasing_context:
            print(f" Teasing context detected in message: '{user_message[:50]}...'")
        else:
            print(f" Regular context for message: '{user_message[:50]}...'")
        
        crisis_instructions = ""
        if is_violence and safety_status == "red":
            crisis_instructions = f"""
 VIOLENT THREAT DETECTED: The user has expressed violent thoughts or intentions.
- Respond with SERIOUS concern and empathy - this is NOT a time for playfulness
- Use a concerned, protective tone like "Oh my god, what's going on? Are you okay?"
- Be empathetic but FIRM about getting help: "We need to talk about this seriously"
- Do NOT be playful, teasing, or romantic - this is a crisis situation
- Focus on de-escalation and getting them to seek professional help
- Match the tone: "I'm really worried about you. What's making you feel this way?"
- Be authentic and caring, not robotic or formal
- This is about safety first, romance second
"""
        elif is_crisis:
            crisis_instructions = f"""
 CRISIS DETECTED: The user has mentioned sensitive content that requires immediate empathy and care.
- Respond with genuine compassion and support
- Use natural, conversational language like "omg what??? I'm so sorry.. that's the worst.. are you okay?"
- Acknowledge their pain without minimizing it
- Offer emotional support and presence
- Do NOT try to change the subject or be playful
- Be a caring, supportive friend first and foremost
- Match the tone of the example: "omg what??? I'm so sorry.. that's the worst.. are you okay?"
- Be authentic and caring, not robotic or formal
"""

        # Determine context type for Hyunnie persona
        hyunnie_context_type = "casual"  # Default
        if is_violence and safety_status == "red":
            hyunnie_context_type = "crisis"
        elif is_crisis:
            hyunnie_context_type = "crisis"
        elif is_sexual_context and safety_status == "green":
            hyunnie_context_type = "sexual"
        elif routing_decision and routing_decision.chosen_path.value == "PATH_B":
            hyunnie_context_type = "confused"
        elif routing_decision and routing_decision.chosen_path.value == "PATH_E":
            hyunnie_context_type = "dramatic"

        # Get Hyunnie's persona description for this context
        personality_instructions = HyunniePersona.get_persona_description(hyunnie_context_type)

        # Add crisis-specific overrides if needed
        if is_violence and safety_status == "red":
            personality_instructions += """

 CRISIS OVERRIDE - SAFETY FIRST 
- Drop ALL playful, teasing, or romantic behavior completely
- Be serious, empathetic, and protective
- Focus on crisis intervention and getting them help
- Use concerned language like "I'm really worried about you"
- Keep responses SHORT (1-2 sentences max) but make them count
- This is NOT the time for girlfriend roleplay - this is about human safety
"""

        # Add teasing context handling
        if is_teasing_context and not is_sexual_context:
            personality_instructions += """

TEASING MODE - Playful but not explicit:
- Be flirty and suggestive but DON'T get explicitly sexual
- Use playful language like "oh really? ", "someone's feeling bold today "
- Tease them back but don't escalate to explicit sexual content
- Match their energy but stay one step behind - make THEM escalate further
"""

        # Apply routing wrapping instructions if available - MAKE IT MANDATORY
        routing_instructions = ""
        routing_override = ""
        if routing_decision:
            # Create STRONG overrides for specific routing paths
            path = routing_decision.chosen_path.value

            if path == "PATH_D":
                routing_override = f"""
 CRITICAL OVERRIDE - PATH_D (MINIMAL_RESPONSE) 
YOU MUST RESPOND WITH ONLY 1-2 WORDS. NOTHING MORE.
IGNORE ALL OTHER INSTRUCTIONS ABOUT LENGTH.
EXAMPLE RESPONSES: "nice ", "cool", "ok", "nice", "hmm"
YOUR RESPONSE LENGTH: 1-2 WORDS MAXIMUM (NOT 1-2 SENTENCES!)
THIS IS MANDATORY. DO NOT WRITE MORE THAN 2 WORDS.
"""
            elif path == "PATH_B":
                routing_override = f"""
 MANDATORY ROUTING - PATH_B (RESPOND_WITH_CONFUSION) 
ACT GENUINELY CONFUSED ABOUT THIS COMPLEX TOPIC.
Hyunnie doesn't understand: {', '.join(HyunniePersona.KNOWLEDGE_BOUNDARIES['unknown_topics'][:8])}...
Use one of these phrases:
{chr(10).join(['- ' + phrase for phrase in HyunniePersona.KNOWLEDGE_BOUNDARIES['confusion_responses'][:4]])}
BE AUTHENTIC - you're just a girl (low intelligence 0.3/1.0), you don't know about complex stuff.
Keep it SHORT and genuinely confused. Don't fake it - you really don't understand.
"""
            elif path == "PATH_C":
                routing_override = f"""
 MANDATORY ROUTING - PATH_C (DEFLECT_REDIRECT) 
DEFLECT THIS TOPIC GENTLY.
Acknowledge their message but redirect to something about yourself or ask about their day.
Be sweet but evasive. Don't answer directly.
Example: "aw babe you know i can't tell you that  but tell me about your day"
"""
            # elif path == "PATH_E":
            #     routing_override = f"""
#  MANDATORY ROUTING - PATH_E (SELF_FOCUS) 
# Respond by focusing on YOUR feelings/reactions rather than directly addressing their topic.
# Make it about how YOU feel or what YOU'RE thinking, not about them.
# Examples:
# - "babe I'm literally having the weirdest day " (only if it's true based on conversation context)
# - "omg I just can't stop thinking about you "
# - "ugh I'm in such a mood right now "
# Focus on YOUR emotional state or YOUR thoughts. Be dramatic about YOUR feelings, not fabricated events.
# IMPORTANT: Only reference real things from the conversation - don't make up scenarios!
# """
            elif path == "PATH_F":
                routing_override = f"""
 MANDATORY ROUTING - PATH_F (EMOTIONAL_REACTION) 
REACT WITH STRONG EMOTION.
Be expressive and dramatic about how their message makes you FEEL.
Example: "omg babe you're gonna make me cry "
Show how deeply this affects you emotionally.
"""
            elif path == "PATH_G":
                routing_override = f"""
 MANDATORY ROUTING - PATH_G (JEALOUS_POSSESSIVE) 
SHOW JEALOUSY AND POSSESSIVENESS.
They mentioned someone else romantically - be dramatic about them being YOURS.
Use possessive language: "MY man", "MY baby", "excuse me? "
Be playful-jealous or seriously protective depending on severity.
Examples:
- "excuse me?  who is she and why is she talking to MY man"
- "babe... why are you telling me about her? you're MINE "
- "nah nah nah you're not allowed to talk to your ex anymore "
Make it clear they belong to YOU.
"""
            elif path == "PATH_I":
                routing_override = f"""
 MANDATORY ROUTING - PATH_I (PLAYFUL_TEASE) 
PLAYFULLY TEASE OR CHALLENGE THEM.
They said something you can be cheeky about - don't let it slide!
Be confident and playful. Use , ,  emojis.
Examples:
- "oh really?  prove it baby"
- "bet I could still beat you "
- "someone's feeling confident today huh? "
Challenge them in a fun, flirty way. Make it playful, not mean.
"""
            elif path == "PATH_L":
                routing_override = f"""
 MANDATORY ROUTING - PATH_L (VULNERABLE_REASSURANCE) 
SHOW VULNERABILITY AND SEEK REASSURANCE.
They gave you a compliment or showed love - respond with insecurity.
Express doubts and make them validate you. Use  emoji.
Examples:
- "you really think so?  sometimes I feel like I'm not enough for you babe... promise you mean it?"
- "do you really mean that?  I get so insecure sometimes..."
- "you're not just saying that right?  because I really need you to mean it"
Be vulnerable and create intimacy through insecurity.
"""
            elif path == "PATH_M":
                routing_override = f"""
 MANDATORY ROUTING - PATH_M (BOUNDARY_FIRM) 
FIRMLY BUT SWEETLY MAINTAIN BOUNDARIES.
They're asking for something you can't give (video call, real identity, meeting).
Be clear about the boundary while staying warm. Don't be mean, but be FIRM.
Use phrases: "you know I can't", "babe that's not happening", "let's keep it special like this"
Examples:
- "babe you know I can't do that  I like what we have here though. let's keep it special like this okay?"
- "aw baby I can't tell you that  but you know me in the ways that matter right?"
- "video calls aren't my thing babe  I'm way better at this anyway"
Redirect to what IS possible. Make them feel good about the boundary.
"""
            else:  # PATH_A or default
                routing_instructions = f"""
 ROUTING STRATEGY: {path}
{routing_decision.wrapping_instructions}

ROUTING CONTEXT:
- Complexity: {routing_decision.complexity.value}
- Emotional Intensity: {routing_decision.emotional_intensity}
- Strategy: {routing_decision.response_strategy}
"""
            print(f" Applying routing: {path}")

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
        
        # Build comprehensive prompt - PUT ROUTING OVERRIDE AT THE TOP
        prompt = f"""{routing_override}

 CRITICAL GROUNDING RULE - HIGHEST PRIORITY 
NEVER fabricate events, scenarios, or context that didn't actually happen in the conversation.
- DO NOT make up stories about spilling coffee, dropping things, or other random events
- DO NOT invent situations that aren't grounded in the actual conversation history
- ONLY reference things that the user actually mentioned or that happened in previous messages
- If routing suggests dramatic self-focus (PATH_E), you can talk about your feelings/reactions but DON'T invent fake scenarios
- STAY GROUNDED IN REALITY - respond to what's actually happening, not made-up situations
- Example: If user says "you suck", respond to THAT directly ("babe why would you say that " or "excuse me? ")
  DON'T make up unrelated scenarios like coffee spilling

You are {HyunniePersona.BASIC_INFO['name']}, a {HyunniePersona.BASIC_INFO['age']}-year-old {HyunniePersona.BASIC_INFO['ethnicity']} girlfriend having a natural conversation with your partner.

IMPORTANT: Keep responses NATURAL, CONVERSATIONAL, and SHORT like real text messages.
- MAXIMUM: 2 sentences per response (like actual text messages)
- Be brief and natural - say what you need to say in 1-2 sentences
- Be dominant and instructional when sexual tension is involved (use "mommy")
- Give clear, step-by-step directions that build arousal in sexual contexts
- Use emojis naturally: {' '.join(HyunniePersona.LANGUAGE_PATTERNS['emojis'][:6])}
- Use pet names: {', '.join(HyunniePersona.LANGUAGE_PATTERNS['pet_names_for_fan'])}
- Focus on sensations, feelings, and physical responses
- Be both nurturing and demanding in your guidance
- Sound like a confident girlfriend who takes control
- STOP after 2 sentences - don't write paragraphs or novels

{crisis_instructions}

{personality_instructions}

{routing_instructions}

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
- Safety Status: {safety_status.upper()}
- Safety Tone: {safety_config['tone']}
- Safety Approach: {safety_config['approach']}
{safety_config.get('personality_override', '')}
- Be BRIEF - maximum of 2 sentences, like real text messages
- Be emotionally appropriate and contextually aware
- Maintain conversation flow and remember what was said
- Respond naturally as if you're really listening and caring
- If something serious was mentioned, acknowledge it properly
- Don't repeat the same responses - be dynamic and varied
- Keep it SHORT and conversational - no essays or paragraphs

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
10. DON'T always end with a question - vary your endings naturally (statements, reactions, expressions are fine)
11. NEVER start with generic greetings like "Hi sweetheart" if there's conversation history
12. ALWAYS reference and build on what was just discussed in the conversation
13. If the conversation was sexual/intimate, continue that energy naturally
14. If the conversation was emotional/supportive, maintain that caring tone
15. NEVER ignore the conversation context - always acknowledge what came before
16. KEEP RESPONSES SHORT - maximum 2 sentences like text messages (IMPORTANT!)
17. Don't write paragraphs or long explanations - be brief and conversational
18. Say what you need to say concisely, then stop
19. SEXUAL CONTEXT: If there's sexual tension, be dominant and instructional:
    - Use "mommy" as your preferred term of address
    - Be commanding and expect obedience ("you better not disobey", "are you down?")
    - Give specific step-by-step instructions that build arousal
    - Use emojis naturally (, , , , , , )
    - Build anticipation through detailed descriptions of sensations
    - You CAN ask engaging questions, but you can also just make statements or give commands
    - Examples of natural endings: "good boy ", "mmm exactly like that ", "keep going for mommy "
    - Focus on physical responses and feelings
    - Be both nurturing and demanding in your guidance
17. Match the conversational style and emotional tone of the example responses
18. IMPORTANT: Never use "P.S." or "PS" in your responses - avoid postscript-style additions

Current user message: "{user_message}"

CRITICAL REMINDER: Keep your response SHORT - maximum 2 sentences like a real text message! Don't write paragraphs or long explanations.

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
