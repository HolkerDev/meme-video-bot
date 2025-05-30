import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig:
    """Configuration class for the Instagram Reels Monitor Bot."""

    # Required settings
    BOT_TOKEN = os.getenv('BOT_TOKEN')

    # Optional settings
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    REACTION_EMOJI =  '🤡'
    LOG_LEVEL = os.getenv(   'LOG_LEVEL', 'INFO')

    # Instagram URL patterns
    INSTAGRAM_PATTERNS = [
        r'https?://(?:www\.)?instagram\.com/reels?/([a-zA-Z0-9_-]+)',
        r'https?://(?:www\.)?instagram\.com/p/([a-zA-Z0-9_-]+)',
        r'https?://(?:www\.)?instagram\.com/reel/([a-zA-Z0-9_-]+)',
        r'https?://instagr\.am/reels?/([a-zA-Z0-9_-]+)',
        r'https?://instagr\.am/p/([a-zA-Z0-9_-]+)',
        r'https?://instagr\.am/reel/([a-zA-Z0-9_-]+)'
    ]

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        return True
