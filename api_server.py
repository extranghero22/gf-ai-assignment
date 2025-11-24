"""
Flask API server for the React frontend
"""

# Fix Windows console encoding issues - MUST be at the very top
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import asyncio
import threading
import time
import json

from enhanced_main import EnhancedMultiAgentConversation, ConversationState
import random
from dotenv import load_dotenv
from enhanced_main import get_conversation_system
from typing_simulator import MultiMessageGenerator
from message_splitter import MessageSplitter
from ai_error_logger import log_ai_error, ErrorCategory, ErrorSeverity
from ghost_detector import GhostDetector, GhostDetectionConfig
from queue import Queue
from conversation_memory import get_conversation_memory

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global variables for conversation management
conversation_system = None
conversation_thread = None
conversation_running = False
message_generator = MultiMessageGenerator()
message_splitter = MessageSplitter()

# Ghost detection globals
ghost_detector = None
ghost_thread = None
ghost_message_queue = Queue()  # Queue for auto-generated messages

def _check_and_redirect_to_sexual_script(conversation_system):
    """Check latest AI response for sexual content and redirect to sexual script if needed"""
    if not conversation_system.current_session or not conversation_system.current_session.context.messages:
        return False
    
    # PREVENT LOOPING: Don't trigger sexual script if it has already been triggered or completed in this session
    if conversation_system.current_session.sexual_script_active or conversation_system.current_session.sexual_script_completed:
        print(f" Sexual script already active or completed - preventing re-trigger")
        return False
    
    # Get the latest message
    latest_message = conversation_system.current_session.context.messages[-1]
    
        # Only check agent messages that aren't already script messages
    if (latest_message.get('role') == 'agent' and 
        not latest_message.get('script_message', False) and
        not latest_message.get('group_part', False)):
        
        ai_response_content = latest_message.get('content', '')
        
        # CRISIS PROTECTION: Never redirect crisis/sadness responses
        crisis_keywords = ['loss', 'died', 'death', 'sad', 'sorrow', 'grief', 'mourn', 'miss', 'sorry', 'hurt', 'pain']
        is_crisis_response = any(word in ai_response_content.lower() for word in crisis_keywords)
        if is_crisis_response:
            print(f" Crisis protection: Blocking sexual redirection for crisis response")
            return False
        
        # Check for sexual keywords in AI response (removed generic words like 'feel')
        sexual_keywords = [
            'undress', 'naked', 'bedroom', 'body', 'sexy', 'hot',
            'horny', 'arousal', 'desire', 'passion', 'caress', 'seduce', 'tease',
            'dominate', 'submissive', 'naughty', 'dirty', 'wild', 'explore', 'intimate',
            'pleasure', 'excite', 'turn on', 'take control', 'mommy', 'baby girl'
        ]
        
        ai_response_lower = ai_response_content.lower()
        found_keywords = [kw for kw in sexual_keywords if kw in ai_response_lower]
        
        # Check if AI response is sexual enough to trigger script (keywords only)
        is_sexual_response = len(found_keywords) >= 3
        
        if is_sexual_response:
            print(f" AI Response Analysis: SEXUAL content detected!")
            print(f" Keywords found: {found_keywords}")
            print(f" AI Response: {ai_response_content[:100]}...")
            
            # Replace the sexual AI response with location question
            location_question = "Before we start... Where are you right now? In your room or somewhere more... exciting? "
            
            # Update the latest message content
            latest_message['content'] = location_question
            latest_message['script_message'] = True
            latest_message['script_message_complete'] = True
            
            # Set flags for sexual script activation
            conversation_system.energy_flags = {"status": "sexual", "reason": "Awaiting location choice"}
            conversation_system.current_session.awaiting_location_choice = True
            
            print(f" Redirecting to sexual script with location question")
            return True
    
    return False

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

def run_ghost_detector():
    """Background thread that monitors for user inactivity and sends ghost messages"""
    global ghost_detector, conversation_system, ghost_message_queue

    print("Ghost detector thread started (60 second timeout)")

    while True:
        try:
            # Only check if there's an active conversation
            if (conversation_system and
                conversation_system.current_session and
                conversation_system.current_session.state.value == "active" and
                ghost_detector):

                # Check if we should send a ghost message
                if ghost_detector.should_send_ghost_message():
                    escalation_level = ghost_detector.state.ghost_messages_sent
                    print(f"Ghost detected! Sending check-in message (level {escalation_level})")

                    # Generate ghost message through the conversation system
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        message = loop.run_until_complete(
                            conversation_system.generate_ghost_message(escalation_level)
                        )
                        if message:
                            # Add to queue for frontend to poll
                            ghost_message_queue.put({
                                "type": "ghost_message",
                                "content": message,
                                "timestamp": time.time(),
                                "escalation_level": escalation_level
                            })
                            ghost_detector.mark_ghost_message_sent()
                            print(f"Ghost message queued: {message}")
                    finally:
                        loop.close()

            # Check every 10 seconds
            time.sleep(10)

        except Exception as e:
            print(f"Ghost detector error: {e}")
            time.sleep(10)

