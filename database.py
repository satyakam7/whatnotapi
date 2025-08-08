"""
MongoDB Database Connection and Utilities
Provides connection to MongoDB Atlas and common database operations
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB connection and operations class"""
    
    def __init__(self, connection_string=None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string (str): MongoDB connection string. If None, uses environment variable.
        """
        if connection_string is None:
            # Try to get from environment variable first
            connection_string = os.getenv('MONGODB_URI')
            # Fallback to the provided connection string
            if connection_string is None:
                connection_string = "mongodb+srv://dbuser:Satyakam9258@circlepeatlas.wnjzy.mongodb.net/whatnot?retryWrites=true&w=majority&appName=circlepeatlas"
        
        self.connection_string = connection_string
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ismaster')
            self.db = self.client.get_default_database()
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB server selection timeout: {e}")
            raise
    
    def get_collection(self, collection_name):
        """
        Get a collection from the database
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            pymongo.collection.Collection: The collection object
        """
        if self.db is None:
            raise ConnectionError("Database connection not established")
        return self.db[collection_name]
    
    def insert_one(self, collection_name, document):
        """
        Insert a single document into a collection
        
        Args:
            collection_name (str): Name of the collection
            document (dict): Document to insert
            
        Returns:
            pymongo.results.InsertOneResult: Result of the insert operation
        """
        try:
            collection = self.get_collection(collection_name)
            # Add timestamp if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.utcnow()
            result = collection.insert_one(document)
            logger.info(f"Inserted document with id: {result.inserted_id}")
            return result
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise
    
    def insert_many(self, collection_name, documents):
        """
        Insert multiple documents into a collection
        
        Args:
            collection_name (str): Name of the collection
            documents (list): List of documents to insert
            
        Returns:
            pymongo.results.InsertManyResult: Result of the insert operation
        """
        try:
            collection = self.get_collection(collection_name)
            # Add timestamps if not present
            for document in documents:
                if 'created_at' not in document:
                    document['created_at'] = datetime.utcnow()
            result = collection.insert_many(documents)
            logger.info(f"Inserted {len(result.inserted_ids)} documents")
            return result
        except Exception as e:
            logger.error(f"Error inserting documents: {e}")
            raise
    
    def find_one(self, collection_name, query=None, projection=None):
        """
        Find a single document in a collection
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter (default: None for no filter)
            projection (dict): Fields to include/exclude (default: None)
            
        Returns:
            dict: The found document or None
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.find_one(query or {}, projection)
            return result
        except Exception as e:
            logger.error(f"Error finding document: {e}")
            raise
    
    def find_many(self, collection_name, query=None, projection=None, limit=None, sort=None):
        """
        Find multiple documents in a collection
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter (default: None for no filter)
            projection (dict): Fields to include/exclude (default: None)
            limit (int): Maximum number of documents to return (default: None)
            sort (list): Sort specification (default: None)
            
        Returns:
            list: List of found documents
        """
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query or {}, projection)
            
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            logger.error(f"Error finding documents: {e}")
            raise
    
    def update_one(self, collection_name, query, update, upsert=False):
        """
        Update a single document in a collection
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter to match the document
            update (dict): Update operations to apply
            upsert (bool): Create document if it doesn't exist (default: False)
            
        Returns:
            pymongo.results.UpdateResult: Result of the update operation
        """
        try:
            collection = self.get_collection(collection_name)
            # Add updated timestamp
            if '$set' not in update:
                update['$set'] = {}
            update['$set']['updated_at'] = datetime.utcnow()
            
            result = collection.update_one(query, update, upsert=upsert)
            logger.info(f"Updated {result.modified_count} document(s)")
            return result
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise
    
    def update_many(self, collection_name, query, update, upsert=False):
        """
        Update multiple documents in a collection
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter to match documents
            update (dict): Update operations to apply
            upsert (bool): Create documents if they don't exist (default: False)
            
        Returns:
            pymongo.results.UpdateResult: Result of the update operation
        """
        try:
            collection = self.get_collection(collection_name)
            # Add updated timestamp
            if '$set' not in update:
                update['$set'] = {}
            update['$set']['updated_at'] = datetime.utcnow()
            
            result = collection.update_many(query, update, upsert=upsert)
            logger.info(f"Updated {result.modified_count} document(s)")
            return result
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise
    
    def delete_one(self, collection_name, query):
        """
        Delete a single document from a collection
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter to match the document
            
        Returns:
            pymongo.results.DeleteResult: Result of the delete operation
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            logger.info(f"Deleted {result.deleted_count} document(s)")
            return result
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise
    
    def delete_many(self, collection_name, query):
        """
        Delete multiple documents from a collection
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter to match documents
            
        Returns:
            pymongo.results.DeleteResult: Result of the delete operation
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(query)
            logger.info(f"Deleted {result.deleted_count} document(s)")
            return result
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def count_documents(self, collection_name, query=None):
        """
        Count documents in a collection
        
        Args:
            collection_name (str): Name of the collection
            query (dict): Query filter (default: None for no filter)
            
        Returns:
            int: Number of documents
        """
        try:
            collection = self.get_collection(collection_name)
            count = collection.count_documents(query or {})
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            raise
    
    def create_index(self, collection_name, index_spec, **kwargs):
        """
        Create an index on a collection
        
        Args:
            collection_name (str): Name of the collection
            index_spec: Index specification
            **kwargs: Additional index options
            
        Returns:
            str: Name of the created index
        """
        try:
            collection = self.get_collection(collection_name)
            index_name = collection.create_index(index_spec, **kwargs)
            logger.info(f"Created index: {index_name}")
            return index_name
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise
    
    def aggregate(self, collection_name, pipeline):
        """
        Perform aggregation on a collection
        
        Args:
            collection_name (str): Name of the collection
            pipeline (list): Aggregation pipeline
            
        Returns:
            list: Aggregation results
        """
        try:
            collection = self.get_collection(collection_name)
            results = list(collection.aggregate(pipeline))
            return results
        except Exception as e:
            logger.error(f"Error in aggregation: {e}")
            raise
    
    def close_connection(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global database instance
db = None

def get_db():
    """
    Get the global database instance
    
    Returns:
        MongoDB: The database instance
    """
    global db
    if db is None:
        db = MongoDB()
    return db

def init_db():
    """Initialize the database connection"""
    global db
    db = MongoDB()
    return db

# Utility functions for common operations
def get_object_id(id_string):
    """
    Convert string to ObjectId
    
    Args:
        id_string (str): String representation of ObjectId
        
    Returns:
        bson.ObjectId: ObjectId object
    """
    try:
        return ObjectId(id_string)
    except Exception as e:
        logger.error(f"Invalid ObjectId: {id_string}")
        raise ValueError(f"Invalid ObjectId: {id_string}")

def serialize_doc(doc):
    """
    Serialize a MongoDB document for JSON response
    
    Args:
        doc (dict): MongoDB document
        
    Returns:
        dict: Serialized document
    """
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            if key == '_id' and isinstance(value, ObjectId):
                # Convert ObjectId to string, but rename to 'id' for cleaner API
                serialized['id'] = str(value)
            elif isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                serialized[key] = serialize_doc(value)
            else:
                serialized[key] = value
        return serialized
    
    # Handle other types that might not be JSON serializable
    if isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    
    return doc
