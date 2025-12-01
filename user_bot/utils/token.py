"""
Token Utilities for User Bot
Handles token generation, encryption, decryption, and validation for verification.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from shared.encryption import (
    encrypt_data,
    decrypt_data,
    generate_token as generate_random_token,
    encode_url_safe,
    decode_url_safe
)
from database.operations.verification import (
    create_verification_token,
    get_verification_token,
    is_token_valid,
    mark_token_in_progress,
    mark_token_completed,
    update_token_status
)
from config.settings import VERIFICATION_TOKEN_EXPIRY

logger = logging.getLogger(__name__)


def generate_token(user_id: int, length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        user_id: User's Telegram ID
        length: Token length
    
    Returns:
        Generated token string
    """
    try:
        # Generate random token
        token = generate_random_token(length)
        
        # Add timestamp and user_id for additional validation
        timestamp = int(datetime.now().timestamp())
        token_data = f"{token}_{user_id}_{timestamp}"
        
        return token_data
    
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return secrets.token_urlsafe(length)


def encrypt_token(token_data: str) -> Optional[str]:
    """
    Encrypt token data.
    
    Args:
        token_data: Token data to encrypt
    
    Returns:
        Encrypted token or None if error
    """
    try:
        encrypted = encrypt_data(token_data)
        return encrypted
    
    except Exception as e:
        logger.error(f"Error encrypting token: {e}")
        return None


def decrypt_token(encrypted_token: str) -> Optional[str]:
    """
    Decrypt token data.
    
    Args:
        encrypted_token: Encrypted token string
    
    Returns:
        Decrypted token data or None if error
    """
    try:
        decrypted = decrypt_data(encrypted_token)
        return decrypted
    
    except Exception as e:
        logger.error(f"Error decrypting token: {e}")
        return None


async def create_user_verification_token(user_id: int) -> Optional[str]:
    """
    Create a verification token for a user and store in database.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Token ID if successful, None otherwise
    """
    try:
        # Generate token
        token_id = generate_token(user_id)
        
        # Store in database
        result = await create_verification_token(
            token_id=token_id,
            user_id=user_id,
            expiry_seconds=VERIFICATION_TOKEN_EXPIRY
        )
        
        if result:
            logger.info(f"Created verification token for user {user_id}")
            return token_id
        
        return None
    
    except Exception as e:
        logger.error(f"Error creating user verification token: {e}")
        return None


async def validate_token(token_id: str, user_id: int) -> Tuple[bool, str]:
    """
    Validate verification token with comprehensive checks.
    
    Args:
        token_id: Token ID to validate
        user_id: User's Telegram ID
    
    Returns:
        Tuple of (is_valid: bool, reason: str)
    """
    try:
        # Check 1: Token exists in database
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            logger.warning(f"Token not found: {token_id}")
            return False, "token_not_found"
        
        # Check 2: Token belongs to this user
        if token_record['user_id'] != user_id:
            logger.warning(f"Token user mismatch: {token_id}")
            return False, "token_mismatch"
        
        # Check 3: Token not expired
        if token_record['expires_at'] < datetime.now():
            logger.warning(f"Token expired: {token_id}")
            return False, "token_expired"
        
        # Check 4: Token not already used
        if token_record['status'] == 'completed':
            logger.warning(f"Token already used: {token_id}")
            return False, "token_reused"
        
        # Check 5: Token must be in 'in_progress' state (set by verification server)
        if token_record['status'] != 'in_progress':
            logger.warning(f"Token not in progress: {token_id}, status: {token_record['status']}")
            return False, "invalid_state"
        
        # Check 6: Time elapsed check (bypass detection)
        time_elapsed = (datetime.now() - token_record['created_at']).total_seconds()
        
        if time_elapsed < 5:  # Too fast, likely bypass
            logger.warning(f"Token verification too fast: {token_id}, elapsed: {time_elapsed}s")
            return False, "too_fast"
        
        # All checks passed
        logger.info(f"Token validated successfully: {token_id}")
        return True, "valid"
    
    except Exception as e:
        logger.error(f"Error validating token: {e}", exc_info=True)
        return False, "error"


async def mark_token_as_in_progress(token_id: str) -> bool:
    """
    Mark token as in progress (verification page loaded).
    
    Args:
        token_id: Token ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        result = await mark_token_in_progress(token_id)
        
        if result:
            logger.info(f"Marked token as in progress: {token_id}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error marking token in progress: {e}")
        return False


async def mark_token_as_completed(token_id: str) -> bool:
    """
    Mark token as completed (verification successful).
    
    Args:
        token_id: Token ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        result = await mark_token_completed(token_id)
        
        if result:
            logger.info(f"Marked token as completed: {token_id}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error marking token completed: {e}")
        return False


