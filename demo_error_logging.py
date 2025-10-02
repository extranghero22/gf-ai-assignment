"""
Demo script showing AI error logging in action
"""

import asyncio
from ai_error_logger import (
    log_conversation_disconnect, log_api_error, log_fallback_used,
    get_error_statistics, get_recent_errors
)

def demo_conversation_disconnect():
    """Demonstrate conversation disconnect detection"""
    print("=== DEMO: Conversation Disconnect Detection ===")
    
    # Simulate the exact scenario from the user's issue
    user_message = "Oh i am very ok. I just want you to like tell me what do you think I think right now"
    ai_response = "Hey baby! How are you doing today?"
    
    conversation_history = [
        {
            "role": "assistant", 
            "content": "Baby, are you okay? You seem a bit off. I'm here for you, always. Let's talk about it if you want. Or maybe just snuggle a bit? What do you need right now?"
        },
        {
            "role": "user", 
            "content": "Oh i am very ok. I just want you to like tell me what do you think I think right now"
        }
    ]
    
    # Log the conversation disconnect
    error_id = log_conversation_disconnect(
        user_message=user_message,
        ai_response=ai_response,
        conversation_history=conversation_history,
        context={
            "demo_scenario": "user_reported_disconnect",
            "disconnect_type": "generic_greeting_after_specific_question"
        }
    )
    
    print(f"Detected conversation disconnect: {error_id}")
    print(f"User asked: {user_message}")
    print(f"AI responded: {ai_response}")
    print(f"Issue: AI ignored the specific question and gave a generic greeting")
    print()

def demo_api_error():
    """Demonstrate API error logging"""
    print("=== DEMO: API Error Logging ===")
    
    # Simulate an API error
    error_id = log_api_error(
        model="mistral-small-latest",
        error=Exception("Rate limit exceeded"),
        user_message="What do you think about this?",
        context={
            "endpoint": "/api/chat/completions",
            "retry_count": 3
        }
    )
    
    print(f"Logged API error: {error_id}")
    print(f"Model: mistral-small-latest")
    print(f"Error: Rate limit exceeded")
    print()

def demo_fallback_usage():
    """Demonstrate fallback usage logging"""
    print("=== DEMO: Fallback Usage Logging ===")
    
    # Simulate fallback usage
    error_id = log_fallback_used(
        reason="All Mistral models failed due to capacity issues",
        user_message="Tell me a story",
        context={
            "models_tried": ["mistral-small", "mistral-medium", "mistral-large"],
            "fallback_type": "context_aware"
        }
    )
    
    print(f"Logged fallback usage: {error_id}")
    print(f"Reason: All Mistral models failed due to capacity issues")
    print()

def show_error_statistics():
    """Show current error statistics"""
    print("=== ERROR STATISTICS ===")
    
    stats = get_error_statistics()
    print(f"Total errors logged: {stats['total_errors']}")
    print(f"Errors by category: {stats['errors_by_category']}")
    print(f"Errors by severity: {stats['errors_by_severity']}")
    print()
    
    print("Recent errors:")
    recent_errors = get_recent_errors(limit=5)
    for i, error in enumerate(recent_errors, 1):
        print(f"  {i}. {error['category']} ({error['severity']}): {error['message'][:60]}...")
    print()

def main():
    """Run the demo"""
    print("AI Error Logging System Demo")
    print("=" * 50)
    print()
    
    # Run demos
    demo_conversation_disconnect()
    demo_api_error()
    demo_fallback_usage()
    
    # Show statistics
    show_error_statistics()
    
    print("Demo completed! Check the 'logs' directory for detailed error logs.")
    print("You can also access error statistics via the API endpoint: /api/errors")

if __name__ == "__main__":
    main()
