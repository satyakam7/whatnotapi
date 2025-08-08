"""
Test script for the updated getNewFromAPi function
This will test the caching mechanism with MongoDB
"""

from inshorts import getNewFromAPi
from database import get_db
import json
from datetime import datetime

def test_news_api_caching():
    """Test the news API caching functionality"""
    
    print("Testing News API Caching Functionality...")
    print("=" * 50)
    
    # Get database instance
    db = get_db()
    
    # Get today's date
    today_date = datetime.now().strftime('%d%m%Y')
    print(f"Today's date: {today_date}")
    
    # Clear any existing cache for today (for testing purposes)
    print("\nClearing existing cache for today...")
    try:
        result = db.delete_many("daily", {"date": today_date})
        print(f"Deleted {result.deleted_count} existing daily cache entries")
    except Exception as e:
        print(f"Error clearing cache: {e}")
    
    # Test 1: First call (should fetch from API and cache)
    print("\n" + "="*50)
    print("TEST 1: First API call (should fetch from API)")
    print("="*50)
    
    result1 = getNewFromAPi()
    
    if result1:
        print(f"Status: {result1.get('status')}")
        print(f"Source: {result1.get('source')}")
        print(f"Total Results: {result1.get('totalResults')}")
        print(f"Cached Date: {result1.get('cached_date')}")
        
        if result1.get('articles'):
            print(f"First article title: {result1['articles'][0].get('title', 'No title')}")
    else:
        print("❌ Failed to get news data")
        return
    
    # Test 2: Second call (should fetch from cache)
    print("\n" + "="*50)
    print("TEST 2: Second API call (should fetch from cache)")
    print("="*50)
    
    result2 = getNewFromAPi()
    
    if result2:
        print(f"Status: {result2.get('status')}")
        print(f"Source: {result2.get('source')}")
        print(f"Total Results: {result2.get('totalResults')}")
        print(f"Cached Date: {result2.get('cached_date')}")
        
        if result2.get('articles'):
            print(f"First article title: {result2['articles'][0].get('title', 'No title')}")
    else:
        print("❌ Failed to get cached news data")
        return
    
    # Verify cache is working
    if result1.get('source') == 'api' and result2.get('source') == 'cache':
        print("\n✅ Caching mechanism is working correctly!")
    else:
        print("\n❌ Caching mechanism might not be working as expected")
    
    # Test 3: Check database collections
    print("\n" + "="*50)
    print("TEST 3: Database Collection Status")
    print("="*50)
    
    try:
        # Check daily collection
        daily_count = db.count_documents("daily", {"date": today_date})
        print(f"Daily collection entries for today: {daily_count}")
        
        # Check news collection
        news_count = db.count_documents("news")
        print(f"Total articles in news collection: {news_count}")
        
        # Check today's articles in news collection
        today_news_count = db.count_documents("news", {
            "cached_at": {"$regex": datetime.now().strftime('%Y-%m-%d')}
        })
        print(f"Articles added today to news collection: {today_news_count}")
        
        # Show sample daily cache entry
        daily_entry = db.find_one("daily", {"date": today_date})
        if daily_entry:
            print(f"Daily cache entry found with {len(daily_entry.get('data', []))} articles")
            print(f"Cache created at: {daily_entry.get('cached_at')}")
        
        # Show sample news entries
        sample_articles = db.find_many("news", limit=3, sort=[("created_at", -1)])
        print(f"\nSample articles from news collection:")
        for i, article in enumerate(sample_articles, 1):
            print(f"  {i}. {article.get('title', 'No title')[:50]}...")
            print(f"     Author: {article.get('author', 'Unknown')}")
            print(f"     Source: {article.get('source', {}).get('name', 'Unknown')}")
            print(f"     URL: {article.get('url', 'No URL')[:50]}...")
            print()
            
    except Exception as e:
        print(f"Error checking database collections: {e}")
    
    print("\n" + "="*50)
    print("Test completed!")
    print("="*50)

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    db = get_db()
    today_date = datetime.now().strftime('%d%m%Y')
    
    try:
        # Ask user before cleanup
        cleanup = input(f"Do you want to clean up today's cache ({today_date})? (y/N): ")
        if cleanup.lower() == 'y':
            # Delete today's daily cache
            result = db.delete_many("daily", {"date": today_date})
            print(f"✅ Deleted {result.deleted_count} daily cache entries")
            
            # Optionally delete today's news articles
            delete_news = input("Do you want to delete today's news articles too? (y/N): ")
            if delete_news.lower() == 'y':
                result = db.delete_many("news", {
                    "cached_at": {"$regex": datetime.now().strftime('%Y-%m-%d')}
                })
                print(f"✅ Deleted {result.deleted_count} news articles")
        else:
            print("Cleanup skipped")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    test_news_api_caching()
    
    # Uncomment the line below if you want to clean up test data
    # cleanup_test_data()
