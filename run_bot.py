#!/usr/bin/env python3
"""
Startup script for the Content Creator Bot
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = ['TELEGRAM_TOKEN', 'FAL_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file:")
        print("1. Copy env_example.txt to .env")
        print("2. Edit .env and add your API keys")
        print("3. Run this script again")
        return False
    
    print("✅ All required environment variables are set")
    return True

def main():
    """Main startup function"""
    print("🤖 Content Creator Bot Startup")
    print("=" * 40)
    
    if not check_environment():
        sys.exit(1)
    
    print("\n🚀 Starting the bot...")
    print("Press Ctrl+C to stop the bot")
    print("=" * 40)
    
    try:
        from bot import ContentCreatorBot
        bot = ContentCreatorBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 