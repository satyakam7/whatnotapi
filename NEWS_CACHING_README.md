# News API Caching System

This document explains the enhanced news API functionality that includes MongoDB caching for improved performance and data persistence.

## Overview

The `getNewFromAPi()` function has been enhanced with a sophisticated caching mechanism that:

1. **Checks for cached data**: First looks for today's news in the MongoDB `daily` collection
2. **Serves from cache**: If found, returns cached data immediately
3. **Fetches from API**: If not cached, calls the external News API
4. **Stores in database**: Saves both daily cache and individual articles
5. **Returns enhanced data**: Provides additional metadata and processing

## Database Collections

### Daily Collection (`daily`)
Stores daily news cache entries:
```json
{
  "_id": "ObjectId",
  "date": "08082025",  // ddmmyyyy format
  "data": [...],       // Array of processed articles
  "total_articles": 20,
  "api_response_status": "ok",
  "cached_at": "2025-08-08T10:30:00.000Z",
  "created_at": "2025-08-08T10:30:00.000Z"
}
```

### News Collection (`news`)
Stores individual news articles:
```json
{
  "_id": "ObjectId",
  "id": "unique-uuid-hex",
  "title": "Intel CEO Dogged by Decades of China Chip Investing, Board Work - Bloomberg.com",
  "description": "For more than three decades, Lip-Bu Tan invested in the Chinese economic boom...",
  "url": "https://www.bloomberg.com/news/articles/2025-08-08/intel-ceo-dogged-by-decades-of-china-chip-investing-board-work",
  "urlToImage": "https://assets.bwbx.io/images/users/iqjWHBFdfxIU/iw6DQKffwBew/v0/1200x800.jpg",
  "publishedAt": "2025-08-08T07:51:12Z",
  "content": "For more than three decades, Lip-Bu Tan invested in the Chinese economic boom...",
  "author": "Ian King",
  "source": {
    "id": "bloomberg",
    "name": "Bloomberg"
  },
  "cached_at": "2025-08-08T10:30:00.000Z",
  "created_at": "2025-08-08T10:30:00.000Z"
}
```

## API Endpoints

### Enhanced News API Endpoints

#### GET /newsapi
- **Description**: Gets today's news with caching
- **Response**: Enhanced news data with caching metadata
- **Example Response**:
```json
{
  "status": "ok",
  "totalResults": 20,
  "articles": [...],
  "source": "cache|api",
  "cached_date": "08082025"
}
```

#### GET /db/news/today
- **Description**: Get today's cached news with additional metadata
- **Response**:
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "totalResults": 20,
    "articles": [...],
    "source": "cache",
    "cached_date": "08082025"
  },
  "timestamp": "2025-08-08T10:30:00.000Z"
}
```

#### GET /db/news/history
- **Description**: Get historical daily news cache
- **Query Parameters**:
  - `limit` (optional): Number of entries to return (default: 10)
  - `date` (optional): Specific date in ddmmyyyy format
- **Example**: `/db/news/history?limit=5&date=07082025`

#### GET /db/news/search
- **Description**: Search news articles by title, description, or content
- **Query Parameters**:
  - `q` (required): Search query text
  - `limit` (optional): Number of results (default: 20)
- **Example**: `/db/news/search?q=technology&limit=10`

## Caching Logic Flow

```
1. getNewFromAPi() called
   ↓
2. Generate today's date (ddmmyyyy)
   ↓
3. Check daily collection for existing cache
   ↓
4. If found → Return cached data
   ↓
5. If not found → Call external News API
   ↓
6. Process API response
   ↓
7. Save to daily collection (full cache)
   ↓
8. Save individual articles to news collection
   ↓
9. Return processed data
```

## Features

### 1. Intelligent Caching
- **Daily Cache**: One cache entry per day to avoid redundant API calls
- **Article Deduplication**: Prevents duplicate articles in the news collection
- **Automatic Expiry**: Cache naturally expires daily

### 2. Enhanced Data Processing
- **Unique IDs**: Each article gets a unique UUID
- **Timestamps**: All entries include creation and caching timestamps
- **Metadata**: Additional fields for better data management

### 3. Error Handling
- **API Failures**: Graceful handling of external API failures
- **Database Errors**: Comprehensive error logging and user feedback
- **Data Validation**: Ensures data integrity before storage

### 4. Performance Benefits
- **Reduced API Calls**: Significant reduction in external API requests
- **Faster Response**: Cached data serves instantly
- **Cost Savings**: Fewer API calls mean lower costs

## Usage Examples

### Basic Usage
```python
from inshorts import getNewFromAPi

