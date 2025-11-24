"""
Engagement Monitoring System - Detects conversation loops and tracks engagement
"""

import time
import re
from typing import List, Optional, Dict, Any
from statistics import mean, stdev
from engagement_types import (
    EngagementMetrics,
    LoopAnalysis,
    LoopType,
    TrendAnalysis
)
from energy_types import EnergySignature


class EngagementScorer:
    """Calculates engagement score from multiple factors"""

    WEIGHTS = {
        'message_length': 0.25,
        'emotional_expression': 0.20,
        'question_asking': 0.15,
        'response_variety': 0.15,
        'energy_intensity': 0.15,
        'conversation_depth': 0.10
    }

    def calculate_engagement_score(
        self,
        metrics: EngagementMetrics,
        context,
        current_energy: Optional[EnergySignature]
    ) -> float:
        """
        Calculate engagement score (0.0-1.0) from multiple factors.

        Args:
            metrics: Current engagement metrics
            context: Conversation context
            current_energy: Current energy signature

        Returns:
            Engagement score between 0.0 and 1.0
        """
        # Factor 1: Message Length Score
        if metrics.message_length_trend:
            avg_length = mean(metrics.message_length_trend[-5:])
            message_length_score = min(1.0, avg_length / 50.0)
        else:
            message_length_score = 0.5

        # Factor 2: Emotional Expression Score
        if metrics.emoji_density_trend and metrics.punctuation_intensity:
            avg_emoji = mean(metrics.emoji_density_trend[-5:])
            avg_punct = mean(metrics.punctuation_intensity[-5:])
            emotional_expression_score = (avg_emoji + avg_punct) / 2
        else:
            emotional_expression_score = 0.5

        # Factor 3: Question Asking Score
        if metrics.question_ratio:
            question_score = min(1.0, mean(metrics.question_ratio[-5:]))
        else:
            question_score = 0.3

        # Factor 4: Response Variety Score
        if len(metrics.message_length_trend) >= 5:
            try:
                variety = stdev(metrics.message_length_trend[-5:])
                response_variety_score = min(1.0, variety / 20.0)
            except:
                response_variety_score = 0.5
        else:
            response_variety_score = 0.5

        # Factor 5: Energy Intensity Score
        if current_energy:
            energy_intensity_score = current_energy.intensity_score
        else:
            energy_intensity_score = 0.5

        # Factor 6: Conversation Depth Score
        conversation_depth_score = metrics.conversation_depth_score

        # Calculate weighted score
        engagement_score = (
            message_length_score * self.WEIGHTS['message_length'] +
            emotional_expression_score * self.WEIGHTS['emotional_expression'] +
            question_score * self.WEIGHTS['question_asking'] +
            response_variety_score * self.WEIGHTS['response_variety'] +
            energy_intensity_score * self.WEIGHTS['energy_intensity'] +
            conversation_depth_score * self.WEIGHTS['conversation_depth']
        )

        return max(0.0, min(1.0, engagement_score))


class ConversationDepthAnalyzer:
    """Analyzes conversation depth to detect shallow exchanges"""

    DEPTH_INDICATORS = {
        'surface': {
            'keywords': ['hi', 'hey', 'yeah', 'ok', 'cool', 'nice', 'lol', 'k', 'yep', 'nah'],
            'score': 0.2
        },
        'casual': {
            'keywords': ['how', 'what', 'doing', 'day', 'good', 'fine', 'work', 'weather'],
            'score': 0.4
        },
        'engaged': {
            'keywords': ['because', 'feel', 'think', 'really', 'actually', 'guess', 'maybe', 'probably'],
            'score': 0.6
        },
        'deep': {
            'keywords': ['love', 'care', 'want', 'need', 'miss', 'dream', 'hope', 'wish', 'feel like', 'heart'],
            'score': 0.8
        }
    }

    def calculate_depth(self, message: str, context) -> float:
        """
        Calculate conversation depth (0.0-1.0).

        Args:
            message: User message
            context: Conversation context

        Returns:
            Depth score 0.0 (surface) to 1.0 (deeply engaged)
        """
        message_lower = message.lower()

        # Factor 1: Message length (longer = deeper potential)
        length_score = min(1.0, len(message) / 100.0)

        # Factor 2: Depth indicator keywords
        depth_scores = []
        for level, data in self.DEPTH_INDICATORS.items():
            if any(keyword in message_lower for keyword in data['keywords']):
                depth_scores.append(data['score'])

        keyword_score = max(depth_scores) if depth_scores else 0.3

        # Factor 3: Follow-up questions (shows thinking)
        has_followup = any(q in message_lower for q in ['why', 'how', 'what about', 'tell me more'])
        followup_score = 0.7 if has_followup else 0.3

        # Factor 4: Personal disclosure indicators
        personal_indicators = ['i feel', 'i think', 'i want', 'i need', 'i love', 'i hate', 'i wish']
        has_personal = any(ind in message_lower for ind in personal_indicators)
        personal_score = 0.8 if has_personal else 0.4

        # Weighted average
        depth_score = (
            length_score * 0.2 +
            keyword_score * 0.4 +
            followup_score * 0.2 +
            personal_score * 0.2
        )

        return max(0.0, min(1.0, depth_score))


