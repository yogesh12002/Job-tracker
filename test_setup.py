#!/usr/bin/env python3
"""
Test script to verify Job Tracker Bot setup
Run this after completing the setup to ensure everything works
"""

import os
import sys
from dotenv import load_dotenv
import requests
import sqlite3

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    load_dotenv()
    
    required_vars = [
        'TELEGRAM_TOKEN',
        'BOT_TOKEN', 
        'EMAIL_USER',
        'EMAIL_PASS',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All environment variables are set")
        return True

def test_database():
    """Test database connection and table creation"""
    print("\n🔍 Testing Database...")
    
    try:
        from app.database import engine
        from app.models import Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Test connection
        conn = sqlite3.connect('applications.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        if tables:
            print(f"✅ Database connected. Tables: {[t[0] for t in tables]}")
            return True
        else:
            print("❌ No tables found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def test_telegram_token():
    """Test Telegram bot token validity"""
    print("\n🔍 Testing Telegram Bot Token...")
    
    load_dotenv()
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_TOKEN not found")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                print(f"✅ Telegram bot token valid. Bot: @{bot_info['result']['username']}")
                return True
            else:
                print(f"❌ Telegram API error: {bot_info}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram token test failed: {str(e)}")
        return False

def test_gmail_credentials():
    """Test Gmail credentials file"""
    print("\n🔍 Testing Gmail Credentials...")
    
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found")
        
        try:
            import json
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            
            if 'installed' in creds or 'web' in creds:
                print("✅ credentials.json format looks correct")
                return True
            else:
                print("❌ credentials.json format invalid")
                return False
                
        except Exception as e:
            print(f"❌ Error reading credentials.json: {str(e)}")
            return False
    else:
        print("❌ credentials.json not found")
        print("   Download from Google Cloud Console and place in project root")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    print("\n🔍 Testing Package Imports...")
    
    packages = [
        'fastapi',
        'uvicorn', 
        'sqlalchemy',
        'telegram',
        'google.auth',
        'googleapiclient',
        'apscheduler',
        'yagmail',
        'beautifulsoup4'
    ]
    
    failed_imports = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages imported successfully")
        return True

def main():
    """Run all tests"""
    print("🚀 Job Tracker Bot Setup Test\n")
    
    tests = [
        test_imports,
        test_environment_variables,
        test_database,
        test_telegram_token,
        test_gmail_credentials
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    print("📊 SETUP TEST RESULTS")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("\n✅ Your Job Tracker Bot is ready to run!")
        print("\nNext steps:")
        print("1. Start FastAPI: uvicorn app.main:app --reload")
        print("2. Start Telegram Bot: python bot.py")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print("\n❌ Please fix the issues above before running the bot")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)