# Get today's news (cached or fresh)
news_data = getNewFromAPi()
print(f"Source: {news_data.get('source')}")  # 'cache' or 'api'
print(f"Articles: {len(news_data.get('articles', []))}")
```

### Testing the Caching
```bash
# First call - will fetch from API
curl http://localhost:5000/newsapi

# Second call - will return from cache
curl http://localhost:5000/newsapi

# Check if source field shows 'cache' on second call
```

### Searching News
```bash
# Search for technology articles
curl "http://localhost:5000/db/news/search?q=technology&limit=5"

# Search for specific terms
curl "http://localhost:5000/db/news/search?q=artificial%20intelligence"
```

### Getting Historical Data
```bash
# Get last 5 days of cached news
curl "http://localhost:5000/db/news/history?limit=5"

# Get specific date
curl "http://localhost:5000/db/news/history?date=07082025"
```

## Configuration

### Environment Variables
```env
# News API Configuration
NEWS_API_KEY=your_news_api_key_here

# MongoDB Configuration (already configured)
MONGODB_URI=mongodb+srv://dbuser:Satyakam9258@circlepeatlas.wnjzy.mongodb.net/whatnot?retryWrites=true&w=majority&appName=circlepeatlas
```

### API Rate Limits
- **NewsAPI**: 1000 requests/day for free tier
- **Caching Benefit**: Reduces to maximum 1 request/day per endpoint

## Testing

### Run Tests
```bash
# Test the caching functionality
python test_news_caching.py

# Test database operations
python test_database.py
```

### Manual Testing
```bash
# Clear today's cache for testing
python -c "
from database import get_db
from datetime import datetime
db = get_db()
today = datetime.now().strftime('%d%m%Y')
result = db.delete_many('daily', {'date': today})
print(f'Cleared {result.deleted_count} cache entries')
"
```

## Monitoring

### Database Statistics
```bash
# Get collection stats
curl http://localhost:5000/db/stats

# Check specific collections
curl http://localhost:5000/db/collections
```

### Cache Status
- Check the `source` field in API responses
- Monitor daily collection for cache entries
- Track API call frequency in logs

## Best Practices

### 1. Cache Management
- **Daily Cleanup**: Consider implementing old cache cleanup
- **Monitoring**: Monitor cache hit rates
- **Backup**: Regular database backups for important news data

### 2. Error Handling
- **Fallback Strategy**: Always have fallback for API failures
- **Logging**: Comprehensive logging for debugging
- **Validation**: Validate data before storage

### 3. Performance
- **Indexing**: Create indexes on frequently queried fields
- **Pagination**: Use pagination for large result sets
- **Compression**: Consider data compression for large articles

## Future Enhancements

### Possible Improvements
1. **Multiple Countries**: Cache news for different countries
2. **Category Caching**: Separate caching for different news categories
3. **TTL (Time To Live)**: Implement automatic cache expiry
4. **Analytics**: Track popular articles and search terms
5. **Real-time Updates**: WebSocket updates for breaking news

### Scaling Considerations
1. **Sharding**: Database sharding for large datasets
2. **CDN**: Content delivery network for images
3. **Load Balancing**: Multiple API instances
4. **Caching Layers**: Redis or Memcached for faster access

## Troubleshooting

### Common Issues

#### Cache Not Working
- Check database connection
- Verify date format (ddmmyyyy)
- Check for database permissions

#### API Failures
- Verify API key validity
- Check rate limits
- Monitor network connectivity

#### Data Inconsistency
- Check for duplicate prevention logic
- Verify timestamp handling
- Monitor data validation

### Debug Commands
```python
# Check today's cache
from database import get_db
from datetime import datetime
db = get_db()
today = datetime.now().strftime('%d%m%Y')
cache = db.find_one('daily', {'date': today})
print('Cache exists:', cache is not None)

# Check article count
count = db.count_documents('news')
print(f'Total articles: {count}')
```
