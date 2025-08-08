"""
Example usage of MongoDB database operations
Run this script to test the database connection and operations
"""

from database import get_db, serialize_doc
from datetime import datetime

def test_database_operations():
    """Test various database operations"""
    
    print("Testing MongoDB Database Operations...")
    
    # Get database instance
    db = get_db()
    
    # Test 1: Insert a sample article
    print("\n1. Testing Insert Operation:")
    sample_article = {
        "title": "Sample News Article",
        "content": "This is a sample news article for testing purposes.",
        "category": "technology",
        "author": "Test Author",
        "url": "https://example.com/article",
        "published_date": datetime.utcnow(),
        "views": 0
    }
    
    try:
        result = db.insert_one("articles", sample_article)
        print(f"✅ Article inserted with ID: {result.inserted_id}")
        article_id = result.inserted_id
    except Exception as e:
        print(f"❌ Error inserting article: {e}")
        return
    
    # Test 2: Find the inserted article
    print("\n2. Testing Find Operation:")
    try:
        found_article = db.find_one("articles", {"_id": article_id})
        if found_article:
            print(f"✅ Article found: {found_article['title']}")
            print(f"   Created at: {found_article['created_at']}")
        else:
            print("❌ Article not found")
    except Exception as e:
        print(f"❌ Error finding article: {e}")
    
    # Test 3: Update the article
    print("\n3. Testing Update Operation:")
    try:
        update_result = db.update_one(
            "articles", 
            {"_id": article_id}, 
            {"$set": {"views": 10, "status": "published"}}
        )
        print(f"✅ Article updated. Modified count: {update_result.modified_count}")
    except Exception as e:
        print(f"❌ Error updating article: {e}")
    
    # Test 4: Find multiple articles
    print("\n4. Testing Find Many Operation:")
    try:
        articles = db.find_many("articles", {"category": "technology"}, limit=5)
        print(f"✅ Found {len(articles)} technology articles")
        for article in articles:
            print(f"   - {article['title']}")
    except Exception as e:
        print(f"❌ Error finding articles: {e}")
    
    # Test 5: Insert sample users
    print("\n5. Testing Insert Many Operation:")
    sample_users = [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "reader",
            "preferences": ["technology", "science"]
        },
        {
            "name": "Jane Smith", 
            "email": "jane@example.com",
            "role": "editor",
            "preferences": ["politics", "business"]
        }
    ]
    
    try:
        result = db.insert_many("users", sample_users)
        print(f"✅ Inserted {len(result.inserted_ids)} users")
    except Exception as e:
        print(f"❌ Error inserting users: {e}")
    
    # Test 6: Count documents
    print("\n6. Testing Count Operation:")
    try:
        article_count = db.count_documents("articles")
        user_count = db.count_documents("users")
        print(f"✅ Total articles: {article_count}")
        print(f"✅ Total users: {user_count}")
    except Exception as e:
        print(f"❌ Error counting documents: {e}")
    
    # Test 7: Aggregation example
    print("\n7. Testing Aggregation Operation:")
    try:
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        category_stats = db.aggregate("articles", pipeline)
        print("✅ Articles by category:")
        for stat in category_stats:
            print(f"   - {stat['_id']}: {stat['count']} articles")
    except Exception as e:
        print(f"❌ Error in aggregation: {e}")
    
    # Test 8: Serialization for JSON response
    print("\n8. Testing JSON Serialization:")
    try:
        articles = db.find_many("articles", limit=2)
        serialized = serialize_doc(articles)
        print("✅ Articles serialized for JSON response:")
        for article in serialized:
            print(f"   - ID: {article['_id']} (now string)")
            print(f"   - Title: {article['title']}")
    except Exception as e:
        print(f"❌ Error in serialization: {e}")
    
    print("\n🎉 Database operations test completed!")

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    db = get_db()
    
    try:
        # Delete test articles
        result = db.delete_many("articles", {"title": "Sample News Article"})
        print(f"✅ Deleted {result.deleted_count} test articles")
        
        # Delete test users
        result = db.delete_many("users", {"email": {"$in": ["john@example.com", "jane@example.com"]}})
        print(f"✅ Deleted {result.deleted_count} test users")
        
    except Exception as e:
        print(f"❌ Error cleaning up: {e}")

if __name__ == "__main__":
    test_database_operations()
    
    # Uncomment the line below if you want to clean up test data
    # cleanup_test_data()
