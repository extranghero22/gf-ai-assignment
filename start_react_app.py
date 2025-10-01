"""
Startup script for the React frontend with Flask backend
"""

import subprocess
import threading
import time
import os
import sys

def start_backend():
    """Start the Flask API server"""
    print("🚀 Starting Flask API server...")
    try:
        subprocess.run([sys.executable, "api_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Backend stopped")

def start_frontend():
    """Start the React development server"""
    print("📱 Starting React frontend...")
    try:
        os.chdir("frontend")
        # Use shell=True on Windows to find npm
        subprocess.run(["npm", "start"], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Frontend stopped")

def main():
    print("🌟 AI Girlfriend Chat - Starting Full Stack Application")
    print("=" * 60)
    
    # Check if frontend directory exists
    if not os.path.exists("frontend"):
        print("❌ Frontend directory not found. Please run this from the project root.")
        return
    
    # Check if node_modules exists
    if not os.path.exists("frontend/node_modules"):
        print("📦 Installing frontend dependencies...")
        os.chdir("frontend")
        subprocess.run(["npm", "install"], check=True, shell=True)
        os.chdir("..")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    print("✅ Backend started on http://localhost:5000")
    print("✅ Frontend will start on http://localhost:3000")
    print("=" * 60)
    
    try:
        # Start frontend (this will block)
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
