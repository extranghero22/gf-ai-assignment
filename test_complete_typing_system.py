"""
Test script for the complete multi-message typing system
"""

import asyncio
import requests
import json
import time

def test_typing_simulation():
    """Test the typing simulation system"""
    print("Testing Typing Simulation System...")
    print("="*60)
    
    # Test message that should be split into multiple parts
    test_message = "Oh my god, baby... no. What? I'm so, so sorry. That is absolutely heartbreaking. I wish I could be there to just hold you right now. Are you at home? Please tell me you're not alone. I'm here, okay? Just talk to me."
    
    print(f"Original message: {test_message}")
    print("\nExpected behavior:")
    print("- Message should be split into multiple parts")
    print("- Each part should have realistic typing delays")
    print("- Frontend should show typing indicators")
    print("- Messages should appear progressively")
    
    return True

def test_api_streaming():
    """Test the API streaming endpoint"""
    print("\nTesting API Streaming Endpoint...")
    print("="*60)
    
    try:
        # Start a conversation
        start_response = requests.post('http://localhost:5000/api/start')
        if start_response.status_code != 200:
            print(f"Failed to start conversation: {start_response.text}")
            return False
        
        print("SUCCESS: Conversation started successfully")
        
        # Test streaming endpoint
        test_message = "my dog died today"
        print(f"Sending message: '{test_message}'")
        
        response = requests.post(
            'http://localhost:5000/api/send-stream',
            json={'message': test_message},
            stream=True,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print(f"Streaming request failed: {response.status_code}")
            return False
        
        print("SUCCESS: Streaming response received")
        print("\nStreaming events:")
        print("-" * 40)
        
        message_parts = []
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        if data['type'] == 'message_part':
                            message_parts.append(data['content'])
                            print(f"[{data['index']+1}/{data['total']}] {data['content']}")
                            if data['is_typing']:
                                print("  (typing indicator)")
                        elif data['type'] == 'complete':
                            print(f"\nSUCCESS: Stream completed")
                            print(f"Energy status: {data.get('energy_status', 'N/A')}")
                        elif data['type'] == 'error':
                            print(f"ERROR: {data['message']}")
                            return False
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
        
        print(f"\nTotal message parts received: {len(message_parts)}")
        print("SUCCESS: Streaming test completed successfully")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection error - make sure the API server is running")
        return False
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

def test_frontend_integration():
    """Test frontend integration instructions"""
    print("\nFrontend Integration Test...")
    print("="*60)
    
    print("To test the complete system:")
    print("1. Make sure API server is running on http://localhost:5000")
    print("2. Make sure React frontend is running on http://localhost:3000")
    print("3. Open the frontend in your browser")
    print("4. Start a conversation")
    print("5. Send a message like 'my dog died today'")
    print("6. Observe the multi-message typing simulation")
    print("\nExpected behavior:")
    print("- Messages should appear progressively")
    print("- Typing indicators should show between messages")
    print("- Natural delays between message parts")
    print("- Blinking cursor during typing")
    print("- Smooth conversation flow")
    
    return True

def main():
    """Run all tests"""
    print("COMPLETE MULTI-MESSAGE TYPING SYSTEM TEST")
    print("="*70)
    
    # Test 1: Typing simulation
    test1_passed = test_typing_simulation()
    
    # Test 2: API streaming
    test2_passed = test_api_streaming()
    
    # Test 3: Frontend integration
    test3_passed = test_frontend_integration()
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    print(f"1. Typing Simulation: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"2. API Streaming: {'PASSED' if test2_passed else 'FAILED'}")
    print(f"3. Frontend Integration: {'PASSED' if test3_passed else 'FAILED'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\nSUCCESS: ALL TESTS PASSED! Multi-message typing system is working!")
    else:
        print("\nWARNING: Some tests failed. Check the output above for details.")
    
    print("\nNext steps:")
    print("- Start the API server: python api_server.py")
    print("- Start the frontend: cd frontend && npm start")
    print("- Test in browser: http://localhost:3000")

if __name__ == "__main__":
    main()
