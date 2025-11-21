"""
Quick diagnostic to test if routing agent is working
"""
import asyncio
from enhanced_main import get_conversation_system

async def test_routing():
    """Test routing agent integration"""
    print("=" * 60)
    print("ROUTING AGENT DIAGNOSTIC TEST")
    print("=" * 60)

    # Get conversation system
    system = get_conversation_system()

    # Check if routing agent exists
    print(f"\n1. Routing agent exists: {system.routing_agent is not None}")
    print(f"2. Routing agent type: {type(system.routing_agent)}")

    # Check girlfriend agent has routing agent
    print(f"3. Girlfriend agent has routing: {system.girlfriend_agent.routing_agent is not None}")

    # Start a session and send a test message
    print("\n4. Starting test session...")
    session_id = await system.start_new_session()
    print(f"   Session ID: {session_id}")

    # Send a simple test message
    print("\n5. Sending test message: 'hello'")
    print("   Watch for routing logs below:")
    print("-" * 60)

    response = await system.send_message("hello")

    print("-" * 60)
    print(f"\n6. Response received: {response[:100]}...")
    print("\n✓ Test complete! Check the logs above for routing decisions.")

if __name__ == "__main__":
    asyncio.run(test_routing())
