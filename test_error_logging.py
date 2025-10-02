"""
Test script for AI error logging system
"""

import asyncio
import time
from ai_error_logger import (
    log_ai_error, log_conversation_disconnect, log_api_error, 
    log_fallback_used, log_response_quality_issue, 
    ErrorCategory, ErrorSeverity, get_error_statistics, get_recent_errors
)

def test_basic_error_logging():
    """Test basic error logging functionality"""
    print("Testing basic error logging...")
    
    # Test API error
    error_id = log_api_error(
        model="test-model",
        error=Exception("Test API error"),
        user_message="Test user message",
        context={"test": True}
    )
    print(f"Logged API error: {error_id}")
    
    # Test conversation disconnect
    error_id = log_conversation_disconnect(
        user_message="Oh i am very ok. I just want you to like tell me what do you think I think right now",
        ai_response="Hey baby! How are you doing today?",
        conversation_history=[
            {"role": "assistant", "content": "Baby, are you okay? You seem a bit off. I'm here for you, always. Let's talk about it if you want. Or maybe just snuggle a bit? What do you need right now?"},
            {"role": "user", "content": "Oh i am very ok. I just want you to like tell me what do you think I think right now"}
        ],
        context={"test_disconnect": True}
    )
    print(f"Logged conversation disconnect: {error_id}")
    
    # Test fallback usage
    error_id = log_fallback_used(
        reason="All models failed",
        user_message="Test message",
        context={"fallback_test": True}
    )
    print(f"Logged fallback usage: {error_id}")
    
    # Test response quality issue
    error_id = log_response_quality_issue(
        user_message="What do you think I'm thinking?",
        ai_response="Hey baby! How are you doing today?",
        issue_description="Response ignores user's specific question",
        conversation_history=[
            {"role": "user", "content": "What do you think I'm thinking?"}
        ],
        context={"quality_test": True}
    )
    print(f"Logged response quality issue: {error_id}")

def test_error_statistics():
    """Test error statistics functionality"""
    print("\nTesting error statistics...")
    
    stats = get_error_statistics()
    print(f"Total errors: {stats['total_errors']}")
    print(f"Errors by category: {stats['errors_by_category']}")
    print(f"Errors by severity: {stats['errors_by_severity']}")
    
    recent_errors = get_recent_errors(limit=5)
    print(f"Recent errors: {len(recent_errors)}")
    for error in recent_errors:
        print(f"   - {error['category']} ({error['severity']}): {error['message'][:50]}...")

def test_conversation_disconnect_detection():
    """Test the specific conversation disconnect scenario from the user's issue"""
    print("\nTesting conversation disconnect detection...")
    
    # Simulate the exact scenario from the user's description
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
    
    # This should be detected as a conversation disconnect
    error_id = log_conversation_disconnect(
        user_message=user_message,
        ai_response=ai_response,
        conversation_history=conversation_history,
        context={
            "test_scenario": "user_reported_disconnect",
            "disconnect_type": "generic_greeting_after_specific_question"
        }
    )
    
    print(f"Detected and logged conversation disconnect: {error_id}")
    print(f"   User asked: {user_message}")
    print(f"   AI responded: {ai_response}")
    print(f"   Issue: AI ignored the specific question and gave a generic greeting")

def test_error_categories():
    """Test different error categories"""
    print("\nTesting different error categories...")
    
    categories_to_test = [
        (ErrorCategory.API_ERROR, "Test API error"),
        (ErrorCategory.CONTEXT_LOSS, "Test context loss"),
        (ErrorCategory.RESPONSE_QUALITY, "Test response quality issue"),
        (ErrorCategory.SAFETY_VIOLATION, "Test safety violation"),
        (ErrorCategory.CONVERSATION_DISCONNECT, "Test conversation disconnect"),
        (ErrorCategory.ENERGY_ANALYSIS_ERROR, "Test energy analysis error"),
        (ErrorCategory.FALLBACK_USED, "Test fallback usage"),
        (ErrorCategory.TIMEOUT, "Test timeout"),
        (ErrorCategory.VALIDATION_ERROR, "Test validation error")
    ]
    
    for category, message in categories_to_test:
        error_id = log_ai_error(
            category=category,
            severity=ErrorSeverity.MEDIUM,
            message=message,
            context={"test_category": category.value}
        )
        print(f"Logged {category.value}: {error_id}")

def test_error_severities():
    """Test different error severities"""
    print("\nTesting different error severities...")
    
    severities_to_test = [
        (ErrorSeverity.LOW, "Low severity test error"),
        (ErrorSeverity.MEDIUM, "Medium severity test error"),
        (ErrorSeverity.HIGH, "High severity test error"),
        (ErrorSeverity.CRITICAL, "Critical severity test error")
    ]
    
    for severity, message in severities_to_test:
        error_id = log_ai_error(
            category=ErrorCategory.API_ERROR,
            severity=severity,
            message=message,
            context={"test_severity": severity.value}
        )
        print(f"Logged {severity.value} severity: {error_id}")

async def main():
    """Run all tests"""
    print("Starting AI Error Logging System Tests")
    print("=" * 50)
    
    try:
        test_basic_error_logging()
        test_error_statistics()
        test_conversation_disconnect_detection()
        test_error_categories()
        test_error_severities()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
        # Show final statistics
        print("\nFinal Error Statistics:")
        stats = get_error_statistics()
        print(f"   Total errors logged: {stats['total_errors']}")
        print(f"   Categories: {list(stats['errors_by_category'].keys())}")
        print(f"   Severities: {list(stats['errors_by_severity'].keys())}")
        
        print("\nRecent Errors:")
        recent = get_recent_errors(limit=3)
        for error in recent:
            print(f"   - {error['category']} ({error['severity']}): {error['message']}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
