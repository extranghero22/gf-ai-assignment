"""
Topic Re-engagement System - Dynamically switches topics to restore engagement
"""

import time
import random
import re
from typing import List, Optional, Dict, Tuple, Callable
from engagement_types import (
    Topic,
    TopicCategory,
    LoopAnalysis,
    LoopType,
    EngagementMetrics,
    FlowSwitch,
    ReengagementDecision,
    ReengagementAttempt
)
from energy_types import EnergySignature, EnergyLevel, EnergyType
from routing_types import RoutingPath


class TopicLibrary:
    """Manages available topics with freshness tracking"""

    def __init__(self):
        self.topics = self._initialize_topics()
        self.topic_usage_history = {}
        self.topic_success_rates = {}

    def _initialize_topics(self) -> Dict[str, Topic]:
        """Initialize comprehensive topic library"""
        topics = {}

        # CASUAL TOPICS
        casual_topics = [
            Topic(
                topic_id="coffee_spill",
                category=TopicCategory.CASUAL,
                keywords=["coffee", "spill", "mess"],
                entry_lines=[
                    "omg babe i just spilled coffee EVERYWHERE ",
                    "ugh i'm such a mess... spilled my coffee all over my shirt lol",
                ],
                preferred_paths=[RoutingPath.IGNORE_SELF_FOCUS, RoutingPath.EMOTIONAL_REACTION],
                relationship_stage="any",
                min_energy_level=EnergyLevel.LOW,
                max_energy_level=EnergyLevel.MEDIUM
            ),
            Topic(
                topic_id="earl_grey_antics",
                category=TopicCategory.CASUAL,
                keywords=["earl grey", "cat", "pet", "sleeping"],
                entry_lines=[
                    "babe Earl Grey is being SO weird right now ",
                    "omg you won't believe what Earl Grey just did",
                    "Earl Grey woke me up by sitting on my face i can't breathe ",
                ],
                preferred_paths=[RoutingPath.IGNORE_SELF_FOCUS, RoutingPath.RESPOND_NORMALLY],
                relationship_stage="any"
            ),
            Topic(
                topic_id="food_craving",
                category=TopicCategory.CASUAL,
                keywords=["food", "hungry", "craving", "eat"],
                entry_lines=[
                    "babe i'm craving tacos SO bad rn ",
                    "ugh i want pizza so bad",
                    "i'm literally starving what should i eat",
                ],
                preferred_paths=[RoutingPath.RESPOND_NORMALLY, RoutingPath.IGNORE_SELF_FOCUS],
                relationship_stage="any"
            ),
            Topic(
                topic_id="shopping_find",
                category=TopicCategory.CASUAL,
                keywords=["shopping", "found", "buy", "cute"],
                entry_lines=[
                    "omg I just saw the cutest dress online",
                    "babe look at this thing I found ",
                    "i need this so bad but it's expensive ",
                ],
                preferred_paths=[RoutingPath.IGNORE_SELF_FOCUS],
                relationship_stage="any"
            ),
        ]

        # PLAYFUL TOPICS
        playful_topics = [
            Topic(
                topic_id="playful_challenge",
                category=TopicCategory.PLAYFUL,
                keywords=["bet", "challenge", "prove"],
                entry_lines=[
                    "bet you can't make me laugh right now ",
                    "i dare you to tell me something interesting babe",
                    "ok entertain me. i'm bored ",
                ],
                preferred_paths=[RoutingPath.PLAYFUL_TEASE],
                relationship_stage="developing",
                min_energy_level=EnergyLevel.MEDIUM
            ),
            Topic(
                topic_id="flirty_tease",
                category=TopicCategory.PLAYFUL,
                keywords=["cute", "flirt", "blush"],
                entry_lines=[
                    "why are you so cute tho ",
                    "you're making me blush stop it ",
                    "babe you're so... *sighs* cute ",
                ],
                preferred_paths=[RoutingPath.PLAYFUL_TEASE, RoutingPath.EMOTIONAL_REACTION],
                relationship_stage="developing"
            ),
        ]

        # INTIMATE TOPICS
        intimate_topics = [
            Topic(
                topic_id="missing_you",
                category=TopicCategory.INTIMATE,
                keywords=["miss", "wish", "see you"],
                entry_lines=[
                    "i miss you babe ",
                    "wish I could see you right now",
                    "been thinking about you all day ",
                ],
                preferred_paths=[RoutingPath.VULNERABLE_REASSURANCE, RoutingPath.EMOTIONAL_REACTION],
                relationship_stage="developing",
                min_energy_level=EnergyLevel.LOW
            ),
            Topic(
                topic_id="thinking_about_you",
                category=TopicCategory.INTIMATE,
                keywords=["thinking", "mind", "distracted"],
                entry_lines=[
                    "can't stop thinking about you babe ",
                    "you're on my mind",
                    "you keep distracting me ",
                ],
                preferred_paths=[RoutingPath.EMOTIONAL_REACTION, RoutingPath.RESPOND_NORMALLY],
                relationship_stage="developing"
            ),
        ]

        # DEEP TOPICS
        deep_topics = [
            Topic(
                topic_id="future_dreams",
                category=TopicCategory.DEEP,
                keywords=["future", "dream", "someday", "plans"],
                entry_lines=[
                    "babe what do you want to do in the future?",
                    "sometimes I think about what our future could be like ",
                    "where do you see yourself in 5 years?",
                ],
                preferred_paths=[RoutingPath.RESPOND_NORMALLY, RoutingPath.VULNERABLE_REASSURANCE],
                relationship_stage="established",
                min_energy_level=EnergyLevel.MEDIUM
            ),
        ]

        # RANDOM INTERRUPTION TOPICS
        random_topics = [
            Topic(
                topic_id="friend_drama",
                category=TopicCategory.RANDOM,
                keywords=["friend", "drama", "happened", "crazy"],
                entry_lines=[
                    "omg omg omg babe my friend just texted me the craziest thing",
                    "babe you won't BELIEVE what just happened",
                    "ok so my friend just told me some INSANE drama",
                ],
                preferred_paths=[RoutingPath.IGNORE_SELF_FOCUS, RoutingPath.EMOTIONAL_REACTION],
                relationship_stage="any"
            ),
            Topic(
                topic_id="random_thought",
                category=TopicCategory.RANDOM,
                keywords=["random", "thought", "realized"],
                entry_lines=[
                    "babe random thought",
                    "ok this is gonna sound weird but",
                    "i just realized something",
                ],
                preferred_paths=[RoutingPath.IGNORE_SELF_FOCUS],
                relationship_stage="any"
            ),
        ]

        # CALLBACK TOPIC (special - dynamically generated)
        callback_topic = Topic(
            topic_id="callback_reference",
            category=TopicCategory.CALLBACK,
            keywords=["remember", "earlier", "you said"],
            entry_lines=[],  # Generated dynamically
            preferred_paths=[RoutingPath.RESPOND_NORMALLY],
            relationship_stage="any"
        )

        # Add all topics to library
        for topic_list in [casual_topics, playful_topics, intimate_topics, deep_topics, random_topics, [callback_topic]]:
            for topic in topic_list:
                topics[topic.topic_id] = topic

        return topics

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        """Get topic by ID"""
        return self.topics.get(topic_id)

    def get_topics_by_category(self, category: TopicCategory) -> List[Topic]:
        """Get all topics in a category"""
        return [t for t in self.topics.values() if t.category == category]

    def record_usage(self, topic: Topic, timestamp: float):
        """Record that topic was used"""
        topic.last_used = timestamp
        topic.times_used += 1
        if topic.topic_id not in self.topic_usage_history:
            self.topic_usage_history[topic.topic_id] = []
        self.topic_usage_history[topic.topic_id].append(timestamp)

    def calculate_freshness(self, topic: Topic, current_message_count: int) -> float:
        """
        Calculate topic freshness score (0.0-1.0).
        1.0 = never used, lower = used recently
        """
        if topic.last_used is None:
            return 1.0

        # Estimate messages since last use (rough approximation)
        time_since_use = time.time() - topic.last_used
        messages_since = int(time_since_use / 30)  # Assume ~30 seconds per message

        if messages_since >= 30:
            return 0.9
        elif messages_since >= 20:
            return 0.7
        elif messages_since >= 10:
            return 0.5
        elif messages_since >= 5:
            return 0.3
        else:
            return 0.1


