import logging
import os
import re

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
from typing import List
from loader import Loader
import youtube
from src.tiktok import TiktokDownloader
from src.twitter import TwitterDownloader

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'WARNING'))
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.CRITICAL)

class InstagramReelsBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        # self.target_channel_id = os.getenv('CHANNEL_ID')
        self.reaction_emoji = '🤡'

        self.loader = Loader()
        self.tiktok = TiktokDownloader()

        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")

        # Regex patterns for Instagram Reels URLs
        self.instagram_reels_patterns = [
            r'https?://(?:www\.)?instagram\.com/reels?/([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?instagram\.com/p/([a-zA-Z0-9_-]+)',  # Posts that might be reels
            r'https?://(?:www\.)?instagram\.com/reel/([a-zA-Z0-9_-]+)',
            r'https?://instagr\.am/reels?/([a-zA-Z0-9_-]+)',
            r'https?://instagr\.am/p/([a-zA-Z0-9_-]+)',
            r'https?://instagr\.am/reel/([a-zA-Z0-9_-]+)'
        ]

        self.youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'https?://youtu\.be/([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?youtube\.com/user/([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)'
        ]

        self.twitter_patterns = [
            r'https?://(?:www\.)?x\.com/([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?x\.com/i/([a-zA-Z0-9_-]+)'
        ]

        self.tiktok_patterns = [
            r'https?://vm\.tiktok\.com/([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9_.-]+/video/([0-9]+)',
        ]

        self.twitter = TwitterDownloader()

        self.application = None

    async def is_instagram_reels_link(self, text: str) -> bool:
        if not text:
            return False

        for pattern in self.instagram_reels_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    async def is_youtube_link(self, text: str) -> bool:
        if not text:
            return False

        for pattern in self.youtube_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    async def is_twitter_link(self, text: str) -> bool:
        if not text:
            return False

        for pattern in self.twitter_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    async def is_tiktok_link(self, text: str) -> bool:
        if not text:
            return False

        for pattern in self.tiktok_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    async def extract_instagram_urls(self, text: str) -> List[str]:
        """Extract all Instagram URLs from text."""
        urls: List[str] = []
        for pattern in self.instagram_reels_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                urls.extend([match for match in matches])
        return urls

    async def handle_channel_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages from channels."""
        try:
            message = update.channel_post or update.message

            if not message:
                return

            message_text = message.text or message.caption or ""
            if await self.is_tiktok_link(message_text):
                print("TikTok link found")
                if message_text[-1] == "/":
                    message_text = message_text[0:-1]
                await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
                path = self.tiktok.download(message_text)
                await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)
                await self.application.bot.send_video(chat_id=message.chat.id, video=open(path, 'rb'))
                self.tiktok.clean(path)
                return

            if await self.is_twitter_link(message_text):
                await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
                path = self.twitter.download(message_text)
                await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)
                # Send video to the chat
                await self.application.bot.send_video(chat_id=message.chat.id, video=open(path, 'rb'))

                await message.set_reaction(self.reaction_emoji)
                logger.info(f"Successfully reacted with {self.reaction_emoji} to message {message.message_id}")
                self.twitter.clean(path)

            if await self.is_youtube_link(message_text):
                await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
                path = youtube.download_youtube_video(message_text)

                if path.endswith('.mp4'):
                    await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)
                    # Send video to the chat
                    await self.application.bot.send_video(chat_id=message.chat.id, video=open(path, 'rb'))

                await message.set_reaction(self.reaction_emoji)
                logger.info(f"Successfully reacted with {self.reaction_emoji} to message {message.message_id}")
                self.loader.clear(path)

            if await self.is_instagram_reels_link(message_text):
                logger.info(f"Found Instagram Reels link in channel {message.chat.title} (ID: {message.chat.id})")

                # Extract URLs for logging
                urls = await self.extract_instagram_urls(message_text)
                logger.info(f"Extracted URL: {urls[0]}")

                # Show typing indicator while processing
                await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

                path = self.loader.download_instagram_video(urls[0])

                if not path or not self.application:
                    logger.error(f"Failed to download Instagram Reels video")
                    return

                # Show upload video indicator while sending
                if path.endswith('.mp4'):
                    await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)
                    # Send video to the chat
                    await self.application.bot.send_video(chat_id=message.chat.id, video=open(path, 'rb'))
                elif path.endswith('.jpg'):
                    await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)
                    await self.application.bot.send_photo(chat_id=message.chat.id, photo=open(path, 'rb'))
                else:
                    logger.error(f"Unsupported file type: {path}")
                    return

                await message.set_reaction(self.reaction_emoji)
                logger.info(f"Successfully reacted with {self.reaction_emoji} to message {message.message_id}")
                self.loader.clear(path)

        except Exception as e:
            logger.error(f"Error handling channel message: {e}")

    async def handle_private_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle private messages to the bot."""
        try:
            message = update.message
            if not message:
                return

            if message.text == '/start':
                # Show typing indicator
                await context.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

                welcome_text = (
                    "🤖 Instagram Reels Monitor Bot\n\n"
                    "Add me to a channel as an admin and I'll react to messages containing Instagram Reels links!\n\n"
                    "Features:\n"
                    f"• Automatically detects Instagram Reels URLs\n"
                    f"• Reacts with {self.reaction_emoji} emoji\n"
                    "• Supports instagram.com and instagr.am domains\n\n"
                    "Commands:\n"
                    "/start - Show this help message\n"
                    "/test <instagram_url> - Test if a URL would be detected"
                )
                await message.reply_text(welcome_text)

            elif message.text and message.text.startswith('/test'):
                test_url = message.text[5:].strip()
                if test_url:
                    is_reels = await self.is_instagram_reels_link(test_url)
                    if is_reels:
                        await message.reply_text(f"✅ This URL would trigger a reaction: {test_url}")
                    else:
                        await message.reply_text(f"❌ This URL would NOT trigger a reaction: {test_url}")
                else:
                    await message.reply_text("Please provide a URL to test. Example: /test https://instagram.com/reels/abc123")

            elif await self.is_instagram_reels_link(message.text or ""):
                await message.reply_text(f"{self.reaction_emoji} This looks like an Instagram Reel!")

        except Exception as e:
            logger.error(f"Error handling private message: {e}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors."""
        logger.error(f"Update {update} caused error {context.error}")

    def run(self):
        """Run the bot."""
        try:
            # Create application
            if self.bot_token is None:
                raise ValueError("Bot token is not set")
            self.application = Application.builder().token(self.bot_token).build()

            # Add handlers
            # Handle channel posts
            self.application.add_handler(
                MessageHandler(filters.ChatType.CHANNEL, self.handle_channel_message)
            )

            # Handle private messages
            self.application.add_handler(
                MessageHandler(filters.ChatType.PRIVATE, self.handle_private_message)
            )

            # Handle group messages (in case bot is added to groups)
            self.application.add_handler(
                MessageHandler(filters.ChatType.GROUPS, self.handle_channel_message)
            )

            # Add error handler
            self.application.add_error_handler(self.error_handler)

            logger.info("Starting Instagram Reels Monitor Bot...")
            logger.info(f"Monitoring for Instagram Reels links with reaction: {self.reaction_emoji}")

            # if self.target_channel_id:
            #     logger.info(f"Monitoring specific channel ID: {self.target_channel_id}")
            # else:
            #     logger.info("Monitoring all channels the bot is added to")

            # Start the bot
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

def main():
    """Main entry point."""
    try:
        bot = InstagramReelsBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == '__main__':
    main()
