# Coded by Sumanjay on 29th Feb 2020
import datetime
import uuid
import requests
import pytz
from database import get_db
from gemini_integration import generate_chats_batch


headers = {
    'authority': 'inshorts.com',
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.5',
    'content-type': 'application/json',
    'referer': 'https://inshorts.com/en/read',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
}

params = (
    ('category', 'top_stories'),
    ('max_limit', '20'),
    ('include_card_data', 'true')
)


def getNews(category):


    if category == 'all':
        response = requests.get(
            'https://inshorts.com/api/en/news?category=all_news&max_limit=10&include_card_data=true')
    else:
        response = requests.get(
            f'https://inshorts.com/api/en/search/trending_topics/{category}', headers=headers, params=params)
    try:
        news_data = response.json()['data']['news_list']
    except Exception as e:
        print(response.text)
        news_data = None

    newsDictionary = {
        'success': True,
        'category': category,
        'data': []
    }

    if not news_data:
        newsDictionary['success'] = response.json()['error']
        newsDictionary['error'] = 'Invalid Category'
        return newsDictionary

    for entry in news_data:
        try:
            news = entry['news_obj']
            author = news['author_name']
            title = news['title']
            imageUrl = news['image_url']
            url = news['shortened_url']
            content = news['content']
            timestamp = news['created_at'] / 1000
            dt_utc = datetime.datetime.utcfromtimestamp(timestamp)
            tz_utc = pytz.timezone('UTC')
            dt_utc = tz_utc.localize(dt_utc)
            tz_ist = pytz.timezone('Asia/Kolkata')
            dt_ist = dt_utc.astimezone(tz_ist)
            date = dt_ist.strftime('%A, %d %B, %Y')
            time = dt_ist.strftime('%I:%M %p').lower()
            readMoreUrl = news['source_url']

            newsObject = {
                'id': uuid.uuid4().hex,
                'title': title,
                'imageUrl': imageUrl,
                'url': url,
                'content': content,
                'author': author,
                'date': date,
                'time': time,
                'readMoreUrl': readMoreUrl
            }
            newsDictionary['data'].append(newsObject)
        except Exception:
            print(entry)
    return newsDictionary




def getNewFromAPi():
    try:
        # Get today's date in ddmmyyyy format
        today = datetime.datetime.now()
        today_date = today.strftime('%d%m%Y')
        
        # Get database instance
        db = get_db()
        
        # Check if today's news already exists in daily collection
        existing_daily_news = db.find_one("daily", {"date": today_date})
        
        if existing_daily_news:
            print(f"Found cached news for date: {today_date}")
            # Remove MongoDB-specific fields before returning
            cached_data = existing_daily_news["data"]
            return {
                "status": "ok",
                "totalResults": len(cached_data),
                "articles": cached_data,
                "source": "cache",
                "cached_date": today_date
            }
        
        # If not found in cache, call the API
        print(f"No cached news found for {today_date}, calling API...")
        response = requests.get(
            'https://newsapi.org/v2/top-headlines?country=us&apiKey=dbcc53bdfabc469ba0e146a8a1d2fa09')
        
        if response.status_code != 200:
            print(f"API request failed with status code: {response.status_code}")
            return {
                "status": "error",
                "message": "Failed to fetch news from API"
            }
        
        api_data = response.json()
        
        if api_data.get("status") != "ok":
            print(f"API returned error: {api_data}")
            return api_data
        
        # Process articles and add additional fields
        processed_articles = []
        for article in api_data.get("articles", []):
            # Extract source information properly
            source_info = article.get("source", {})
            source_id = source_info.get("id") if isinstance(source_info, dict) else None
            source_name = source_info.get("name") if isinstance(source_info, dict) else str(source_info)
            
            # Add unique ID and timestamp to each article
            processed_article = {
                "id": uuid.uuid4().hex,
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "urlToImage": article.get("urlToImage"),
                "publishedAt": article.get("publishedAt"),
                "content": article.get("content"),
                "author": article.get("author"),
                "source": {
                    "id": source_id,
                    "name": source_name
                },
                "cached_at": datetime.datetime.utcnow().isoformat(),
                "chats": []  # Will be populated by Gemini
            }
            processed_articles.append(processed_article)
        
        # Get system prompt from Google Sheets
        try:
            sys_prompt = fetch_prompt_from_sheet()
            print("Fetched system prompt from Google Sheets")
        except Exception as e:
            print(f"Error fetching prompt: {e}")
            sys_prompt = "You are a helpful news assistant. Explain news articles in a conversational way using Hindi-English mix."
        
        # Generate chats for all articles using Gemini
        print("Generating chats for articles using Gemini AI...")
        gemini_api_key = "AIzaSyA0mSmGq-SZ57Nzutk1TD3dGxcQC98LnZw"
        processed_articles = generate_chats_batch(processed_articles, sys_prompt, gemini_api_key)
        
        # Save individual articles to news collection
        for processed_article in processed_articles:
            try:
                # Check if article already exists (by URL to avoid duplicates)
                existing_article = db.find_one("news", {"url": processed_article.get("url")})
                if not existing_article:
                    db.insert_one("news", processed_article)
                    print(f"Saved article with chats: {processed_article.get('title', 'Unknown title')}")
                else:
                    print(f"Article already exists: {processed_article.get('title', 'Unknown title')}")
            except Exception as e:
                print(f"Error saving individual article: {e}")
        
        # Save daily cache entry
        daily_entry = {
            "date": today_date,
            "data": processed_articles,
            "total_articles": len(processed_articles),
            "api_response_status": api_data.get("status"),
            "cached_at": datetime.datetime.utcnow().isoformat(),
            "chats_generated": True,
            "system_prompt_used": sys_prompt[:100] + "..." if len(sys_prompt) > 100 else sys_prompt
        }
        
        try:
            db.insert_one("daily", daily_entry)
            print(f"Saved daily cache for {today_date} with {len(processed_articles)} articles and chats")
        except Exception as e:
            print(f"Error saving daily cache: {e}")
        
        # Return the processed response
        return {
            "status": "ok",
            "totalResults": len(processed_articles),
            "articles": processed_articles,
            "source": "api",
            "cached_date": today_date,
            "chats_generated": True
        }
        
    except Exception as e:
        print(f"Error in getNewFromAPi: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def fetch_prompt_from_sheet():
    """
    Fetch system prompt from Google Sheets CSV
    """
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQcbyRJdN_iIMtgncjishiFKSo-PwkoAfdwUHogw94_h3WQFcmXwNlRD9sBAB3nRXmvS0qNtNKx5GEb/pub?output=csv"
    
    try:
        res = requests.get(csv_url, timeout=10)
        res.raise_for_status()  # Raise error if request fails
        
        text = res.text.strip()  # Get CSV as string
        
        # If it's a CSV with headers, you might want to parse it properly
        # For now, returning the entire content as requested
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching prompt from sheet: {e}")
        # Return a default prompt if sheet fetch fails
        return """You are a helpful news assistant. Explain news articles in a conversational way using Hindi-English mix (Hinglish). 
        Break down complex topics into simple, engaging sentences. Use casual language that young people would understand. 
        Make it sound like you're chatting with a friend about the news."""

prompt = fetch_prompt_from_sheet()
print(prompt)


  