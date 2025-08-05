# 🚀 Inshorts News API - Deployment Guide

Your Flask application is ready to deploy! Here are the fastest deployment options:

## 🎯 Quick Deploy Options

### 1. **Render (Recommended - Free)**
- Go to [render.com](https://render.com)
- Sign up/Login with GitHub
- Click "New Web Service"
- Connect your GitHub repository
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- Click "Create Web Service"

### 2. **Heroku (Free Tier Available)**
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login and deploy
heroku login
heroku create your-app-name
git add .
git commit -m "Deploy"
git push heroku main
```

### 3. **PythonAnywhere (Free)**
- Go to [pythonanywhere.com](https://www.pythonanywhere.com)
- Sign up for free account
- Upload your files via Files tab
- Go to Web tab → Add a new web app
- Choose Flask and Python 3.11
- Set source code to `/home/yourusername/mysite`
- Set WSGI configuration file to point to your app

### 4. **Vercel (Free)**
```bash
# Install Vercel CLI
npm install -g vercel

# Login and deploy
vercel login
vercel --yes
```

## 📁 Files Prepared

✅ `Procfile` - For Heroku/Railway deployment  
✅ `runtime.txt` - Python version specification  
✅ `requirements.txt` - All dependencies  
✅ `render.yaml` - Render configuration  
✅ `vercel.json` - Vercel configuration  
✅ `app.py` - Main Flask application  
✅ `inshorts.py` - News fetching logic  

## 🧪 Test Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

## 🌐 API Endpoints

Once deployed, your API will have these endpoints:

- `GET /` - Health check
- `GET /news?category=all` - All news
- `GET /news?category=top_stories` - Top stories
- `GET /news?category=latest` - Latest news
- `GET /news?category=trending` - Trending news

## 🚀 Recommended: Render Deployment

1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub**
3. **Click "New Web Service"**
4. **Connect your GitHub repo**
5. **Configure:**
   - **Name:** `inshorts-news-api`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. **Click "Create Web Service"**

Your app will be live in 2-3 minutes! 🎉

## 📊 Expected Response Format

```json
{
  "success": true,
  "category": "top_stories",
  "data": [
    {
      "id": "unique_id",
      "title": "News Title",
      "imageUrl": "image_url",
      "url": "shortened_url",
      "content": "News content...",
      "author": "Author Name",
      "date": "Monday, 15 January, 2024",
      "time": "10:30 am",
      "readMoreUrl": "full_article_url"
    }
  ]
}
```

## 🔧 Troubleshooting

- **Port 5000 in use:** Change port in `app.py` or disable AirPlay Receiver on macOS
- **Dependencies missing:** Run `pip install -r requirements.txt`
- **CORS issues:** Already configured with `flask-cors`

## 🎉 Success!

Your Inshorts News API is now ready to deploy! Choose any of the platforms above and your API will be live in minutes. 