class TopicSelector:
    """Selects appropriate topic for re-engagement"""

    def __init__(self, topic_library: TopicLibrary):
        self.topic_library = topic_library

    async def select_reengagement_topic(
        self,
        engagement_metrics: EngagementMetrics,
        loop_analysis: LoopAnalysis,
        context,
        current_energy: EnergySignature,
        decision: ReengagementDecision
    ) -> Optional[Topic]:
        """
        Select best topic for current situation.

        Args:
            engagement_metrics: Current engagement metrics
            loop_analysis: Loop detection results
            context: Conversation context
            current_energy: Current energy signature
            decision: Re-engagement decision

        Returns:
            Selected Topic or None
        """
        # Filter by relationship stage
        relationship_stage = self._get_relationship_stage(context)
        candidate_topics = []

        for topic in self.topic_library.topics.values():
            if topic.relationship_stage != "any" and topic.relationship_stage != relationship_stage:
                continue

            # Filter by energy compatibility
            if current_energy:
                if current_energy.energy_level < topic.min_energy_level:
                    continue
                if current_energy.energy_level > topic.max_energy_level:
                    continue

            # Filter by recommended category
            if decision.recommended_category and topic.category != decision.recommended_category:
                continue

            # Exclude very recently used topics
            freshness = self.topic_library.calculate_freshness(topic, len(context.messages))
            if freshness < 0.2:
                continue

            candidate_topics.append(topic)

        if not candidate_topics:
            return None

        # Rank topics
        scored_topics = []
        for topic in candidate_topics:
            score = self._score_topic(topic, engagement_metrics, current_energy, context)
            scored_topics.append((topic, score))

        # Sort by score
        scored_topics.sort(key=lambda x: x[1], reverse=True)

        # Weighted random selection from top 3
        top_topics = scored_topics[:min(3, len(scored_topics))]
        weights = [score for _, score in top_topics]
        selected = random.choices([t for t, _ in top_topics], weights=weights)[0]

        return selected

    def _score_topic(self, topic: Topic, metrics: EngagementMetrics,
                     energy: EnergySignature, context) -> float:
        """Score a topic for selection"""
        score = 0.0

        # Freshness (40% weight)
        freshness = self.topic_library.calculate_freshness(topic, len(context.messages))
        score += freshness * 0.4

        # Success rate (30% weight)
        score += topic.success_rate * 0.3

        # Energy alignment (20% weight)
        if energy:
            if topic.category == TopicCategory.PLAYFUL and energy.energy_type == EnergyType.PLAYFUL:
                score += 0.2
            elif topic.category == TopicCategory.INTIMATE and energy.energy_type == EnergyType.INTIMATE:
                score += 0.2
            else:
                score += 0.1

        # Base score (10% weight)
        score += 0.1

        return score

    def _get_relationship_stage(self, context) -> str:
        """Determine relationship stage from message count"""
        message_count = len(context.messages) if hasattr(context, 'messages') else 0
        if message_count < 10:
            return "early"
        elif message_count < 50:
            return "developing"
        else:
            return "established"


