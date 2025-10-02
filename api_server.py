"""
Flask API server for the React frontend
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import asyncio
import threading
import time
import json
import random
from enhanced_main import get_conversation_system
from typing_simulator import MultiMessageGenerator
from message_splitter import MessageSplitter
from ai_error_logger import log_ai_error, ErrorCategory, ErrorSeverity

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global variables for conversation management
conversation_system = None
conversation_thread = None
conversation_running = False
message_generator = MultiMessageGenerator()
message_splitter = MessageSplitter()

def _calculate_realistic_delay(part: str, index: int, total_parts: int) -> float:
    """
    Calculate realistic typing delay based on message content and context
    
    Args:
        part: The message part being sent
        index: Current part index (0-based)
        total_parts: Total number of parts
        
    Returns:
        Delay in seconds
    """
    # Base delay range
    base_min, base_max = 0.8, 2.5
    
    # Adjust based on message content
    if "..." in part or "typing" in part.lower() or "sec" in part.lower():
        # Typing indicators - shorter delay
        delay = random.uniform(0.3, 0.8)
    elif len(part) < 10:
        # Short messages - quick response
        delay = random.uniform(0.5, 1.2)
    elif len(part) > 50:
        # Long messages - more thinking time
        delay = random.uniform(1.5, 3.0)
    elif "?" in part:
        # Questions - more thinking time
        delay = random.uniform(1.0, 2.5)
    elif "!" in part:
        # Exclamations - quick response
        delay = random.uniform(0.6, 1.5)
    else:
        # Normal messages
        delay = random.uniform(base_min, base_max)
    
    # Adjust based on position in sequence
    if index == 0:
        # First message - slightly longer (thinking time)
        delay *= 1.2
    elif index == total_parts - 2:
        # Second to last - shorter (wrapping up)
        delay *= 0.8
    
    # Add some randomness to avoid predictable patterns
    delay += random.uniform(-0.2, 0.2)
    
    # Ensure delay is within reasonable bounds
    return max(0.2, min(delay, 4.0))

def run_conversation_async():
    """Run the conversation system in a separate thread"""
    global conversation_running
    conversation_running = True
    try:
        # Start the conversation system
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_conversation_system().start_new_session())
    except Exception as e:
        print(f"Conversation error: {e}")
        log_ai_error(
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.HIGH,
            message=f"Conversation system startup failed: {str(e)}",
            context={'function': 'run_conversation_async'},
            exception=e
        )
    finally:
        conversation_running = False

@app.route('/api/start', methods=['POST'])
def start_conversation():
    """Start a new conversation session"""
    global conversation_system, conversation_thread, conversation_running
    
    if conversation_running:
        return jsonify({"error": "Conversation already running"})
    
    try:
        conversation_system = get_conversation_system()
        
        # Start conversation in background thread
        conversation_thread = threading.Thread(target=run_conversation_async)
        conversation_thread.daemon = True
        conversation_thread.start()
        
        # Wait for session to be initialized (no timeout)
        while True:
            if (conversation_system.current_session and 
                conversation_system.current_session.state.value == "active"):
                break
            time.sleep(0.1)
        
        return jsonify({
            "status": "started", 
            "session_id": conversation_system.current_session.session_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/send', methods=['POST'])
def send_message():
    """Send a message to the conversation system"""
    global conversation_system
    
    if not conversation_system or not conversation_system.current_session:
        return jsonify({"error": "No active session"})
    
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"})
    
    try:
        # Process message and get response
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(conversation_system.process_user_response(message))
        
        # Get the last message from the conversation context
        if (conversation_system.current_session and 
            conversation_system.current_session.context.messages):
            last_message = conversation_system.current_session.context.messages[-1]
            if last_message.get('role') == 'agent':
                return jsonify({
                    "status": "sent", 
                    "ai_response": last_message.get('content', ''),
                    "energy_status": conversation_system.energy_flags
                })
        
        return jsonify({"status": "sent", "ai_response": "No response generated"})
        
    except Exception as e:
        print(f"Message processing error: {e}")
        log_ai_error(
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message=f"Message processing failed: {str(e)}",
            context={'endpoint': '/api/send', 'message': message},
            user_message=message,
            exception=e
        )
        return jsonify({"error": str(e)})

@app.route('/api/send-stream', methods=['POST'])
def send_message_stream():
    """Send a message and stream multiple responses with typing simulation"""
    global conversation_system, message_generator
    
    if not conversation_system or not conversation_system.current_session:
        return jsonify({"error": "No active session"})
    
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"})
    
    def generate_stream():
        try:
            # Process message and get response
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Process message without timeout
                loop.run_until_complete(
                    conversation_system.process_user_response(message)
                )
            except Exception as e:
                # Return error if processing fails
                error_data = {"type": "error", "message": f"Processing error: {str(e)}"}
                yield f"data: {json.dumps(error_data)}\n\n"
                
                # Log the error
                log_ai_error(
                    category=ErrorCategory.API_ERROR,
                    severity=ErrorSeverity.MEDIUM,
                    message=f"Stream processing failed: {str(e)}",
                    context={'endpoint': '/api/send-stream', 'message': message},
                    user_message=message,
                    exception=e
                )
                return
            
            # Get the last message from the conversation context
            if (conversation_system.current_session and 
                conversation_system.current_session.context.messages):
                last_message = conversation_system.current_session.context.messages[-1]
                
                if last_message.get('role') == 'agent':
                    full_response = last_message.get('content', '')
                    print(f"🔵 Sending response to frontend: {full_response[:100]}...")
                    
                    # Use message splitter to create intelligent sequence based on content
                    # Determine context from the conversation
                    context = "general"
                    if conversation_system.energy_flags:
                        if any(flag in conversation_system.energy_flags for flag in ["sexual", "intimate"]):
                            context = "sexual"
                        elif any(flag in conversation_system.energy_flags for flag in ["crisis", "emotional"]):
                            context = "crisis"
                        elif any(flag in conversation_system.energy_flags for flag in ["supportive", "caring"]):
                            context = "emotional"
                    
                    message_parts = message_splitter.split_message(full_response, context)
                    print(f"🔵 Split into {len(message_parts)} parts for {context} content")
                    
                    # Send each part with calculated delays
                    for i, part in enumerate(message_parts):
                        event_data = {
                            "type": "message_part",
                            "content": part.content,
                            "index": i,
                            "total": len(message_parts),
                            "is_typing": False,
                            "delay": part.delay,
                            "part_type": part.type
                        }
                        print(f"🔵 Part {i+1} ({part.type}, delay: {part.delay}s): {part.content[:50]}...")
                        yield f"data: {json.dumps(event_data)}\n\n"
                        
                        # Add delay between parts (except for the last one)
                        if i < len(message_parts) - 1:
                            time.sleep(part.delay)
                    
                    # Send completion event
                    completion_data = {
                        "type": "complete",
                        "energy_status": conversation_system.energy_flags
                    }
                    print(f"🔵 Completion data: {completion_data}")
                    yield f"data: {json.dumps(completion_data)}\n\n"
                else:
                    # No agent response
                    error_data = {"type": "error", "message": "No response generated"}
                    yield f"data: {json.dumps(error_data)}\n\n"
            else:
                # No session
                error_data = {"type": "error", "message": "No active session"}
                yield f"data: {json.dumps(error_data)}\n\n"
                
        except Exception as e:
            error_data = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return Response(generate_stream(), mimetype='text/event-stream')

@app.route('/api/stop', methods=['POST'])
def stop_conversation():
    """Stop the current conversation"""
    global conversation_system, conversation_running
    
    try:
        if conversation_system and conversation_system.current_session:
            # End the session
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(conversation_system._end_session("User requested stop"))
        
        conversation_running = False
        return jsonify({"status": "stopped"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get conversation metrics"""
    global conversation_system
    
    try:
        if not conversation_system or not conversation_system.current_session:
            return jsonify({"error": "No active session"})
        
        # Get session metrics
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        metrics = loop.run_until_complete(conversation_system.get_session_metrics())
        
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/errors', methods=['GET'])
def get_error_statistics():
    """Get AI error statistics and recent errors"""
    try:
        from ai_error_logger import get_error_statistics, get_recent_errors
        
        stats = get_error_statistics()
        recent_errors = get_recent_errors(limit=20)
        
        return jsonify({
            "statistics": stats,
            "recent_errors": recent_errors,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("React frontend should connect to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
