"""
Users Database Operations
CRUD operations for user verification and management.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId

from config.database import get_collection

logger = logging.getLogger(__name__)


async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user by Telegram user ID.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        User document or None
    """
    try:
        collection = get_collection('users_verification')
        
        user = collection.find_one({'user_id': user_id})
        
        if user:
            user['_id'] = str(user['_id'])
        
        return user
    
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}", exc_info=True)
        return None


async def create_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None
) -> Optional[str]:
    """
    Create a new user record.
    
    Args:
        user_id: Telegram user ID
        username: Telegram username
        first_name: User's first name
    
    Returns:
        User ID (MongoDB ObjectId as string) if successful, None otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        # Check if user already exists
        existing = collection.find_one({'user_id': user_id})
        if existing:
            logger.warning(f"User {user_id} already exists")
            return str(existing['_id'])
        
        # Create user document
        user_doc = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'is_verified': False,
            'verified_at': None,
            'expires_at': None,
            'files_accessed_count': 0,
            'files_accessed': [],
            'last_access': datetime.now(),
            'created_at': datetime.now()
        }
        
        result = collection.insert_one(user_doc)
        
        logger.info(f"Created user: {user_id}")
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        return None


async def update_user(user_id: int, updates: Dict[str, Any]) -> bool:
    """
    Update user details.
    
    Args:
        user_id: Telegram user ID
        updates: Dictionary of fields to update
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        # Add update timestamp
        updates['updated_at'] = datetime.now()
        
        result = collection.update_one(
            {'user_id': user_id},
            {'$set': updates}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated user: {user_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error updating user: {e}", exc_info=True)
        return False


async def get_all_users(
    limit: Optional[int] = None,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Get all users with pagination.
    
    Args:
        limit: Maximum number of users to return
        skip: Number of users to skip
    
    Returns:
        List of user documents
    """
    try:
        collection = get_collection('users_verification')
        
        cursor = collection.find().sort('created_at', -1).skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        
        users = list(cursor)
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return users
    
    except Exception as e:
        logger.error(f"Error getting all users: {e}", exc_info=True)
        return []


async def get_all_users_count() -> int:
    """
    Get total number of users.
    
    Returns:
        Number of users
    """
    try:
        collection = get_collection('users_verification')
        return collection.count_documents({})
    
    except Exception as e:
        logger.error(f"Error getting users count: {e}", exc_info=True)
        return 0


async def get_verified_users() -> List[Dict[str, Any]]:
    """
    Get all currently verified users (not expired).
    
    Returns:
        List of verified user documents
    """
    try:
        collection = get_collection('users_verification')
        
        now = datetime.now()
        
        users = list(
            collection.find({
                'is_verified': True,
                'expires_at': {'$gt': now}
            }).sort('expires_at', 1)
        )
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return users
    
    except Exception as e:
        logger.error(f"Error getting verified users: {e}", exc_info=True)
        return []


async def get_verified_users_count() -> int:
    """
    Get number of currently verified users (not expired).
    
    Returns:
        Number of verified users
    """
    try:
        collection = get_collection('users_verification')
        
        now = datetime.now()
        
        return collection.count_documents({
            'is_verified': True,
            'expires_at': {'$gt': now}
        })
    
    except Exception as e:
        logger.error(f"Error getting verified users count: {e}", exc_info=True)
        return 0


async def get_active_users(since: datetime) -> List[Dict[str, Any]]:
    """
    Get users active since a specific datetime.
    
    Args:
        since: Datetime to check from
    
    Returns:
        List of active user documents
    """
    try:
        collection = get_collection('users_verification')
        
        users = list(
            collection.find({
                'last_access': {'$gte': since}
            }).sort('last_access', -1)
        )
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return users
    
    except Exception as e:
        logger.error(f"Error getting active users: {e}", exc_info=True)
        return []


async def get_users_joined_today() -> int:
    """
    Get number of users who joined today.
    
    Returns:
        Number of users joined today
    """
    try:
        collection = get_collection('users_verification')
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        return collection.count_documents({
            'created_at': {'$gte': today}
        })
    
    except Exception as e:
        logger.error(f"Error getting users joined today: {e}", exc_info=True)
        return 0


async def get_users_joined_this_week() -> int:
    """
    Get number of users who joined this week.
    
    Returns:
        Number of users joined this week
    """
    try:
        collection = get_collection('users_verification')
        
        week_ago = datetime.now() - timedelta(days=7)
        
        return collection.count_documents({
            'created_at': {'$gte': week_ago}
        })
    
    except Exception as e:
        logger.error(f"Error getting users joined this week: {e}", exc_info=True)
        return 0


async def get_users_joined_this_month() -> int:
    """
    Get number of users who joined this month.
    
    Returns:
        Number of users joined this month
    """
    try:
        collection = get_collection('users_verification')
        
        month_ago = datetime.now() - timedelta(days=30)
        
        return collection.count_documents({
            'created_at': {'$gte': month_ago}
        })
    
    except Exception as e:
        logger.error(f"Error getting users joined this month: {e}", exc_info=True)
        return 0


async def verify_user_manually(
    user_id: int,
    hours: int,
    verified_by: Optional[int] = None
) -> bool:
    """
    Manually verify a user for specified hours.
    
    Args:
        user_id: Telegram user ID
        hours: Hours to verify for
        verified_by: Admin user ID who verified
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        verified_at = datetime.now()
        expires_at = verified_at + timedelta(hours=hours)
        
        # Check if user exists
        user = collection.find_one({'user_id': user_id})
        
        if not user:
            # Create user first
            await create_user(user_id)
        
        # Update verification
        update_doc = {
            'is_verified': True,
            'verified_at': verified_at,
            'expires_at': expires_at,
            'files_accessed_count': 0,
            'files_accessed': [],
            'verified_by': verified_by,
            'updated_at': datetime.now()
        }
        
        result = collection.update_one(
            {'user_id': user_id},
            {'$set': update_doc}
        )
        
        if result.modified_count > 0 or result.matched_count > 0:
            logger.info(f"Manually verified user {user_id} for {hours} hours")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error manually verifying user: {e}", exc_info=True)
        return False


async def unverify_user(user_id: int) -> bool:
    """
    Remove verification from a user.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        result = collection.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'is_verified': False,
                    'verified_at': None,
                    'expires_at': None,
                    'updated_at': datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Unverified user: {user_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error unverifying user: {e}", exc_info=True)
        return False


async def reset_user_file_limit(user_id: int) -> bool:
    """
    Reset user's file access count to 0.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        result = collection.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'files_accessed_count': 0,
                    'files_accessed': [],
                    'updated_at': datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Reset file limit for user: {user_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error resetting user file limit: {e}", exc_info=True)
        return False


async def update_user_verification(
    user_id: int,
    expires_at: Optional[datetime] = None,
    **kwargs
) -> bool:
    """
    Update user verification details.
    
    Args:
        user_id: Telegram user ID
        expires_at: New expiry datetime
        **kwargs: Additional fields to update
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        updates = {'updated_at': datetime.now()}
        
        if expires_at:
            updates['expires_at'] = expires_at
        
        updates.update(kwargs)
        
        result = collection.update_one(
            {'user_id': user_id},
            {'$set': updates}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated verification for user: {user_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error updating user verification: {e}", exc_info=True)
        return False


async def increment_user_file_access(user_id: int, post_no: int) -> bool:
    """
    Increment user's file access count and add to accessed files.
    
    Args:
        user_id: Telegram user ID
        post_no: Post number of accessed file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        result = collection.update_one(
            {'user_id': user_id},
            {
                '$inc': {'files_accessed_count': 1},
                '$addToSet': {'files_accessed': post_no},
                '$set': {'last_access': datetime.now()}
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Incremented file access for user {user_id}, post {post_no}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error incrementing file access: {e}", exc_info=True)
        return False


async def user_has_accessed_file(user_id: int, post_no: int) -> bool:
    """
    Check if user has already accessed a specific file.
    
    Args:
        user_id: Telegram user ID
        post_no: Post number
    
    Returns:
        True if already accessed, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        user = collection.find_one({
            'user_id': user_id,
            'files_accessed': post_no
        })
        
        return user is not None
    
    except Exception as e:
        logger.error(f"Error checking file access: {e}", exc_info=True)
        return False


async def is_user_verified(user_id: int) -> bool:
    """
    Check if user is currently verified (not expired).
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        True if verified, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        now = datetime.now()
        
        user = collection.find_one({
            'user_id': user_id,
            'is_verified': True,
            'expires_at': {'$gt': now}
        })
        
        return user is not None
    
    except Exception as e:
        logger.error(f"Error checking user verification: {e}", exc_info=True)
        return False


async def cleanup_expired_verifications() -> int:
    """
    Mark expired verifications as not verified.
    
    Returns:
        Number of users updated
    """
    try:
        collection = get_collection('users_verification')
        
        now = datetime.now()
        
        result = collection.update_many(
            {
                'is_verified': True,
                'expires_at': {'$lt': now}
            },
            {
                '$set': {
                    'is_verified': False,
                    'updated_at': datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Cleaned up {result.modified_count} expired verifications")
        
        return result.modified_count
    
    except Exception as e:
        logger.error(f"Error cleaning up expired verifications: {e}", exc_info=True)
        return 0


async def get_user_stats(user_id: int) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a user.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        Dictionary with user statistics
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return {}
        
        now = datetime.now()
        is_verified = user.get('is_verified', False)
        expires_at = user.get('expires_at')
        
        time_remaining = None
        if is_verified and expires_at:
            if expires_at > now:
                delta = expires_at - now
                time_remaining = int(delta.total_seconds() / 3600)  # Hours
        
        stats = {
            'user_id': user_id,
            'username': user.get('username'),
            'is_verified': is_verified,
            'verified_at': user.get('verified_at'),
            'expires_at': expires_at,
            'time_remaining_hours': time_remaining,
            'files_accessed_count': user.get('files_accessed_count', 0),
            'files_accessed': user.get('files_accessed', []),
            'last_access': user.get('last_access'),
            'created_at': user.get('created_at')
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting user stats: {e}", exc_info=True)
        return {}


async def search_users(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search users by username or user ID.
    
    Args:
        query: Search query
        limit: Maximum number of results
    
    Returns:
        List of matching user documents
    """
    try:
        collection = get_collection('users_verification')
        
        # Try to search by user_id if query is numeric
        users = []
        
        if query.isdigit():
            user_id_query = int(query)
            users = list(
                collection.find({'user_id': user_id_query})
            )
        
        # Also search by username
        if not users:
            regex_query = {'$regex': query, '$options': 'i'}
            users = list(
                collection.find({
                    '$or': [
                        {'username': regex_query},
                        {'first_name': regex_query}
                    ]
                }).limit(limit)
            )
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return users
    
    except Exception as e:
        logger.error(f"Error searching users: {e}", exc_info=True)
        return []


async def delete_user(user_id: int) -> bool:
    """
    Delete a user record.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('users_verification')
        
        result = collection.delete_one({'user_id': user_id})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted user: {user_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        return False