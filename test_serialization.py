"""
Test script to verify ObjectId serialization is working
"""

import sys
import json
from datetime import datetime

# Test the serialization functions
def test_serialization():
    print("Testing ObjectId serialization fixes...")
    
    try:
        from database import serialize_doc, get_db
        from bson import ObjectId
        
        # Test 1: Direct ObjectId serialization
        print("\n1. Testing direct ObjectId serialization:")
        test_id = ObjectId()
        serialized_id = serialize_doc(test_id)
        print(f"   ObjectId: {test_id}")
        print(f"   Serialized: {serialized_id}")
        print(f"   Type: {type(serialized_id)}")
        
        # Test 2: Document with ObjectId serialization
        print("\n2. Testing document serialization:")
        test_doc = {
            "_id": ObjectId(),
            "title": "Test Article",
            "created_at": datetime.now(),
            "nested": {
                "ref_id": ObjectId(),
                "timestamp": datetime.now()
            }
        }
        
        print(f"   Original doc has ObjectIds: {any(isinstance(v, ObjectId) for v in test_doc.values())}")
        
        serialized_doc = serialize_doc(test_doc)
        print(f"   Serialized doc:")
        for key, value in serialized_doc.items():
            print(f"     {key}: {value} (type: {type(value).__name__})")
        
        # Test 3: JSON serialization
        print("\n3. Testing JSON serialization:")
        try:
            json_str = json.dumps(serialized_doc)
            print(f"   ✅ JSON serialization successful")
            print(f"   JSON length: {len(json_str)} characters")
        except Exception as e:
            print(f"   ❌ JSON serialization failed: {e}")
        
        # Test 4: List of documents
        print("\n4. Testing list serialization:")
        test_list = [test_doc, test_doc.copy()]
        serialized_list = serialize_doc(test_list)
        
        try:
            json_str = json.dumps(serialized_list)
            print(f"   ✅ List JSON serialization successful")
            print(f"   List items: {len(serialized_list)}")
        except Exception as e:
            print(f"   ❌ List JSON serialization failed: {e}")
            
        print("\n✅ All serialization tests completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure pymongo is installed: pip install pymongo")
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_flask_endpoints():
    """Test the actual Flask endpoints"""
    print("\n" + "="*50)
    print("Testing Flask API endpoints...")
    print("="*50)
    
    import requests
    
    base_url = "http://localhost:5000"
    
    endpoints_to_test = [
        "/newsapi",
        "/db/news/today", 
        "/db/stats",
        "/db/collections"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ {endpoint} - Status: {response.status_code}")
                    print(f"   Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   Keys: {list(data.keys())}")
                except Exception as e:
                    print(f"   ❌ {endpoint} - JSON parsing failed: {e}")
            else:
                print(f"   ⚠️ {endpoint} - Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {endpoint} - Connection failed (is Flask app running?)")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    test_serialization()
    
    # Uncomment to test Flask endpoints (requires running Flask app)
    # test_flask_endpoints()