class ConversationLoopDetector:
    """Detects repetitive conversation patterns"""

    def __init__(self):
        self.topic_keywords_history = []
        self.pattern_buffer = []

    def detect_loops(self, context) -> LoopAnalysis:
        """
        Detect conversation loops and patterns.

        Args:
            context: Conversation context

        Returns:
            LoopAnalysis with detection results
        """
        if not context or not hasattr(context, 'messages') or len(context.messages) < 6:
            return LoopAnalysis()

        # Get recent messages
        recent_messages = context.messages[-10:]

        # Check for different loop types
        interview_loop = self._detect_interview_mode(recent_messages)
        if interview_loop.loop_detected:
            return interview_loop

        validation_loop = self._detect_validation_seeking(recent_messages)
        if validation_loop.loop_detected:
            return validation_loop

        topic_exhaustion = self._detect_topic_exhaustion(recent_messages)
        if topic_exhaustion.loop_detected:
            return topic_exhaustion

        dead_end = self._detect_dead_end_pattern(recent_messages)
        if dead_end.loop_detected:
            return dead_end

        polite_disengagement = self._detect_polite_disengagement(recent_messages)
        if polite_disengagement.loop_detected:
            return polite_disengagement

        return LoopAnalysis()

    def _detect_interview_mode(self, messages: List[Dict]) -> LoopAnalysis:
        """Detect interview mode loop (AI asks Q, user answers, repeat)"""
        if len(messages) < 6:
            return LoopAnalysis()

        # Count question patterns in last 6 messages
        question_pattern_count = 0
        for i in range(0, len(messages) - 1, 2):
            if messages[i].get('role') == 'agent' and messages[i + 1].get('role') == 'user':
                ai_msg = messages[i].get('content', '')
                user_msg = messages[i + 1].get('content', '')

                # AI asks question and user gives short answer
                if '?' in ai_msg and len(user_msg.split()) < 15:
                    question_pattern_count += 1

        if question_pattern_count >= 3:
            return LoopAnalysis(
                loop_detected=True,
                loop_type=LoopType.INTERVIEW_MODE,
                severity=min(1.0, question_pattern_count / 5.0),
                consecutive_pattern_count=question_pattern_count,
                recommended_action="Switch to self-disclosure mode",
                confidence=0.85
            )

        return LoopAnalysis()

    def _detect_validation_seeking(self, messages: List[Dict]) -> LoopAnalysis:
        """Detect validation seeking loop (PATH_L overuse)"""
        path_l_count = 0
        vulnerable_keywords = ['really', 'sure', 'promise', '', 'enough', 'pretty', 'think so']

        for msg in messages:
            if msg.get('role') == 'agent':
                content = msg.get('content', '').lower()
                if any(keyword in content for keyword in vulnerable_keywords):
                    path_l_count += 1

        if path_l_count >= 3:
            return LoopAnalysis(
                loop_detected=True,
                loop_type=LoopType.VALIDATION_SEEKING,
                severity=min(1.0, path_l_count / 5.0),
                consecutive_pattern_count=path_l_count,
                recommended_action="Switch to confident/playful mode",
                confidence=0.80
            )

        return LoopAnalysis()

    def _detect_topic_exhaustion(self, messages: List[Dict]) -> LoopAnalysis:
        """Detect topic exhaustion (same topic discussed repeatedly)"""
        if len(messages) < 5:
            return LoopAnalysis()

        # Extract keywords from messages
        topic_keywords = {}
        for msg in messages:
            content = msg.get('content', '').lower()
            words = re.findall(r'\b\w+\b', content)
            # Count non-common words
            for word in words:
                if len(word) > 4 and word not in ['about', 'what', 'think', 'really']:
                    topic_keywords[word] = topic_keywords.get(word, 0) + 1

        # Find most repeated topic
        if topic_keywords:
            max_topic = max(topic_keywords.items(), key=lambda x: x[1])
            if max_topic[1] >= 4:  # Topic mentioned 4+ times
                return LoopAnalysis(
                    loop_detected=True,
                    loop_type=LoopType.TOPIC_EXHAUSTION,
                    severity=min(1.0, max_topic[1] / 6.0),
                    affected_topics=[max_topic[0]],
                    recommended_action="Pivot to new topic",
                    confidence=0.70
                )

        return LoopAnalysis()

    def _detect_dead_end_pattern(self, messages: List[Dict]) -> LoopAnalysis:
        """Detect dead-end pattern (3+ very short replies)"""
        consecutive_short = 0

        for msg in reversed(messages):
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                word_count = len(content.split())
                if word_count < 10:
                    consecutive_short += 1
                else:
                    break

        if consecutive_short >= 3:
            return LoopAnalysis(
                loop_detected=True,
                loop_type=LoopType.DEAD_END,
                severity=min(1.0, consecutive_short / 5.0),
                consecutive_pattern_count=consecutive_short,
                recommended_action="Dramatic topic shift needed",
                confidence=0.90
            )

        return LoopAnalysis()

    def _detect_polite_disengagement(self, messages: List[Dict]) -> LoopAnalysis:
        """Detect polite disengagement (user responding but losing emotion)"""
        if len(messages) < 5:
            return LoopAnalysis()

        user_messages = [m for m in messages if m.get('role') == 'user']
        if len(user_messages) < 3:
            return LoopAnalysis()

        # Track emoji/punctuation density over time
        emotion_densities = []
        for msg in user_messages[-5:]:
            content = msg.get('content', '')
            emoji_count = len(re.findall(r'[--]|[]', content))
            punct_count = content.count('!') + content.count('?')
            density = (emoji_count + punct_count) / max(1, len(content))
            emotion_densities.append(density)

        # Check if density is declining
        if len(emotion_densities) >= 3:
            first_half = mean(emotion_densities[:2])
            second_half = mean(emotion_densities[2:])
            decline = first_half - second_half

            if decline > 0.01 and second_half < 0.05:  # Significant decline
                return LoopAnalysis(
                    loop_detected=True,
                    loop_type=LoopType.POLITE_DISENGAGEMENT,
                    severity=min(1.0, decline * 20),
                    recommended_action="Create emotional connection",
                    confidence=0.75
                )

        return LoopAnalysis()