class ReengagementStrategies:
    """Different strategies for topic injection"""

    @staticmethod
    async def callback_strategy(context, topic: Topic) -> str:
        """Reference something mentioned earlier"""
        # Scan last 20 messages for interesting user statements
        if not hasattr(context, 'messages') or len(context.messages) < 5:
            return "babe I was thinking about something you said earlier"

        user_messages = [m for m in context.messages[-20:] if m.get('role') == 'user']

        # Find a substantial user message
        for msg in reversed(user_messages):
            content = msg.get('content', '')
            if len(content.split()) > 10:
                # Extract a key phrase
                words = content.split()
                if len(words) > 15:
                    snippet = ' '.join(words[:15]) + "..."
                else:
                    snippet = content

                return f"babe i was thinking about what you said earlier... about {snippet.lower()}. tell me more about that?"

        return "babe remember what we were talking about earlier? I've been thinking about it"

    @staticmethod
    async def pivot_strategy(context, topic: Topic) -> str:
        """Related to current topic but shifts direction"""
        # Just use the first entry line as a natural pivot
        if topic.entry_lines:
            return random.choice(topic.entry_lines)
        return "babe speaking of that... "

    @staticmethod
    async def random_interruption_strategy(context, topic: Topic) -> str:
        """Dramatic topic shift"""
        if topic.entry_lines:
            return random.choice(topic.entry_lines)
        return "omg babe wait"

    @staticmethod
    async def vulnerable_strategy(context, topic: Topic) -> str:
        """Show vulnerability to create intimacy"""
        vulnerable_lines = [
            "babe... can i tell you something? ",
            "i've been feeling kinda off today",
            "honestly i just needed to talk to you",
        ]
        return random.choice(vulnerable_lines)

    @staticmethod
    async def playful_challenge_strategy(context, topic: Topic) -> str:
        """Create fun tension"""
        if topic.category == TopicCategory.PLAYFUL and topic.entry_lines:
            return random.choice(topic.entry_lines)
        return "ok babe i'm bored. entertain me "


