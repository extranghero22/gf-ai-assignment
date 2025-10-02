# AI Error Logging System

## Overview

I've implemented a comprehensive AI error logging system to address the conversation disconnect issue you reported. The system automatically detects and logs various types of AI errors, with special focus on conversation disconnects.

## What Was Implemented

### 1. Core Error Logging System (`ai_error_logger.py`)

- **Structured Error Logging**: JSON-formatted logs with comprehensive context
- **Error Categories**: API errors, conversation disconnects, response quality issues, fallback usage, etc.
- **Severity Levels**: Low, Medium, High, Critical
- **Automatic Detection**: Built-in conversation disconnect detection
- **Statistics Tracking**: Real-time error statistics and trends

### 2. Conversation Disconnect Detection

The system specifically detects the type of disconnect you experienced:

```python
# Detects when AI ignores conversation context
disconnect_indicators = [
    # Generic greetings when there's context
    ai_response.lower().startswith(('hey baby! how are you doing today?', ...)),
    
    # Not referencing previous conversation
    not any(keyword in ai_response.lower() for keyword in [
        'you said', 'you mentioned', 'you asked', 'you told me',
        'earlier', 'before', 'just now', 'you were', 'you seem'
    ]),
    
    # Complete topic change without acknowledgment
    len(ai_response) > 20 and not any(
        word in ai_response.lower() for word in 
        last_user_message.lower().split()[:5]
    )
]
```

### 3. Integration Points

- **Girlfriend Agent**: Automatic disconnect detection after each response
- **API Server**: Error logging for all API endpoints
- **Error Statistics**: Real-time tracking via `/api/errors` endpoint

## How It Works

### Automatic Detection

When the AI generates a response, the system automatically:

1. **Checks for conversation context** - Ensures there's conversation history
2. **Analyzes response patterns** - Looks for generic greetings, lack of context references
3. **Logs disconnects** - Records detailed information about the disconnect
4. **Tracks statistics** - Updates error counts and categories

### Log Structure

Each error log entry contains:

```json
{
  "error_id": "ERR_1759417989207_4661",
  "timestamp": 1759417989.207,
  "datetime": "2025-10-02T23:13:09.207000",
  "category": "conversation_disconnect",
  "severity": "high",
  "message": "AI response does not maintain conversation context",
  "context": {
    "disconnect_indicators": {
      "generic_greeting": true,
      "no_reference": true,
      "topic_change": true
    },
    "last_user_message": "Oh i am very ok. I just want you to like tell me what do you think I think right now",
    "conversation_length": 2
  },
  "user_message": "Oh i am very ok. I just want you to like tell me what do you think I think right now",
  "ai_response": "Hey baby! How are you doing today?",
  "conversation_history": [...],
  "model_used": "mistral-small-latest",
  "fallback_used": false
}
```

## Usage

### Viewing Error Statistics

```bash
# Via API endpoint
curl http://localhost:5000/api/errors

# Via Python
from ai_error_logger import get_error_statistics, get_recent_errors

stats = get_error_statistics()
recent = get_recent_errors(limit=10)
```

### Log Files

- **Location**: `logs/ai_errors_YYYYMMDD.log`
- **Format**: JSON lines (one error per line)
- **Rotation**: Daily log files
- **Retention**: Configurable

### Demo Scripts

```bash
# Test the logging system
python test_error_logging.py

# See it in action
python demo_error_logging.py
```

## Error Categories

1. **`conversation_disconnect`** - AI ignores conversation context
2. **`api_error`** - API failures, rate limits, timeouts
3. **`response_quality`** - Poor or inappropriate responses
4. **`fallback_used`** - When fallback responses are used
5. **`context_loss`** - Conversation context is lost
6. **`safety_violation`** - Safety filter violations
7. **`energy_analysis_error`** - Energy analysis failures
8. **`timeout`** - Request timeouts
9. **`validation_error`** - Input validation failures

## Severity Levels

- **`low`** - Informational, fallback usage
- **`medium`** - API errors, response quality issues
- **`high`** - Conversation disconnects, context loss
- **`critical`** - System failures, safety violations

## Benefits

1. **Automatic Detection**: No manual intervention needed
2. **Comprehensive Context**: Full conversation history and error details
3. **Real-time Monitoring**: Immediate error detection and logging
4. **Trend Analysis**: Track error patterns over time
5. **Debugging Support**: Detailed information for troubleshooting
6. **API Integration**: Access error data via REST API

## Example: Your Reported Issue

The system would automatically detect and log your conversation disconnect:

```
User: "Oh i am very ok. I just want you to like tell me what do you think I think right now"
AI: "Hey baby! How are you doing today?"

DETECTED: Conversation disconnect
- Generic greeting after specific question
- No reference to previous conversation
- Complete topic change without acknowledgment
```

This gets logged as a HIGH severity `conversation_disconnect` error with full context.

## Next Steps

1. **Monitor the logs** to see when disconnects occur
2. **Analyze patterns** to identify root causes
3. **Use the data** to improve the AI's context awareness
4. **Set up alerts** for critical errors
5. **Track improvements** over time

The system is now active and will automatically log any AI errors, including conversation disconnects like the one you experienced.
