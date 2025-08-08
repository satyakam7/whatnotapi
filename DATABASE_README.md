# MongoDB Database Integration

This project now includes MongoDB Atlas integration for storing and retrieving data. The database connection is configured to work with your MongoDB Atlas cluster.

## Setup

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

The database connection string and other configurations are stored in the `.env` file:

```env
MONGODB_URI=mongodb+srv://dbuser:Satyakam9258@circlepeatlas.wnjzy.mongodb.net/whatnot?retryWrites=true&w=majority&appName=circlepeatlas
```

### 3. Test Database Connection

Run the test script to verify your database connection:

```bash
python test_database.py
```

## Database Operations

### Basic Usage

```python
from database import get_db, serialize_doc, get_object_id

# Get database instance
db = get_db()

# Insert a document
result = db.insert_one("articles", {
    "title": "Breaking News",
    "content": "This is the article content",
    "category": "technology"
})

# Find documents
articles = db.find_many("articles", {"category": "technology"})

# Update a document
db.update_one("articles", 
              {"_id": get_object_id("article_id")}, 
              {"$set": {"views": 100}})

# Delete a document
db.delete_one("articles", {"_id": get_object_id("article_id")})
```

### Available Methods

#### Insert Operations
- `insert_one(collection_name, document)` - Insert a single document
- `insert_many(collection_name, documents)` - Insert multiple documents

#### Find Operations
- `find_one(collection_name, query, projection)` - Find a single document
- `find_many(collection_name, query, projection, limit, sort)` - Find multiple documents

#### Update Operations
- `update_one(collection_name, query, update, upsert)` - Update a single document
- `update_many(collection_name, query, update, upsert)` - Update multiple documents

#### Delete Operations
- `delete_one(collection_name, query)` - Delete a single document
- `delete_many(collection_name, query)` - Delete multiple documents

#### Utility Operations
- `count_documents(collection_name, query)` - Count documents
- `aggregate(collection_name, pipeline)` - Perform aggregation
- `create_index(collection_name, index_spec)` - Create indexes

## API Endpoints

The Flask app now includes several database API endpoints:

### Articles Collection

- **GET /db/articles** - Get all articles (supports ?category and ?limit parameters)
- **POST /db/articles** - Create a new article
- **GET /db/articles/<id>** - Get a specific article
- **PUT /db/articles/<id>** - Update an article
- **DELETE /db/articles/<id>** - Delete an article

### Users Collection

- **GET /db/users** - Get all users (supports ?limit parameter)
- **POST /db/users** - Create a new user

### Database Management

- **GET /db/collections** - List all collections
- **GET /db/stats** - Get database statistics

## Example API Usage

### Create an Article

```bash
curl -X POST http://localhost:5000/db/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Article",
    "content": "This is a sample article",
    "category": "technology",
    "author": "John Doe"
  }'
```

### Get Articles by Category

```bash
curl "http://localhost:5000/db/articles?category=technology&limit=10"
```

### Update an Article

```bash
curl -X PUT http://localhost:5000/db/articles/<article_id> \
  -H "Content-Type: application/json" \
  -d '{
    "views": 150,
    "status": "published"
  }'
```

## Data Models

### Article Document Structure

```json
{
  "_id": "ObjectId",
  "title": "string",
  "content": "string", 
  "category": "string",
  "author": "string",
  "url": "string",
  "published_date": "datetime",
  "views": "number",
  "status": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### User Document Structure

```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "role": "string",
  "preferences": ["array of strings"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Features

### Automatic Timestamps
- All documents automatically get `created_at` timestamp on insert
- Updates automatically add/update `updated_at` timestamp

### JSON Serialization
- ObjectIds and datetime objects are automatically serialized for JSON responses
- Use `serialize_doc()` function to prepare MongoDB documents for API responses

### Error Handling
- Comprehensive error handling for all database operations
- Detailed logging for debugging

### Connection Management
- Automatic connection handling
- Connection pooling via PyMongo
- Proper error handling for connection failures

## Security Notes

1. **Environment Variables**: Sensitive configuration is stored in `.env` file
2. **Input Validation**: Always validate input data before database operations
3. **Error Messages**: Avoid exposing sensitive database information in error messages
4. **Indexes**: Create appropriate indexes for better query performance

## Performance Tips

1. **Indexes**: Create indexes on frequently queried fields
2. **Pagination**: Use limit and skip for large result sets
3. **Projection**: Only fetch needed fields using projection
4. **Aggregation**: Use aggregation pipelines for complex queries

## Troubleshooting

### Connection Issues
- Verify MongoDB Atlas cluster is running
- Check network connectivity
- Ensure connection string is correct
- Verify database user permissions

### Import Errors
- Install PyMongo: `pip install pymongo`
- Check Python environment is activated

### Performance Issues
- Monitor query performance
- Create appropriate indexes
- Use aggregation for complex operations
- Implement pagination for large datasets