class TrendAnalyzer:
    """Analyzes engagement trends over time"""

    def analyze_trend(self, engagement_history: List[float]) -> TrendAnalysis:
        """
        Analyze engagement trend from history.

        Args:
            engagement_history: List of engagement scores over time

        Returns:
            TrendAnalysis with trend information
        """
        if len(engagement_history) < 3:
            return TrendAnalysis()

        recent_scores = engagement_history[-10:]

        # Simple linear regression for trend
        if len(recent_scores) >= 3:
            # Calculate trend using first half vs second half
            first_half = mean(recent_scores[:len(recent_scores)//2])
            second_half = mean(recent_scores[len(recent_scores)//2:])

            trend_velocity = (second_half - first_half) / max(0.1, first_half)

            # Determine direction
            if trend_velocity < -0.1:
                trend_direction = "falling"
                is_critical = trend_velocity < -0.3
            elif trend_velocity > 0.1:
                trend_direction = "rising"
                is_critical = False
            else:
                trend_direction = "stable"
                is_critical = False

            # Calculate confidence based on consistency
            try:
                confidence = 1.0 - min(1.0, stdev(recent_scores) / max(0.1, mean(recent_scores)))
            except:
                confidence = 0.5

            return TrendAnalysis(
                trend_direction=trend_direction,
                trend_velocity=trend_velocity,
                trend_confidence=confidence,
                is_critical=is_critical
            )

        return TrendAnalysis()


class EngagementMonitor:
    """Main engagement monitoring orchestrator"""

    def __init__(self):
        self.scorer = EngagementScorer()
        self.loop_detector = ConversationLoopDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.depth_analyzer = ConversationDepthAnalyzer()

    async def update_metrics(
        self,
        user_message: str,
        context,
        current_energy: Optional[EnergySignature] = None
    ) -> EngagementMetrics:
        """
        Update engagement metrics based on new message.

        Args:
            user_message: Latest user message
            context: Conversation context
            current_energy: Current energy signature

        Returns:
            Updated EngagementMetrics
        """
        # Get or create metrics
        if hasattr(context, 'engagement_metrics') and context.engagement_metrics:
            metrics = context.engagement_metrics
        else:
            metrics = EngagementMetrics()

        # Update message length trend
        word_count = len(user_message.split())
        metrics.message_length_trend.append(word_count)
        if len(metrics.message_length_trend) > 10:
            metrics.message_length_trend.pop(0)

        # Update emoji density
        emoji_count = len(re.findall(r'[-]|[]', user_message))
        emoji_density = emoji_count / max(1, len(user_message))
        metrics.emoji_density_trend.append(emoji_density)
        if len(metrics.emoji_density_trend) > 10:
            metrics.emoji_density_trend.pop(0)

        # Update punctuation intensity
        punct_count = user_message.count('!') + user_message.count('?')
        punct_intensity = punct_count / max(1, len(user_message.split()))
        metrics.punctuation_intensity.append(punct_intensity)
        if len(metrics.punctuation_intensity) > 10:
            metrics.punctuation_intensity.pop(0)

        # Update question ratio
        has_question = 1.0 if '?' in user_message else 0.0
        metrics.question_ratio.append(has_question)
        if len(metrics.question_ratio) > 10:
            metrics.question_ratio.pop(0)

        # Update engagement words
        engagement_words = ['omg', 'really', 'wow', 'seriously', 'amazing', 'love', 'hate', 'crazy']
        engagement_word_count = sum(1 for word in engagement_words if word in user_message.lower())
        metrics.engagement_words_count.append(engagement_word_count)
        if len(metrics.engagement_words_count) > 10:
            metrics.engagement_words_count.pop(0)

        # Update conversation depth
        metrics.conversation_depth_score = self.depth_analyzer.calculate_depth(user_message, context)

        # Calculate current engagement score
        metrics.current_engagement_score = self.scorer.calculate_engagement_score(
            metrics, context, current_energy
        )

        # BOOST engagement score for direct questions and commands (indicates active engagement)
        user_message_lower = user_message.lower().strip()
        question_words = ['what', 'why', 'how', 'who', 'when', 'where', 'which', 'can you', 'could you', 'will you', 'would you']
        imperative_commands = ['tell me', 'talk to me', 'spill', 'share', 'explain', 'show me', 'let me know', 'give me', 'talk about']

        has_question_mark = '?' in user_message_lower
        starts_with_question = any(user_message_lower.startswith(qw) for qw in question_words)
        has_imperative = any(cmd in user_message_lower for cmd in imperative_commands)

        if has_question_mark or starts_with_question:
            # Direct questions show high engagement - boost score significantly
            metrics.current_engagement_score = min(1.0, metrics.current_engagement_score + 0.3)
            print(f" Engagement boosted for question: {metrics.current_engagement_score:.2f}")
        elif has_imperative:
            # Imperative commands also show engagement - moderate boost
            metrics.current_engagement_score = min(1.0, metrics.current_engagement_score + 0.2)
            print(f" Engagement boosted for command: {metrics.current_engagement_score:.2f}")

        # Update engagement history in context
        if hasattr(context, 'engagement_history'):
            context.engagement_history.append(metrics.current_engagement_score)
            if len(context.engagement_history) > 20:
                context.engagement_history.pop(0)

            # Analyze trend
            trend = self.trend_analyzer.analyze_trend(context.engagement_history)
            metrics.engagement_trend = trend.trend_direction
            metrics.trend_velocity = trend.trend_velocity

        # Update dead-end count
        if word_count < 10:
            metrics.dead_end_count += 1
        else:
            metrics.dead_end_count = 0

        # Check for engagement drop
        if metrics.current_engagement_score < 0.4 and metrics.last_engagement_drop is None:
            metrics.last_engagement_drop = time.time()
        elif metrics.current_engagement_score >= 0.5:
            metrics.last_engagement_drop = None

        return metrics

    async def detect_loops(self, context) -> LoopAnalysis:
        """
        Detect conversation loops.

        Args:
            context: Conversation context

        Returns:
            LoopAnalysis
        """
        return self.loop_detector.detect_loops(context)
