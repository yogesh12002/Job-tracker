#!/usr/bin/env python3
"""
Convenient script to run both FastAPI server and Telegram bot
"""

import subprocess
import sys
import time
import signal
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please copy .env.example to .env and configure it.")
        return False
    
    # Check critical environment variables
    required_vars = ['TELEGRAM_TOKEN', 'EMAIL_USER']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please configure your .env file")
        return False
    
    print("✅ Requirements check passed")
    return True

def run_services():
    """Run both FastAPI and Telegram bot services"""
    if not check_requirements():
        return
    
    print("🚀 Starting Job Tracker Bot services...")
    
    # Start FastAPI server
    print("📡 Starting FastAPI server...")
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])
    
    # Wait a moment for API to start
    time.sleep(3)
    
    # Start Telegram bot
    print("🤖 Starting Telegram bot...")
    bot_process = subprocess.Popen([sys.executable, "bot.py"])
    
    print("\n" + "="*50)
    print("🎉 JOB TRACKER BOT IS RUNNING!")
    print("="*50)
    print("📡 FastAPI Server: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🤖 Telegram Bot: Running in background")
    print("\nPress Ctrl+C to stop both services")
    print("="*50)
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down services...")
        api_process.terminate()
        bot_process.terminate()
        
        # Wait for processes to terminate
        api_process.wait()
        bot_process.wait()
        
        print("✅ Services stopped successfully")
        sys.exit(0)
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Wait for processes
        api_process.wait()
        bot_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    run_services()