class ReengagementTriggerDetector:
    """Decides when to trigger re-engagement"""

    def should_reengage(
        self,
        engagement_metrics: EngagementMetrics,
        loop_analysis: LoopAnalysis,
        context
    ) -> Tuple[bool, ReengagementDecision]:
        """
        Determine if re-engagement needed.

        Returns:
            Tuple of (should_reengage, ReengagementDecision)
        """
        decision = ReengagementDecision()

        # Check rate limiting
        if hasattr(context, 'last_re_engagement') and context.last_re_engagement:
            time_since_last = time.time() - context.last_re_engagement
            message_count = len(context.messages) if hasattr(context, 'messages') else 0

            # Min 10 messages OR 120 seconds between interventions
            if time_since_last < 120 and message_count < 10:
                return (False, decision)

        # CRITICAL: Check if user just asked a direct question - NEVER interrupt active questions
        if context.messages and len(context.messages) > 0:
            last_user_message = None
            # Find last user message
            for msg in reversed(context.messages):
                if msg.get('role') == 'user':
                    last_user_message = msg.get('content', '').lower().strip()
                    break

            if last_user_message:
                # Question detection keywords
                question_words = ['what', 'why', 'how', 'who', 'when', 'where', 'which', 'can you', 'could you', 'will you', 'would you']
                imperative_commands = ['tell me', 'talk to me', 'spill', 'share', 'explain', 'show me', 'let me know', 'give me', 'talk about']

                # Check for direct questions
                has_question_mark = '?' in last_user_message
                starts_with_question = any(last_user_message.startswith(qw) for qw in question_words)
                has_imperative = any(cmd in last_user_message for cmd in imperative_commands)

                if has_question_mark or starts_with_question or has_imperative:
                    print(f" Re-engagement blocked: User asked a direct question or gave command")
                    return (False, decision)

        # CRITICAL: Check for conversational continuity - don't interrupt natural flow
        if context.messages and len(context.messages) >= 2:
            last_ai_message = None
            # Find last AI message
            for msg in reversed(context.messages):
                if msg.get('role') in ['assistant', 'agent']:
                    last_ai_message = msg.get('content', '').lower().strip()
                    break

            if last_ai_message:
                # Phrases that naturally expect a response
                expecting_response_phrases = [
                    'random thought', 'guess what', 'want to hear', 'wanna know',
                    'tell you something', 'you know what', 'listen to this',
                    'i have to tell you', 'let me tell you'
                ]

                if any(phrase in last_ai_message for phrase in expecting_response_phrases):
                    print(f" Re-engagement blocked: AI's last message expects natural response")
                    return (False, decision)

        # Critical disengagement (immediate)
        # Lowered from 0.15 to 0.05 to reduce false positives
        if engagement_metrics.current_engagement_score < 0.05:
            decision.should_reengage = True
            decision.reason = "Critical disengagement detected"
            decision.urgency = "critical"
            decision.recommended_category = TopicCategory.RANDOM
            decision.recommended_strategy = "random_interruption"
            decision.confidence = 0.9
            return (True, decision)

        # Dead-end pattern (high priority)
        if loop_analysis.loop_detected and loop_analysis.loop_type == LoopType.DEAD_END:
            decision.should_reengage = True
            decision.reason = "Dead-end pattern detected"
            decision.urgency = "high"
            decision.recommended_category = TopicCategory.RANDOM
            decision.recommended_strategy = "random_interruption"
            decision.confidence = loop_analysis.confidence
            return (True, decision)

        # Gradual decline (planned)
        if (engagement_metrics.current_engagement_score < 0.5 and
            engagement_metrics.engagement_trend == "falling" and
            engagement_metrics.trend_velocity < -0.3):
            decision.should_reengage = True
            decision.reason = "Gradual engagement decline"
            decision.urgency = "normal"
            decision.recommended_category = TopicCategory.CALLBACK
            decision.recommended_strategy = "callback"
            decision.confidence = 0.75
            return (True, decision)

        # Loop detected
        if loop_analysis.loop_detected and loop_analysis.severity > 0.7:
            decision.should_reengage = True
            decision.reason = f"Loop detected: {loop_analysis.loop_type.value}"
            decision.urgency = "normal"

            # Choose category based on loop type
            if loop_analysis.loop_type == LoopType.INTERVIEW_MODE:
                decision.recommended_category = TopicCategory.CASUAL
                decision.recommended_strategy = "pivot"
            elif loop_analysis.loop_type == LoopType.VALIDATION_SEEKING:
                decision.recommended_category = TopicCategory.PLAYFUL
                decision.recommended_strategy = "playful_challenge"
            else:
                decision.recommended_category = TopicCategory.RANDOM
                decision.recommended_strategy = "random_interruption"

            decision.confidence = loop_analysis.confidence
            return (True, decision)

        return (False, decision)