@app.route('/api/start', methods=['POST'])
def start_conversation():
    """Start a new conversation session"""
    global conversation_system, conversation_thread, conversation_running
    global ghost_detector, ghost_thread, ghost_message_queue

    if conversation_running:
        return jsonify({"error": "Conversation already running"})

    try:
        conversation_system = get_conversation_system()

        # Initialize ghost detector with 60 second timeout for testing
        config = GhostDetectionConfig(
            timeout_seconds=60,
            max_ghost_messages=3,
            check_interval_seconds=10,
            escalation_delays=[60, 90, 120]  # 1 min, 1.5 min, 2 min
        )
        ghost_detector = GhostDetector(config)

        # Clear any old ghost messages
        while not ghost_message_queue.empty():
            ghost_message_queue.get()

        # Start conversation in background thread
        conversation_thread = threading.Thread(target=run_conversation_async)
        conversation_thread.daemon = True
        conversation_thread.start()

        # Start ghost detector thread if not already running
        if ghost_thread is None or not ghost_thread.is_alive():
            ghost_thread = threading.Thread(target=run_ghost_detector)
            ghost_thread.daemon = True
            ghost_thread.start()

        # Wait for session to be initialized (no timeout)
        while True:
            if (conversation_system.current_session and
                conversation_system.current_session.state.value == "active"):
                break
            time.sleep(0.1)

        # Initialize ghost detector with current time
        ghost_detector.update_user_activity()

        return jsonify({
            "status": "started",
            "session_id": conversation_system.current_session.session_id,
            "ghost_detection": {
                "enabled": True,
                "timeout_seconds": config.timeout_seconds
            }
        })

    except Exception as e:
        log_ai_error(
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.HIGH,
            message=f"Conversation system startup failed: {str(e)}",
            context={'function': 'start_conversation'},
            exception=e
        )
        return jsonify({"error": str(e)})

