"""
Verification Token Database Operations
CRUD operations for verification tokens and bypass detection.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from bson import ObjectId

from config.database import get_collection
from config.settings import VERIFICATION_TOKEN_EXPIRY

logger = logging.getLogger(__name__)


async def create_verification_token(
    token_id: str,
    user_id: int,
    expiry_seconds: Optional[int] = None
) -> Optional[str]:
    """
    Create a new verification token.
    
    Args:
        token_id: Unique token ID
        user_id: Telegram user ID
        expiry_seconds: Token expiry in seconds
    
    Returns:
        Token ID (MongoDB ObjectId as string) if successful, None otherwise
    """
    try:
        collection = get_collection('verification_tokens')
        
        if expiry_seconds is None:
            expiry_seconds = VERIFICATION_TOKEN_EXPIRY
        
        created_at = datetime.now()
        expires_at = created_at + timedelta(seconds=expiry_seconds)
        
        token_doc = {
            'token_id': token_id,
            'user_id': user_id,
            'status': 'pending',  # pending, in_progress, completed, expired
            'created_at': created_at,
            'expires_at': expires_at,
            'completed_at': None,
            'updated_at': created_at
        }
        
        result = await collection.insert_one(token_doc)
        
        logger.info(f"Created verification token for user {user_id}")
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Error creating verification token: {e}", exc_info=True)
        return None


async def get_verification_token(token_id: str) -> Optional[Dict[str, Any]]:
    """
    Get verification token by token ID.
    
    Args:
        token_id: Token ID
    
    Returns:
        Token document or None
    """
    try:
        collection = get_collection('verification_tokens')
        
        token = await collection.find_one({'token_id': token_id})
        
        if token:
            token['_id'] = str(token['_id'])
        
        return token
    
    except Exception as e:
        logger.error(f"Error getting verification token: {e}", exc_info=True)
        return None


async def get_token_by_user(user_id: int, status: str = 'pending') -> Optional[Dict[str, Any]]:
    """
    Get verification token by user ID.
    
    Args:
        user_id: User's Telegram ID
        status: Token status to filter by
    
    Returns:
        Token document or None
    """
    try:
        collection = get_collection('verification_tokens')
        
        token = await collection.find_one({
            'user_id': user_id,
            'status': status
        })
        
        if token:
            token['_id'] = str(token['_id'])
        
        return token
    
    except Exception as e:
        logger.error(f"Error getting token by user: {e}", exc_info=True)
        return None


async def update_token_status(
    token_id: str,
    status: str,
    completed_at: Optional[datetime] = None
) -> bool:
    """
    Update token status.
    
    Args:
        token_id: Token ID
        status: New status (pending, in_progress, completed, expired)
        completed_at: Completion timestamp (optional)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('verification_tokens')
        
        update_doc = {
            'status': status,
            'updated_at': datetime.now()
        }
        
        if completed_at:
            update_doc['completed_at'] = completed_at
        elif status == 'completed':
            update_doc['completed_at'] = datetime.now()
        
        result = await collection.update_one(
            {'token_id': token_id},
            {'$set': update_doc}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated token {token_id} status to {status}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error updating token status: {e}", exc_info=True)
        return False


async def mark_token_in_progress(token_id: str) -> bool:
    """
    Mark token as in progress (user reached verification page).
    
    Args:
        token_id: Token ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        return await update_token_status(token_id, 'in_progress')
    
    except Exception as e:
        logger.error(f"Error marking token in progress: {e}", exc_info=True)
        return False


async def mark_token_completed(token_id: str) -> bool:
    """
    Mark token as completed (verification successful).
    
    Args:
        token_id: Token ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        return await update_token_status(token_id, 'completed', datetime.now())
    
    except Exception as e:
        logger.error(f"Error marking token completed: {e}", exc_info=True)
        return False


async def mark_token_expired(token_id: str) -> bool:
    """
    Mark token as expired.
    
    Args:
        token_id: Token ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        return await update_token_status(token_id, 'expired')
    
    except Exception as e:
        logger.error(f"Error marking token expired: {e}", exc_info=True)
        return False


async def delete_verification_token(token_id: str) -> bool:
    """
    Delete a verification token.
    
    Args:
        token_id: Token ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('verification_tokens')
        
        result = await collection.delete_one({'token_id': token_id})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted token: {token_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error deleting token: {e}", exc_info=True)
        return False


async def is_token_valid(token_id: str) -> bool:
    """
    Check if token is valid (exists, not expired, correct status).
    
    Args:
        token_id: Token ID
    
    Returns:
        True if valid, False otherwise
    """
    try:
        token = await get_verification_token(token_id)
        
        if not token:
            return False
        
        # Check expiry
        if token['expires_at'] < datetime.now():
            return False
        
        # Check status
        if token['status'] not in ['pending', 'in_progress']:
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Error checking token validity: {e}", exc_info=True)
        return False


async def is_token_expired(token_id: str) -> bool:
    """
    Check if token is expired.
    
    Args:
        token_id: Token ID
    
    Returns:
        True if expired, False otherwise
    """
    try:
        token = await get_verification_token(token_id)
        
        if not token:
            return True
        
        return token['expires_at'] < datetime.now()
    
    except Exception as e:
        logger.error(f"Error checking token expiry: {e}", exc_info=True)
        return True


async def cleanup_expired_tokens(hours: int = 24) -> int:
    """
    Delete expired tokens older than specified hours.
    
    Args:
        hours: Hours to keep expired tokens
    
    Returns:
        Number of tokens deleted
    """
    try:
        collection = get_collection('verification_tokens')
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        result = await collection.delete_many({
            'expires_at': {'$lt': cutoff_time}
        })
        
        if result.deleted_count > 0:
            logger.info(f"Cleaned up {result.deleted_count} expired tokens")
        
        return result.deleted_count
    
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}", exc_info=True)
        return 0


async def get_pending_tokens() -> List[Dict[str, Any]]:
    """
    Get all pending tokens.
    
    Returns:
        List of pending token documents
    """
    try:
        collection = get_collection('verification_tokens')
        
        tokens = await collection.find({'status': 'pending'}).to_list(length=None)
        
        for token in tokens:
            token['_id'] = str(token['_id'])
        
        return tokens
    
    except Exception as e:
        logger.error(f"Error getting pending tokens: {e}", exc_info=True)
        return []


async def get_tokens_by_status(status: str) -> List[Dict[str, Any]]:
    """
    Get tokens by status.
    
    Args:
        status: Token status to filter by
    
    Returns:
        List of token documents
    """
    try:
        collection = get_collection('verification_tokens')
        
        tokens = await collection.find({'status': status}).to_list(length=None)
        
        for token in tokens:
            token['_id'] = str(token['_id'])
        
        return tokens
    
    except Exception as e:
        logger.error(f"Error getting tokens by status: {e}", exc_info=True)
        return []


async def get_user_token_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get token history for a user.
    
    Args:
        user_id: User's Telegram ID
        limit: Maximum number of tokens to return
    
    Returns:
        List of token documents
    """
    try:
        collection = get_collection('verification_tokens')
        
        tokens = await collection.find(
            {'user_id': user_id}
        ).sort('created_at', -1).limit(limit).to_list(length=None)
        
        for token in tokens:
            token['_id'] = str(token['_id'])
        
        return tokens
    
    except Exception as e:
        logger.error(f"Error getting user token history: {e}", exc_info=True)
        return []


async def get_verification_stats() -> Dict[str, Any]:
    """
    Get verification statistics.
    
    Returns:
        Dictionary with statistics
    """
    try:
        collection = get_collection('verification_tokens')
        
        total_tokens = await collection.count_documents({})
        pending = await collection.count_documents({'status': 'pending'})
        completed = await collection.count_documents({'status': 'completed'})
        expired = await collection.count_documents({'status': 'expired'})
        
        return {
            'total_tokens': total_tokens,
            'pending': pending,
            'completed': completed,
            'expired': expired,
            'in_progress': await collection.count_documents({'status': 'in_progress'})
        }
    
    except Exception as e:
        logger.error(f"Error getting verification stats: {e}", exc_info=True)
        return {}


async def has_user_pending_token(user_id: int) -> bool:
    """
    Check if user has pending verification token.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        True if user has pending token, False otherwise
    """
    try:
        collection = get_collection('verification_tokens')
        
        token = await collection.find_one({
            'user_id': user_id,
            'status': 'pending',
            'expires_at': {'$gt': datetime.now()}
        })
        
        return token is not None
    
    except Exception as e:
        logger.error(f"Error checking pending token: {e}", exc_info=True)
        return False


async def invalidate_user_tokens(user_id: int) -> int:
    """
    Invalidate all user tokens.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Number of tokens invalidated
    """
    try:
        collection = get_collection('verification_tokens')
        
        result = await collection.update_many(
            {'user_id': user_id, 'status': {'$in': ['pending', 'in_progress']}},
            {'$set': {'status': 'expired', 'updated_at': datetime.now()}}
        )
        
        return result.modified_count
    
    except Exception as e:
        logger.error(f"Error invalidating user tokens: {e}", exc_info=True)
        return 0


async def get_token_age_seconds(token_id: str) -> Optional[int]:
    """
    Get token age in seconds.
    
    Args:
        token_id: Token ID
    
    Returns:
        Age in seconds or None
    """
    try:
        token = await get_verification_token(token_id)
        
        if not token:
            return None
        
        age = datetime.now() - token['created_at']
        return int(age.total_seconds())
    
    except Exception as e:
        logger.error(f"Error getting token age: {e}", exc_info=True)
        return None


async def delete_user_tokens(user_id: int) -> int:
    """
    Delete all tokens for a user.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Number of tokens deleted
    """
    try:
        collection = get_collection('verification_tokens')
        
        result = await collection.delete_many({'user_id': user_id})
        
        logger.info(f"Deleted {result.deleted_count} tokens for user {user_id}")
        return result.deleted_count
    
    except Exception as e:
        logger.error(f"Error deleting user tokens: {e}", exc_info=True)
        return 0
