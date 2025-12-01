"""
Verification Utilities for User Bot
Handles user verification checking, status management, and verification flow.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import requests

from database.operations.users import (
    get_user_by_id,
    is_user_verified as db_is_user_verified,
    verify_user_manually,
    update_user_verification
)
from database.operations.verification import (
    create_verification_token,
    get_verification_token,
    has_user_pending_token,
    invalidate_user_tokens
)
from database.operations.settings import get_setting_value
from shared.utils import build_deep_link
from shared.encryption import encode_url_safe
from config.settings import (
    USER_BOT_USERNAME,
    VERIFICATION_TOKEN_EXPIRY,
    VERIFICATION_PERIOD_HOURS
)
from user_bot.utils.token import (
    generate_unique_token_id,
    validate_token
)

logger = logging.getLogger(__name__)


async def is_user_verified(user_id: int) -> bool:
    """
    Check if user is currently verified (not expired).
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        True if verified and not expired, False otherwise
    """
    try:
        return await db_is_user_verified(user_id)
    
    except Exception as e:
        logger.error(f"Error checking if user verified: {e}")
        return False


async def check_verification_status(user_id: int) -> Dict[str, Any]:
    """
    Get detailed verification status for a user.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Dictionary with verification status details
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return {
                'exists': False,
                'is_verified': False,
                'expired': False,
                'time_remaining': None,
                'files_accessed': 0,
                'files_remaining': 0
            }
        
        is_verified = user.get('is_verified', False)
        expires_at = user.get('expires_at')
        files_accessed = user.get('files_accessed_count', 0)
        files_remaining = max(0, 3 - files_accessed)
        
        expired = False
        time_remaining = None
        
        if is_verified and expires_at:
            now = datetime.now()
            expired = expires_at < now
            
            if not expired:
                time_diff = expires_at - now
                time_remaining = {
                    'total_seconds': int(time_diff.total_seconds()),
                    'hours': int(time_diff.total_seconds() / 3600),
                    'minutes': int((time_diff.total_seconds() % 3600) / 60)
                }
        
        return {
            'exists': True,
            'is_verified': is_verified and not expired,
            'expired': expired,
            'time_remaining': time_remaining,
            'expires_at': expires_at,
            'verified_at': user.get('verified_at'),
            'files_accessed': files_accessed,
            'files_remaining': files_remaining
        }
    
    except Exception as e:
        logger.error(f"Error checking verification status: {e}")
        return {
            'exists': False,
            'is_verified': False,
            'expired': False,
            'time_remaining': None,
            'files_accessed': 0,
            'files_remaining': 0,
            'error': str(e)
        }


async def generate_verification_link(user_id: int) -> Optional[str]:
    """
    Generate verification shortlink for user.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Shortlink URL or None if error
    """
    try:
        # Check if user already has pending token
        has_pending = await has_user_pending_token(user_id)
        
        if has_pending:
            # Invalidate old tokens
            await invalidate_user_tokens(user_id)
        
        # Generate new token
        token_id = generate_unique_token_id(user_id)
        
        # Store token in database
        result = await create_verification_token(
            token_id=token_id,
            user_id=user_id,
            expiry_seconds=VERIFICATION_TOKEN_EXPIRY
        )
        
        if not result:
            logger.error(f"Failed to create verification token for user {user_id}")
            return None
        
        # Get shortlink API credentials from settings
        shortlink_api = await get_setting_value('shortlink_api_key')
        shortlink_base = await get_setting_value('shortlink_base_url')
        
        if not shortlink_api or not shortlink_base:
            logger.error("Shortlink API not configured")
            return None
        
        # Generate destination URL (verification server)
        verification_server_url = await get_setting_value('verification_server_url')
        
        if not verification_server_url:
            from config.settings import VERIFICATION_SERVER_URL
            verification_server_url = VERIFICATION_SERVER_URL
        
        # Encode token for URL
        encoded_token = encode_url_safe(token_id)
        destination_url = f"{verification_server_url}/verify?token={encoded_token}"
        
        # Generate shortlink
        shortlink = await create_shortlink(
            destination_url=destination_url,
            api_key=shortlink_api,
            base_url=shortlink_base
        )
        
        if shortlink:
            logger.info(f"Generated verification link for user {user_id}")
            return shortlink
        
        return None
    
    except Exception as e:
        logger.error(f"Error generating verification link: {e}", exc_info=True)
        return None


