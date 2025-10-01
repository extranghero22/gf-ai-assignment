"""
Simple Flask Web Interface for Energy-Aware Conversation System
"""

from flask import Flask, render_template, request, jsonify
import asyncio
import json
import threading
import time
from enhanced_main import get_conversation_system, ConversationState

app = Flask(__name__)

# Global variables for web interface
conversation_thread = None
conversation_running = False

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/start', methods=['POST'])
def start_conversation():
    """Start a new conversation session"""
    global conversation_thread, conversation_running

    if conversation_running:
        return jsonify({"error": "Conversation already running"})

    def run_conversation():
        global conversation_running
        conversation_running = True
        try:
            # Start session and wait for initialization
            asyncio.run(get_conversation_system().start_new_session())
        except Exception as e:
            print(f"Conversation error: {e}")
        finally:
            conversation_running = False

    conversation_thread = threading.Thread(target=run_conversation)
    conversation_thread.daemon = True
    conversation_thread.start()
    
    # Wait for session to be fully initialized (no timeout)
    while True:
        if (get_conversation_system().current_session and 
            get_conversation_system().current_session.state == ConversationState.ACTIVE):
            break
        time.sleep(0.1)

    return jsonify({"status": "started", "session_id": get_conversation_system().current_session.session_id})

@app.route('/api/send', methods=['POST'])
def send_message():
    """Send a message to the conversation system"""
    if not get_conversation_system().current_session:
        return jsonify({"error": "No active session"})

    data = request.get_json()
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "No message provided"})

    try:
        # Process message and get response
        asyncio.run(get_conversation_system().process_user_response(message))
        
        # Get the last message from the conversation context
        if get_conversation_system().current_session and get_conversation_system().current_session.context.messages:
            last_message = get_conversation_system().current_session.context.messages[-1]
            if last_message.get('role') == 'agent':
                return jsonify({
                    "status": "sent", 
                    "ai_response": last_message.get('content', ''),
                    "energy_status": get_conversation_system().energy_flags
                })
        
        return jsonify({"status": "sent", "ai_response": "No response generated"})
        
    except Exception as e:
        print(f"Message processing error: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get current session metrics"""
    if not get_conversation_system().current_session:
        return jsonify({"error": "No active session"})

    try:
        metrics = asyncio.run(get_conversation_system().get_session_metrics())
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current conversation status"""
    return jsonify({
        "running": conversation_running,
        "session_active": get_conversation_system().current_session is not None,
        "session_state": get_conversation_system().current_session.state.value if get_conversation_system().current_session else "none",
        "energy_flags": get_conversation_system().energy_flags
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
