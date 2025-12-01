"""
Database Configuration
Handles MongoDB connection using Motor (async driver).
"""

import logging
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import asyncio

from .settings import MONGODB_URI

logger = logging.getLogger(__name__)

# Global database client and instance
_mongo_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None

DATABASE_NAME = "telegram_bot_db"


def connect_database() -> AsyncIOMotorDatabase:
    """
    Connect to MongoDB using Motor (async).
    
    Returns:
        Database instance
    """
    global _mongo_client, _database
    
    if _database is not None:
        logger.info("Database already connected")
        return _database
    
    try:
        logger.info("Connecting to MongoDB with Motor (async)...")
        
        _mongo_client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=45000,
        )
        
        _database = _mongo_client[DATABASE_NAME]
        
        logger.info(f"Successfully connected to MongoDB: {DATABASE_NAME}")
        
        return _database
    
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise


def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance.
    
    Returns:
        Database instance
    """
    if _database is None:
        raise RuntimeError("Database not connected. Call connect_database() first.")
    
    return _database


def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """
    Get collection from database.
    
    Args:
        collection_name: Name of collection
    
    Returns:
        Collection instance (async)
    """
    db = get_database()
    return db[collection_name]


async def close_database() -> None:
    """
    Close database connection.
    """
    global _mongo_client, _database
    
    if _mongo_client is not None:
        try:
            logger.info("Closing MongoDB connection...")
            _mongo_client.close()
            _mongo_client = None
            _database = None
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB: {e}")


async def create_indexes() -> None:
    """
    Create database indexes for better performance.
    """
    try:
        logger.info("Creating database indexes...")
        
        db = get_database()
        
        # Files collection indexes
        await db['files'].create_index('post_no', unique=True)
        await db['files'].create_index('created_at')
        await db['files'].create_index([('created_at', -1)])
        
        # Users collection indexes
        await db['users_verification'].create_index('user_id', unique=True)
        await db['users_verification'].create_index('is_verified')
        await db['users_verification'].create_index('expires_at')
        await db['users_verification'].create_index([('expires_at', 1)], expireAfterSeconds=0)
        
        # Verification tokens indexes
        await db['verification_tokens'].create_index('token_id', unique=True)
        await db['verification_tokens'].create_index('user_id')
        await db['verification_tokens'].create_index('status')
        await db['verification_tokens'].create_index('expires_at')
        
        # Force sub channels indexes
        await db['force_sub_channels'].create_index('channel_username', unique=True)
        await db['force_sub_channels'].create_index('is_active')
        
        # Admin settings indexes
        await db['admin_settings'].create_index('setting_key', unique=True)
        
        # Admin logs indexes
        await db['admin_logs'].create_index('admin_id')
        await db['admin_logs'].create_index('timestamp')
        await db['admin_logs'].create_index([('timestamp', -1)])
        
        logger.info("Database indexes created successfully")
    
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


async def test_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        True if connection successful
    """
    try:
        db = get_database()
        await db.admin.command('ping')
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


async def get_database_stats() -> dict:
    """
    Get database statistics.
    
    Returns:
        Dictionary with database stats
    """
    try:
        db = get_database()
        stats = await db.command('dbStats')
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}