async def create_shortlink(
    destination_url: str,
    api_key: str,
    base_url: str
) -> Optional[str]:
    """
    Create shortlink using shortlink API.
    Supports just2earn.com and get2short.com APIs.
    
    Args:
        destination_url: Final destination URL
        api_key: Shortlink API key
        base_url: Shortlink base URL
    
    Returns:
        Shortlink URL or None if error
    """
    try:
        # Determine API format based on base_url
        if 'just2earn.com' in base_url:
            # Just2Earn API format: https://just2earn.com/api?api=api_token&url=yourdestinationlink.com
            api_endpoint = f"{base_url}/api"
            params = {
                'api': api_key,
                'url': destination_url
            }
            
            # Make GET request to Just2Earn API
            response = requests.get(
                api_endpoint,
                params=params,
                timeout=10
            )
            
        elif 'get2short.com' in base_url:
            # Get2Short API format: https://get2short.com/api?api=api_token&url=yourdestinationlink.com
            api_endpoint = f"{base_url}/api"
            params = {
                'api': api_key,
                'url': destination_url
            }
            
            # Make GET request to Get2Short API
            response = requests.get(
                api_endpoint,
                params=params,
                timeout=10
            )
        else:
            # Fallback to generic API format (POST with JSON)
            api_endpoint = f"{base_url}/api/shorten"
            payload = {
                'url': destination_url,
                'api_key': api_key
            }
            
            # Make POST request
            response = requests.post(
                api_endpoint,
                json=payload,
                timeout=10
            )
        
        if response.status_code == 200:
            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError:
                # If not JSON, try to extract URL from text response
                if response.text.startswith('http'):
                    logger.info(f"Created shortlink (text response): {response.text}")
                    return response.text
                logger.error(f"Invalid response format: {response.text}")
                return None
            
            # Handle different response formats
            shortlink = None
            
            # Check for common response field names
            for field in ['short_url', 'shorturl', 'short', 'link', 'url']:
                if field in data:
                    shortlink = data[field]
                    break
            
            # If still no shortlink, check if the response itself is the shortlink
            if not shortlink and isinstance(data, str) and data.startswith('http'):
                shortlink = data
            
            if shortlink and shortlink.startswith('http'):
                logger.info(f"Created shortlink: {shortlink}")
                return shortlink
            else:
                logger.error(f"No valid shortlink in response: {data}")
                return None
        
        logger.error(f"Shortlink API error: {response.status_code}, {response.text}")
        return None
    
    except requests.Timeout:
        logger.error("Shortlink API request timeout")
        return None
    
    except Exception as e:
        logger.error(f"Error creating shortlink: {e}")
        return None


async def verify_user(user_id: int, token_id: str) -> Tuple[bool, str]:
    """
    Verify user after successful token validation.
    
    Args:
        user_id: User's Telegram ID
        token_id: Token ID that was validated
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Validate token one more time
        is_valid, reason = await validate_token(token_id, user_id)
        
        if not is_valid:
            logger.warning(f"Token validation failed for user {user_id}: {reason}")
            return False, reason
        
        # Get verification period from settings
        verification_hours = await get_setting_value(
            'verification_period_hours',
            default=str(VERIFICATION_PERIOD_HOURS)
        )
        
        try:
            verification_hours = int(verification_hours)
        except:
            verification_hours = VERIFICATION_PERIOD_HOURS
        
        # Verify user
        result = await verify_user_manually(
            user_id=user_id,
            hours=verification_hours,
            verified_by=0  # 0 indicates automatic verification
        )
        
        if result:
            logger.info(f"User {user_id} verified successfully for {verification_hours} hours")
            return True, "verified"
        
        logger.error(f"Failed to verify user {user_id}")
        return False, "verification_failed"
    
    except Exception as e:
        logger.error(f"Error verifying user: {e}", exc_info=True)
        return False, "error"


async def extend_verification(user_id: int, additional_hours: int) -> bool:
    """
    Extend user's verification period.
    
    Args:
        user_id: User's Telegram ID
        additional_hours: Hours to add
    
    Returns:
        True if successful, False otherwise
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return False
        
        current_expires_at = user.get('expires_at')
        
        if not current_expires_at:
            return False
        
        # Calculate new expiry
        new_expires_at = current_expires_at + timedelta(hours=additional_hours)
        
        # Update verification
        result = await update_user_verification(
            user_id=user_id,
            expires_at=new_expires_at
        )
        
        if result:
            logger.info(f"Extended verification for user {user_id} by {additional_hours} hours")
        
        return result
    
    except Exception as e:
        logger.error(f"Error extending verification: {e}")
        return False


