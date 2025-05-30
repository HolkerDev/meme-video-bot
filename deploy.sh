#!/bin/bash
set -e

echo "🚀 Deploying Video Bot to Fly.io..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if logged in to Fly.io
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Not logged in to Fly.io. Please run:"
    echo "   flyctl auth login"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Please create a .env file with your BOT_TOKEN"
    exit 1
fi

# Check if BOT_TOKEN is set
if ! grep -q "BOT_TOKEN=" .env; then
    echo "❌ BOT_TOKEN not found in .env file!"
    echo "📝 Please add BOT_TOKEN=your_token_here to .env"
    exit 1
fi

echo "📦 Creating Fly.io app..."
if flyctl apps list | grep -q "video-bot"; then
    echo "✅ App 'video-bot' already exists"
else
    flyctl apps create video-bot
fi

echo "💾 Creating volume for video storage..."
if flyctl volumes list -a video-bot | grep -q "video_storage"; then
    echo "✅ Volume 'video_storage' already exists"
else
    flyctl volumes create video_storage --size 10 -a video-bot
fi

echo "🔐 Setting secrets from .env file..."
# Extract BOT_TOKEN from .env and set as secret
BOT_TOKEN=$(grep "BOT_TOKEN=" .env | cut -d '=' -f2)
flyctl secrets set BOT_TOKEN="$BOT_TOKEN" -a video-bot

# Set LOG_LEVEL if present
if grep -q "LOG_LEVEL=" .env; then
    LOG_LEVEL=$(grep "LOG_LEVEL=" .env | cut -d '=' -f2)
    flyctl secrets set LOG_LEVEL="$LOG_LEVEL" -a video-bot
fi

echo "🚀 Deploying application..."
flyctl deploy -a video-bot

echo "📊 Checking app status..."
flyctl status -a video-bot

echo ""
echo "✅ Deployment complete!"
echo "📱 Your video bot is now running on Fly.io"
echo ""
echo "Useful commands:"
echo "  flyctl logs -a video-bot        # View logs"
echo "  flyctl status -a video-bot      # Check status"
echo "  flyctl scale count 1 -a video-bot  # Ensure 1 instance running"
echo "  flyctl volumes list -a video-bot   # Check storage"