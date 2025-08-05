#!/bin/bash

echo "🚀 Deploying Inshorts News API..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

echo "✅ Dependencies installed"

# Test the application locally
echo "🧪 Testing application locally..."
python app.py &
APP_PID=$!
sleep 3

# Test if the app is running
if curl -s http://localhost:5000 > /dev/null; then
    echo "✅ Application is running locally"
    kill $APP_PID
else
    echo "❌ Application failed to start locally"
    kill $APP_PID
    exit 1
fi

echo ""
echo "🎯 Deployment Options:"
echo "1. Render (Free tier available)"
echo "2. Heroku (Free tier available)"
echo "3. PythonAnywhere (Free tier available)"
echo "4. Vercel (Free tier available)"
echo "5. Railway (Paid only)"
echo ""
echo "📋 To deploy to Render:"
echo "   - Go to https://render.com"
echo "   - Sign up/Login"
echo "   - Click 'New Web Service'"
echo "   - Connect your GitHub repository"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: gunicorn app:app"
echo ""
echo "📋 To deploy to Heroku:"
echo "   - Install Heroku CLI: brew install heroku/brew/heroku"
echo "   - Run: heroku create your-app-name"
echo "   - Run: git add . && git commit -m 'Deploy'"
echo "   - Run: git push heroku main"
echo ""
echo "📋 To deploy to PythonAnywhere:"
echo "   - Go to https://www.pythonanywhere.com"
echo "   - Sign up for free account"
echo "   - Upload your files"
echo "   - Set up WSGI configuration"
echo ""
echo "🌐 Your app is ready to deploy!"
echo "📁 Files prepared:"
echo "   - Procfile (for Heroku/Railway)"
echo "   - runtime.txt (Python version)"
echo "   - requirements.txt (dependencies)"
echo "   - render.yaml (Render configuration)"
echo "   - vercel.json (Vercel configuration)" 