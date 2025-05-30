# Instagram Reels Video Bot

A Telegram bot that automatically detects Instagram Reels links in channels and downloads/reposts the videos.

## Features

- 🔍 Automatically detects Instagram Reels URLs in Telegram channels
- 📥 Downloads videos using instaloader
- 📤 Reposts videos directly to the chat
- 🎯 Reacts with emoji to processed messages
- 🤖 Supports private commands (/start, /test)

## Deployment on Fly.io

### Prerequisites

1. **Install flyctl CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly.io:**
   ```bash
   flyctl auth login
   ```

3. **Get a Telegram Bot Token:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the bot token

### Quick Deploy

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your BOT_TOKEN
   ```

2. **Deploy with one command:**
   ```bash
   ./deploy.sh
   ```

### Manual Deployment

1. **Create Fly.io app:**
   ```bash
   flyctl apps create video-bot
   ```

2. **Create storage volume (10GB):**
   ```bash
   flyctl volumes create video_storage --size 10 -a video-bot
   ```

3. **Set secrets:**
   ```bash
   flyctl secrets set BOT_TOKEN=your_bot_token_here -a video-bot
   flyctl secrets set LOG_LEVEL=INFO -a video-bot
   ```

4. **Deploy:**
   ```bash
   flyctl deploy -a video-bot
   ```

## Configuration

### Environment Variables

- `BOT_TOKEN` - Your Telegram bot token (required)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING, ERROR)
- `DOWNLOAD_DIR` - Directory for temporary video downloads (default: /app/data)

### Storage

The app uses a 10GB mounted volume at `/app/data` for temporary video downloads. Videos are automatically cleaned up after processing.

## Usage

1. **Add bot to a Telegram channel as admin**
2. **The bot will automatically:**
   - Monitor messages for Instagram Reels links
   - Download the videos
   - Repost them in the same chat
   - React with 🤡 emoji
   - Clean up temporary files

3. **Private commands:**
   - `/start` - Show help message
   - `/test <url>` - Test if a URL would be detected

## Monitoring

### Check app status:
```bash
flyctl status -a video-bot
```

### View logs:
```bash
flyctl logs -a video-bot
```

### Scale instances:
```bash
flyctl scale count 1 -a video-bot
```

### Check storage usage:
```bash
flyctl volumes list -a video-bot
```

## Supported Instagram URL Formats

- `https://www.instagram.com/reels/[id]`
- `https://www.instagram.com/p/[id]`
- `https://www.instagram.com/reel/[id]`
- `https://instagr.am/reels/[id]`
- `https://instagr.am/p/[id]`
- `https://instagr.am/reel/[id]`

## Architecture

- **Base Image:** Python 3.11-slim
- **Memory:** 1GB RAM
- **Storage:** 10GB mounted volume
- **Health Check:** HTTP endpoint on port 8080
- **Auto-scaling:** Maintains 1 running instance

## Troubleshooting

### Bot not responding:
```bash
flyctl logs -a video-bot
```

### Storage issues:
```bash
flyctl volumes list -a video-bot
flyctl volumes extend video_storage --size 20 -a video-bot
```

### Update bot token:
```bash
flyctl secrets set BOT_TOKEN=new_token -a video-bot
flyctl deploy -a video-bot
```

### Redeploy:
```bash
flyctl deploy -a video-bot
```

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token
   ```

3. **Run locally:**
   ```bash
   python run_bot.py
   ```

## License

MIT License