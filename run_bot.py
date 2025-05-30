#!/usr/bin/env python3
"""
Instagram Reels Monitor Bot - Startup Script

This script provides an easy way to start the bot with proper error handling
and environment validation.
"""

import sys
import logging
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main startup function."""
    try:
        # Check if .env file exists
        env_file = Path(__file__).parent / ".env"
        if not env_file.exists():
            print("❌ Error: .env file not found!")
            print("📝 Please copy .env.example to .env and configure your bot token.")
            print("   cp .env.example .env")

        # Import and run bot
        from main import InstagramReelsBot

        print("🚀 Starting Instagram Reels Monitor Bot...")
        print("📱 The bot will monitor channels for Instagram Reels links")
        print("⏹️  Press Ctrl+C to stop the bot")
        print("-" * 50)

        bot = InstagramReelsBot()
        bot.run()

    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📦 Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("📝 Please check your .env file configuration")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logging.exception("Full error details:")
        sys.exit(1)

if __name__ == "__main__":
    main()
