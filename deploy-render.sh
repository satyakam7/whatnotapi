#!/bin/bash

echo "🚀 One-Click Render Deployment for Inshorts News API"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

echo "✅ Repository ready"
echo ""
echo "🎯 Next Steps:"
echo "1. Go to https://render.com"
echo "2. Sign up/Login with GitHub"
echo "3. Click 'New Web Service'"
echo "4. Connect this repository"
echo "5. Configure:"
echo "   - Name: inshorts-news-api"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: gunicorn app:app"
echo "6. Click 'Create Web Service'"
echo ""
echo "⏱️  Your app will be live in 2-3 minutes!"
echo ""
echo "🌐 API will be available at: https://your-app-name.onrender.com"
echo "📖 API Documentation:"
echo "   - GET / - Health check"
echo "   - GET /news?category=all - All news"
echo "   - GET /news?category=top_stories - Top stories"
echo "   - GET /news?category=latest - Latest news"
echo "   - GET /news?category=trending - Trending news" 