class TopicReengagementSystem:
    """Main orchestrator for topic re-engagement"""

    def __init__(self):
        self.topic_library = TopicLibrary()
        self.topic_selector = TopicSelector(self.topic_library)
        self.trigger_detector = ReengagementTriggerDetector()
        self.strategies = ReengagementStrategies()
        self.active_attempts = []

    async def check_and_reengage(
        self,
        engagement_metrics: EngagementMetrics,
        loop_analysis: LoopAnalysis,
        context,
        current_energy: EnergySignature
    ) -> Optional[Tuple[str, Topic, RoutingPath]]:
        """
        Check if re-engagement needed and generate response.

        Returns:
            Tuple of (message, topic, forced_path) or None
        """
        # Check if should re-engage
        should_reengage, decision = self.trigger_detector.should_reengage(
            engagement_metrics, loop_analysis, context
        )

        if not should_reengage:
            return None

        # Select topic
        topic = await self.topic_selector.select_reengagement_topic(
            engagement_metrics, loop_analysis, context, current_energy, decision
        )

        if not topic:
            return None

        # Choose strategy
        strategy_func = self._get_strategy_function(decision.recommended_strategy)

        # Generate message
        message = await strategy_func(context, topic)

        # Choose forced path
        forced_path = topic.preferred_paths[0] if topic.preferred_paths else RoutingPath.RESPOND_NORMALLY

        # Record attempt
        attempt = ReengagementAttempt(
            timestamp=time.time(),
            pre_engagement_score=engagement_metrics.current_engagement_score,
            topic_used=topic,
            strategy_used=decision.recommended_strategy,
            forced_path=forced_path,
            loop_type=loop_analysis.loop_type
        )
        self.active_attempts.append(attempt)

        # Record usage
        self.topic_library.record_usage(topic, time.time())

        return (message, topic, forced_path)

    def _get_strategy_function(self, strategy_name: str) -> Callable:
        """Get strategy function by name"""
        strategy_map = {
            "callback": self.strategies.callback_strategy,
            "pivot": self.strategies.pivot_strategy,
            "random_interruption": self.strategies.random_interruption_strategy,
            "vulnerable": self.strategies.vulnerable_strategy,
            "playful_challenge": self.strategies.playful_challenge_strategy
        }
        return strategy_map.get(strategy_name, self.strategies.pivot_strategy)

    def measure_success(self, attempt: ReengagementAttempt, post_score: float):
        """Measure success of re-engagement attempt"""
        attempt.post_engagement_score = post_score
        attempt.engagement_delta = post_score - attempt.pre_engagement_score
        attempt.success = attempt.engagement_delta > 0.15
        attempt.measured = True

        # Update topic success rate
        if attempt.success:
            attempt.topic_used.success_rate = min(1.0, attempt.topic_used.success_rate + 0.1)
        else:
            attempt.topic_used.success_rate = max(0.0, attempt.topic_used.success_rate - 0.05)
