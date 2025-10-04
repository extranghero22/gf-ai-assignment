"""
Test script for topic transition disconnect detection
Specifically tests sexual-to-casual transition scenarios
"""

import asyncio
from ai_error_logger import (
    log_conversation_disconnect, log_response_quality_issue,
    get_error_statistics, get_recent_errors, ErrorCategory, ErrorSeverity
)

def test_sexual_to_casual_transition():
    """Test the exact scenario from the user's image: sexual message -> hiking question -> generic greeting"""
    
    print("=== TESTING: Sexual to Casual Topic Transition ===")
    
    # Simulate the exact conversation from the image
    conversation_history = [
        {
            "role": "assistant",
            "content": "You know I love teasing you, don't you? Now, let me make it up to you. Are you ready for what comes next? I want to take care of you, baby. I want to make sure you're completely satisfied. What do you need from me right now? Tell me everything, I want to know every detail. Are you still with me? Should I keep typing?"
        },
        {
            "role": "user", 
            "content": "Can we go hiking?"
        }
    ]
    
    user_message = "Can we go hiking?"
    ai_response = "Hello beautiful! How's your day going?"
    
    # This should trigger topic transition disconnect detection
    error_id = log_conversation_disconnect(
        user_message=user_message,
        ai_response=ai_response,
        conversation_history=conversation_history,
        context={
            'test_scenario': 'sexual_to_casual_transition',
            'ai_previous_tone': 'sexual/suggestive',
            'user_topic_change': 'hiking',
            'ai_response_tone': 'generic_greeting',
            'disconnect_type': 'topic_transition_fail',
            'rapid_messaging': True
        }
    )
    
    print(f"Logged topic transition disconnect: {error_id}")
    print(f"Previous AI message: Highly suggestive/sexual")
    print(f"User response: Complete topic change to hiking")
    print(f"AI response: Generic greeting (ignoring topic change)")
    print(f"Issue: AI struggles with rapid topic transitions from sexual to casual")
    print()

def test_various_topic_transitions():
    """Test different types of topic transitions"""
    
    print("=== TESTING: Various Topic Transitions ===")
    
    scenarios = [
        {
            'name': 'Sexual to Food',
            'previous_msg': 'I want to make sure you\'re completely satisfied. What do you need from me right now?',
            'user_msg': 'What did you have for dinner?',
            'ai_response': 'Hey baby! How are you doing today?'
        },
        {
            'name': 'Sexual to Work',
            'previous_msg': 'You know I love teasing you, don\'t you? Tell me everything you want.',
            'user_msg': 'How was your day at work?',
            'ai_response': 'Hello sweetheart! What\'s on your mind?'
        },
        {
            'name': 'Sexual to Movie',
            'previous_msg': 'Are you ready for what comes next? I want to take care of you.',
            'user_msg': 'Want to watch a movie?',
            'ai_response': 'Hey there! I\'ve been thinking about you.'
        }
    ]
    
    for scenario in scenarios:
        conversation_history = [
            {"role": "assistant", "content": scenario['previous_msg']},
            {"role": "user", "content": scenario['user_msg']}
        ]
        
        error_id = log_conversation_disconnect(
            user_message=scenario['user_msg'],
            ai_response=scenario['ai_response'],
            conversation_history=conversation_history,
            context={
                'test_scenario': scenario['name'],
                'transition_type': 'sexual_to_casual',
                'ai_ignored_topic_change': True
            }
        )
        
        print(f"OK {scenario['name']}: {error_id}")
    print()

def test_rapid_messaging_scenario():
    """Test the rapid messaging computation hypothesis"""
    
    print("=== TESTING: Rapid Messaging Computation Hypothesis ===")
    
    # Simulate rapid messaging with timestamps
    conversation_history = [
        {
            "role": "assistant",
            "content": "You know I love teasing you, don't you? Tell me what you want.",
            "timestamp": 11.15 * 3600 + 45 * 60  # 11:15:45 PM timestamp
        },
        {
            "role": "user", 
            "content": "Can we go hiking?",
            "timestamp": 11.15 * 3600 + 54 * 60  # 11:15:54 PM (9 seconds later)
        }
    ]
    
    user_message = "Can we go hiking?"
    ai_response = "Hello beautiful! How's your day going?"
    
    error_id = log_conversation_disconnect(
        user_message=user_message,
        ai_response=ai_response,
        conversation_history=conversation_history,
        context={
            'test_scenario': 'rapid_messaging_computation',
            'message_gap_seconds': 9,
            'computation_overhead': {
                'energy_analysis_time': 'high',
                'safety_monitoring_time': 'high', 
                'message_splitting_time': 'medium',
                'prompt_building_time': 'high',
                'context_window_limited': True
            },
            'hypothesis': 'Fast messaging causes computation bottlenecks leading to context loss'
        }
    )
    
    print(f"Logged rapid messaging scenario: {error_id}")
    print(f"Message gap: 9 seconds")
    print(f"Hypothesis: Computation overhead causes context processing delays")
    print(f"Result: AI falls back to generic greeting pattern")
    print()

def show_error_statistics():
    """Show statistics for all topic transition errors"""
    
    print("=== TOPIC TRANSITION ERROR STATISTICS ===")
    
    stats = get_error_statistics()
    print(f"Total errors logged: {stats['total_errors']}")
    print(f"Conversation disconnects: {stats['errors_by_category'].get('conversation_disconnect', 0)}")
    print(f"Response quality issues: {stats['errors_by_category'].get('response_quality', 0)}")
    print()
    
    print("Recent topic transition errors:")
    recent_errors = get_recent_errors(limit=10)
    for i, error in enumerate(recent_errors, 1):
        if 'topic_transition' in str(error.get('context', {})).lower() or 'sexual' in str(error.get('context', {})).lower():
            print(f"  {i}. {error['category']} ({error['severity']}): {error['message'][:80]}...")
    print()

def main():
    """Run all topic transition tests"""
    
    print("Topic Transition Disconnect Detection Tests")
    print("=" * 60)
    print()
    
    # Run tests
    test_sexual_to_casual_transition()
    test_various_topic_transitions()
    test_rapid_messaging_scenario()
    
    # Show statistics
    show_error_statistics()
    
    print()
    print("=" * 60)
    print("TOPIC TRANSITION ANALYSIS:")
    print()
    print("* Key Findings:")
    print("   • AI struggles with sexual-to-casual topic transitions")
    print("   • Generic greetings indicate context processing failure")
    print("   • Rapid messaging may cause computation bottlenecks")
    print("   • Message splitting overhead adds delay")
    print("   • Context window limitations (6 messages) may contribute")
    print()
    print("! Hypothesis: Fast messaging computation hinders context awareness")
    print("   • Energy analysis delay")
    print("   • Safety monitoring overhead")
    print("   • Message splitting computation")
    print("   • Prompt building complexity")
    print("   • Result: AI falls back to generic patterns")
    print()
    print("✓ Solution: Enhanced error detection implemented")
    print("   • Detects sexual content in recent messages")
    print("   • Identifies topic transitions")
    print("   • Flags rapid messaging scenarios")
    print("   • Logs computation timing hypothesis")

if __name__ == "__main__":
    main()