async def invalidate_token(token_id: str) -> bool:
    """
    Invalidate/expire a token.
    
    Args:
        token_id: Token ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        result = await update_token_status(token_id, 'expired')
        
        if result:
            logger.info(f"Invalidated token: {token_id}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error invalidating token: {e}")
        return False


def encode_token_for_url(token_id: str) -> str:
    """
    Encode token for URL (base64 URL-safe).
    
    Args:
        token_id: Token ID
    
    Returns:
        URL-safe encoded token
    """
    try:
        return encode_url_safe(token_id)
    
    except Exception as e:
        logger.error(f"Error encoding token for URL: {e}")
        return token_id


def decode_token_from_url(encoded_token: str) -> Optional[str]:
    """
    Decode token from URL (base64 URL-safe).
    
    Args:
        encoded_token: URL-safe encoded token
    
    Returns:
        Decoded token ID or None if error
    """
    try:
        return decode_url_safe(encoded_token)
    
    except Exception as e:
        logger.error(f"Error decoding token from URL: {e}")
        return None


async def get_token_info(token_id: str) -> Optional[Dict[str, Any]]:
    """
    Get token information from database.
    
    Args:
        token_id: Token ID
    
    Returns:
        Token information dictionary or None
    """
    try:
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return None
        
        # Calculate time remaining
        time_remaining = None
        if token_record['expires_at'] > datetime.now():
            time_diff = token_record['expires_at'] - datetime.now()
            time_remaining = int(time_diff.total_seconds())
        
        return {
            'token_id': token_record['token_id'],
            'user_id': token_record['user_id'],
            'status': token_record['status'],
            'created_at': token_record['created_at'],
            'expires_at': token_record['expires_at'],
            'time_remaining': time_remaining,
            'is_expired': token_record['expires_at'] < datetime.now()
        }
    
    except Exception as e:
        logger.error(f"Error getting token info: {e}")
        return None


async def check_token_status(token_id: str) -> str:
    """
    Check current status of a token.
    
    Args:
        token_id: Token ID
    
    Returns:
        Token status: 'pending', 'in_progress', 'completed', 'expired', 'not_found', 'error'
    """
    try:
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return "not_found"
        
        # Check if expired
        if token_record['expires_at'] < datetime.now():
            return "expired"
        
        return token_record['status']
    
    except Exception as e:
        logger.error(f"Error checking token status: {e}")
        return "error"


def parse_token_data(token_data: str) -> Optional[Dict[str, Any]]:
    """
    Parse token data to extract components.
    
    Args:
        token_data: Token data string (format: token_userid_timestamp)
    
    Returns:
        Dictionary with parsed data or None
    """
    try:
        parts = token_data.split('_')
        
        if len(parts) < 3:
            return None
        
        return {
            'token': parts[0],
            'user_id': int(parts[1]),
            'timestamp': int(parts[2])
        }
    
    except Exception as e:
        logger.error(f"Error parsing token data: {e}")
        return None


async def is_token_expired(token_id: str) -> bool:
    """
    Check if token is expired.
    
    Args:
        token_id: Token ID
    
    Returns:
        True if expired, False otherwise
    """
    try:
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return True
        
        return token_record['expires_at'] < datetime.now()
    
    except Exception as e:
        logger.error(f"Error checking if token expired: {e}")
        return True


async def get_token_age_seconds(token_id: str) -> Optional[int]:
    """
    Get token age in seconds.
    
    Args:
        token_id: Token ID
    
    Returns:
        Age in seconds or None
    """
    try:
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return None
        
        age = datetime.now() - token_record['created_at']
        return int(age.total_seconds())
    
    except Exception as e:
        logger.error(f"Error getting token age: {e}")
        return None


def generate_unique_token_id(user_id: int) -> str:
    """
    Generate unique token ID with user context.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Unique token ID
    """
    timestamp = int(datetime.now().timestamp() * 1000)  # Milliseconds for uniqueness
    random_part = secrets.token_hex(16)
    
    return f"{random_part}_{user_id}_{timestamp}"


async def cleanup_user_tokens(user_id: int) -> int:
    """
    Cleanup expired tokens for a user.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Number of tokens cleaned up
    """
    try:
        from database.operations.verification import delete_user_tokens
        
        # For now, just log - actual implementation would delete expired tokens
        logger.info(f"Cleanup requested for user {user_id} tokens")
        
        # This would be implemented in database operations
        # return await delete_user_tokens(user_id)
        return 0
    
    except Exception as e:
        logger.error(f"Error cleaning up user tokens: {e}")
        return 0