async def get_verification_time_remaining(user_id: int) -> Optional[Dict[str, int]]:
    """
    Get time remaining in verification period.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Dictionary with time remaining or None
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return None
        
        if not user.get('is_verified', False):
            return None
        
        expires_at = user.get('expires_at')
        
        if not expires_at:
            return None
        
        now = datetime.now()
        
        if expires_at < now:
            return {
                'expired': True,
                'total_seconds': 0,
                'hours': 0,
                'minutes': 0
            }
        
        time_diff = expires_at - now
        total_seconds = int(time_diff.total_seconds())
        
        return {
            'expired': False,
            'total_seconds': total_seconds,
            'hours': total_seconds // 3600,
            'minutes': (total_seconds % 3600) // 60
        }
    
    except Exception as e:
        logger.error(f"Error getting verification time remaining: {e}")
        return None


async def can_verify_again(user_id: int) -> Tuple[bool, str]:
    """
    Check if user can verify again.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Tuple of (can_verify: bool, reason: str)
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return True, "new_user"
        
        is_verified = user.get('is_verified', False)
        expires_at = user.get('expires_at')
        
        if not is_verified:
            return True, "not_verified"
        
        if not expires_at:
            return True, "no_expiry"
        
        now = datetime.now()
        
        if expires_at < now:
            return True, "expired"
        
        # User is currently verified
        return False, "already_verified"
    
    except Exception as e:
        logger.error(f"Error checking if can verify again: {e}")
        return False, "error"


async def get_verification_history(user_id: int) -> Dict[str, Any]:
    """
    Get verification history for a user.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Dictionary with verification history
    """
    try:
        from database.operations.verification import get_user_token_history
        
        user = await get_user_by_id(user_id)
        token_history = await get_user_token_history(user_id, limit=10)
        
        total_verifications = len([t for t in token_history if t['status'] == 'completed'])
        
        return {
            'user_id': user_id,
            'is_verified': user.get('is_verified', False) if user else False,
            'current_expires_at': user.get('expires_at') if user else None,
            'last_verified_at': user.get('verified_at') if user else None,
            'total_verifications': total_verifications,
            'recent_tokens': token_history[:5],
            'files_accessed': user.get('files_accessed_count', 0) if user else 0
        }
    
    except Exception as e:
        logger.error(f"Error getting verification history: {e}")
        return {
            'user_id': user_id,
            'error': str(e)
        }


async def reset_verification(user_id: int) -> bool:
    """
    Reset user's verification (for re-verification).
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from database.operations.users import unverify_user, reset_user_file_limit
        
        # Unverify user
        unverify_result = await unverify_user(user_id)
        
        # Reset file limit
        reset_result = await reset_user_file_limit(user_id)
        
        # Invalidate any pending tokens
        await invalidate_user_tokens(user_id)
        
        if unverify_result and reset_result:
            logger.info(f"Reset verification for user {user_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error resetting verification: {e}")
        return False


async def check_verification_eligibility(user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Check if user is eligible to receive files (comprehensive check).
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Tuple of (is_eligible: bool, reason: str, details: dict)
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return False, "user_not_found", None
        
        # Check verified status
        is_verified = user.get('is_verified', False)
        
        if not is_verified:
            return False, "not_verified", None
        
        # Check expiry
        expires_at = user.get('expires_at')
        
        if not expires_at:
            return False, "no_expiry", None
        
        now = datetime.now()
        
        if expires_at < now:
            return False, "expired", {
                'expired_at': expires_at
            }
        
        # Check file access limit
        files_accessed = user.get('files_accessed_count', 0)
        
        if files_accessed >= 3:
            return False, "limit_reached", {
                'files_accessed': files_accessed,
                'limit': 3
            }
        
        # All checks passed
        time_diff = expires_at - now
        
        return True, "eligible", {
            'files_accessed': files_accessed,
            'files_remaining': 3 - files_accessed,
            'time_remaining': {
                'hours': int(time_diff.total_seconds() / 3600),
                'minutes': int((time_diff.total_seconds() % 3600) / 60)
            }
        }
    
    except Exception as e:
        logger.error(f"Error checking verification eligibility: {e}")
        return False, "error", {'error': str(e)}


async def get_user_verification_stats(user_id: int) -> Dict[str, Any]:
    """
    Get comprehensive verification statistics for a user.
    
    Args:
        user_id: User's Telegram ID
    
    Returns:
        Dictionary with verification statistics
    """
    try:
        status = await check_verification_status(user_id)
        history = await get_verification_history(user_id)
        time_remaining = await get_verification_time_remaining(user_id)
        
        return {
            'user_id': user_id,
            'current_status': status,
            'history': history,
            'time_remaining': time_remaining,
            'timestamp': datetime.now()
        }
    
    except Exception as e:
        logger.error(f"Error getting verification stats: {e}")
        return {
            'user_id': user_id,
            'error': str(e)
        }