@app.route('/api/send', methods=['POST'])
def send_message():
    """Send a message to the conversation system"""
    global conversation_system
    
    if not conversation_system or not conversation_system.current_session:
        return jsonify({"error": "No active session"})
    
    # Check if session is stopped
    if conversation_system.current_session.state == ConversationState.STOPPED:
        return jsonify({"error": "Session has been stopped"})
    
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
    print(f"API STREAMING CALLED - {time.strftime('%H:%M:%S')}")
    global conversation_system, message_generator, ghost_detector

    if not conversation_system or not conversation_system.current_session:
        return jsonify({"error": "No active session"})

    # Check if session is stopped
    if conversation_system.current_session.state == ConversationState.STOPPED:
        return jsonify({"error": "Session has been stopped"})

    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "No message provided"})

    # Update ghost detector - user is active!
    if ghost_detector:
        ghost_detector.update_user_activity()
        print(f"Ghost detector reset - user sent message")
    
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
            
            # Get agent messages from the conversation context
            # Check for grouped messages (multiple agent messages added in sequence)
            if (conversation_system.current_session and 
                conversation_system.current_session.context.messages):
                
                # Check if we need to redirect to sexual script based on AI response content
                redirected = _check_and_redirect_to_sexual_script(conversation_system)
                
                # Collect agent messages - look for ALL consecutive agent messages
                agent_messages = []
                for msg in reversed(conversation_system.current_session.context.messages):
                    if msg.get('role') == 'agent':
                        agent_messages.insert(0, msg)  # Insert at beginning to maintain order
                        continue  # Keep collecting until we hit a user message
                    else:
                        # Hit a user message, stop collecting
                        break
                
                if agent_messages:
                    print(f" Found {len(agent_messages)} agent message(s) to send")
                    print(f" DEBUG - Messages collected:")
                    for i, msg in enumerate(agent_messages):
                        print(f"   {i+1}: {msg.get('content', '')[:50]}... (complete: {msg.get('script_message_complete', False)})")
                    
                    # Send all collected agent messages
                    for msg_idx, agent_msg in enumerate(agent_messages):
                        full_response = agent_msg.get('content', '')
                        
                        # Handle grouped messages (content is a list)
                        if isinstance(full_response, list):
                            # For grouped messages, send each part directly without splitting
                            print(f" Sending grouped message parts {msg_idx + 1}/{len(agent_messages)}: {len(full_response)} parts")
                            for part_idx, part_content in enumerate(full_response):
                                # Send each part as an individual message
                                yield f"data: {json.dumps({
                                    'type': 'message_part',
                                    'role': 'agent',
                                    'content': part_content.strip(),
                                    'timestamp': agent_msg['timestamp'],
                                    'is_typing': False,
                                    'typing_delay': 500,
                                    'group_part': True,
                                    'part_index': part_idx + 1,
                                    'total_parts': len(full_response)
                                })}\n\n"
                            
                            # Skip the normal message splitting for grouped content
                            continue
                        
                        # Handle single messages normally
                        print(f" Sending message {msg_idx + 1}/{len(agent_messages)}: {full_response[:100]}...")

                        # Use pre-split message_chunks if available (already split by girlfriend agent)
                        if 'message_chunks' in agent_msg and agent_msg['message_chunks']:
                            message_parts = agent_msg['message_chunks']
                            print(f" Using pre-split chunks: {len(message_parts)} parts")
                        else:
                            # Fallback: Use message splitter to create intelligent sequence based on content
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
                            print(f" Fallback split into {len(message_parts)} parts for {context} content")
                        
                        # Send each part with calculated delays
                        for i, part in enumerate(message_parts):
                            # Handle both MessageChunk (delay_before) and MessagePart (delay)
                            delay_value = getattr(part, 'delay_before', None) or getattr(part, 'delay', 0.5)

                            event_data = {
                                "type": "message_part",
                                "content": part.content,
                                "index": i,
                                "total": len(message_parts),
                                "is_typing": False,
                                "delay": delay_value,
                            }
                            print(f" Part {i+1} (delay: {delay_value}s): {part.content[:50]}...")
                            yield f"data: {json.dumps(event_data)}\n\n"

                            # Add delay between parts (except for the last one)
                            if i < len(message_parts) - 1:
                                time.sleep(delay_value)
                    
                    # Send completion event
                    completion_data = {
                        "type": "complete",
                        "energy_status": conversation_system.energy_flags,
                        "session_stopped": conversation_system.session_stopped_for_safety
                    }
                    print(f" Completion data: {completion_data}")
                    yield f"data: {json.dumps(completion_data)}\n\n"
                else:
                    # No agent messages found - but still send energy status for crisis toast
                    completion_data = {
                        "type": "complete",
                        "energy_status": conversation_system.energy_flags,
                        "session_stopped": conversation_system.session_stopped_for_safety
                    }
                    print(f" No agent messages, but sending energy status: {completion_data}")
                    yield f"data: {json.dumps(completion_data)}\n\n"
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
    global conversation_system, conversation_running, ghost_detector

    try:
        if conversation_system and conversation_system.current_session:
            # End the session
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(conversation_system._end_session("User requested stop"))

        # Reset ghost detector
        if ghost_detector:
            ghost_detector.reset()

        conversation_running = False
        return jsonify({"status": "stopped"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/poll-messages', methods=['GET'])
def poll_messages():
    """Poll for auto-generated messages (ghost messages)"""
    global ghost_message_queue, ghost_detector

    messages = []

    # Get all pending ghost messages from queue
    while not ghost_message_queue.empty():
        try:
            msg = ghost_message_queue.get_nowait()
            messages.append(msg)
        except:
            break

    # Get ghost detector status
    ghost_status = None
    if ghost_detector:
        ghost_status = ghost_detector.get_status()

    return jsonify({
        "messages": messages,
        "ghost_status": ghost_status,
        "timestamp": time.time()
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get conversation metrics"""
    global conversation_system
    
    try:
        if not conversation_system or not conversation_system.current_session:
            return jsonify({"error": "No active session"})
        
        # Check if session is stopped
        if conversation_system.current_session.state == ConversationState.STOPPED:
            return jsonify({"error": "Session has been stopped"})
        
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

# Conversation Memory Endpoints
@app.route('/api/conversation-history', methods=['GET'])
def get_conversation_history():
    """Get conversation history summary and recent messages"""
    try:
        memory = get_conversation_memory()

        if not memory.current_history:
            return jsonify({
                "status": "no_history",
                "messages": [],
                "total_messages": 0,
                "summary": "No conversation history"
            })

        return jsonify({
            "status": "ok",
            "session_id": memory.current_history.session_id,
            "created_at": memory.current_history.created_at,
            "updated_at": memory.current_history.updated_at,
            "total_messages": memory.current_history.total_messages,
            "recent_messages": memory.get_context_messages(20),
            "summary": memory.get_summary()
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/conversation-history/clear', methods=['POST'])
def clear_conversation_history():
    """Clear all conversation history"""
    try:
        memory = get_conversation_memory()
        memory.clear_history()

        return jsonify({
            "status": "cleared",
            "message": "Conversation history has been cleared"
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/conversation-history/export', methods=['POST'])
def export_conversation_history():
    """Export current conversation to a separate file"""
    try:
        memory = get_conversation_memory()

        if not memory.current_history:
            return jsonify({"error": "No conversation to export"})

        filepath = memory.export_session()

        return jsonify({
            "status": "exported",
            "filepath": filepath,
            "message": f"Conversation exported to {filepath}"
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("React frontend should connect to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
