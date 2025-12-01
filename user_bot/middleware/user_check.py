"""
User Check Middleware for User Bot
Middleware functions for validating user state, subscriptions, and permissions.
"""

import logging
from datetime import datetime
from typing import Tuple, Optional
from telegram import Update, Bot
from telegram.error import TelegramError

from database.operations.users import (
    get_user_by_id,
    create_user,
    is_user_verified,
)
from database.operations.channels import get_active_channels

logger = logging.getLogger(__name__)


async def check_user_exists(user_id: int) -> Tuple[bool, Optional[dict]]:
    """
    Check if user exists in database.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        Tuple of (exists: bool, user_data: dict or None)
    """
    try:
        user = await get_user_by_id(user_id)
        return (True, user) if user else (False, None)
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")
        return False, None


async def ensure_user_record(update: Update) -> Optional[dict]:
    """
    Ensure user record exists in database, create if not.
    
    Args:
        update: Telegram update object
    
    Returns:
        User record dictionary or None if error
    """
    try:
        user = update.effective_user
        user_id = user.id
        username = user.username
        first_name = user.first_name
        
        # Check if user exists
        exists, user_record = await check_user_exists(user_id)
        
        if not exists:
            # Create new user record
            await create_user(
                user_id=user_id,
                username=username,
                first_name=first_name
            )
            logger.info(f"Created new user record: {user_id}")
            
            # Fetch the newly created record
            user_record = await get_user_by_id(user_id)
        
        return user_record
    
    except Exception as e:
        logger.error(f"Error ensuring user record: {e}")
        return None


async def check_force_subscribe(bot: Bot, user_id: int) -> Tuple[bool, list]:
    """
    Check if user is subscribed to all force subscribe channels.
    
    Args:
        bot: Telegram bot instance
        user_id: Telegram user ID
    
    Returns:
        Tuple of (is_subscribed_all: bool, unsubscribed_channels: list)
    """
    try:
        # Get all active channels
        channels = await get_active_channels()
        
        if not channels:
            # No force sub channels configured
            return True, []
        
        unsubscribed = []
        
        for channel in channels:
            channel_id = channel.get('channel_id')
            channel_username = channel.get('channel_username')
            
            # Try to get chat member
            try:
                if channel_id:
                    member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                else:
                    member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
                
                # Check if user is a member (not left or kicked)
                if member.status in ['left', 'kicked']:
                    unsubscribed.append(channel)
            
            except TelegramError as e:
                # User not in channel or bot not admin
                logger.warning(f"Could not check membership for {channel_username}: {e}")
                unsubscribed.append(channel)
        
        is_subscribed_all = len(unsubscribed) == 0
        
        return is_subscribed_all, unsubscribed
    
    except Exception as e:
        logger.error(f"Error checking force subscribe: {e}")
        return False, []


async def check_verification(user_id: int) -> Tuple[bool, Optional[str]]:
    """
    Check if user is currently verified and not expired.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        Tuple of (is_verified: bool, status_message: str or None)
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return False, "user_not_found"
        
        # Check if verified
        if not user.get('is_verified', False):
            return False, "not_verified"
        
        # Check expiry
        expires_at = user.get('expires_at')
        if not expires_at:
            return False, "no_expiry"
        
        now = datetime.now()
        
        if expires_at < now:
            return False, "expired"
        
        return True, "verified"
    
    except Exception as e:
        logger.error(f"Error checking verification: {e}")
        return False, "error"


async def check_file_access_limit(user_id: int, limit: int = 3) -> Tuple[bool, int]:
    """
    Check if user has reached file access limit.
    
    Args:
        user_id: Telegram user ID
        limit: File access limit (default: 3)
    
    Returns:
        Tuple of (can_access: bool, current_count: int)
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return False, 0
        
        current_count = user.get('files_accessed_count', 0)
        can_access = current_count < limit
        
        return can_access, current_count
    
    except Exception as e:
        logger.error(f"Error checking file access limit: {e}")
        return False, 0


async def validate_user_for_download(bot: Bot, user_id: int) -> Tuple[bool, str, Optional[list]]:
    """
    Comprehensive validation for file download.
    Checks force sub, verification, and file access limit.
    
    Args:
        bot: Telegram bot instance
        user_id: Telegram user ID
    
    Returns:
        Tuple of (can_download: bool, reason: str, channels: list or None)
        
    Reasons:
        - "success" - Can download
        - "force_sub_failed" - Not subscribed to all channels
        - "not_verified" - User not verified
        - "verification_expired" - Verification expired
        - "limit_reached" - File access limit reached
        - "error" - Error occurred
    """
    try:
        # Check 1: Force Subscribe
        is_subscribed, unsubscribed_channels = await check_force_subscribe(bot, user_id)
        
        if not is_subscribed:
            return False, "force_sub_failed", unsubscribed_channels
        
        # Check 2: Verification
        is_verified, status = await check_verification(user_id)
        
        if not is_verified:
            if status == "expired":
                return False, "verification_expired", None
            else:
                return False, "not_verified", None
        
        # Check 3: File Access Limit
        can_access, current_count = await check_file_access_limit(user_id)
        
        if not can_access:
            return False, "limit_reached", None
        
        # All checks passed
        return True, "success", None
    
    except Exception as e:
        logger.error(f"Error validating user for download: {e}")
        return False, "error", None


async def get_user_verification_status(user_id: int) -> dict:
    """
    Get detailed verification status for a user.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        Dictionary with verification details
    """
    try:
        user = await get_user_by_id(user_id)
        
        if not user:
            return {
                'exists': False,
                'is_verified': False,
                'expired': False,
                'files_accessed': 0,
                'files_remaining': 0,
                'expires_at': None,
                'time_remaining': None
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
                    'hours': int(time_diff.total_seconds() / 3600),
                    'minutes': int((time_diff.total_seconds() % 3600) / 60)
                }
        
        return {
            'exists': True,
            'is_verified': is_verified and not expired,
            'expired': expired,
            'files_accessed': files_accessed,
            'files_remaining': files_remaining,
            'expires_at': expires_at,
            'time_remaining': time_remaining
        }
    
    except Exception as e:
        logger.error(f"Error getting verification status: {e}")
        return {
            'exists': False,
            'is_verified': False,
            'expired': False,
            'files_accessed': 0,
            'files_remaining': 0,
            'expires_at': None,
            'time_remaining': None
        }


async def is_user_admin(bot: Bot, user_id: int, chat_id: int) -> bool:
    """
    Check if user is admin in a chat.
    
    Args:
        bot: Telegram bot instance
        user_id: Telegram user ID
        chat_id: Chat ID to check
    
    Returns:
        True if user is admin, False otherwise
    """
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ['creator', 'administrator']
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


async def refresh_user_activity(user_id: int) -> bool:
    """
    Update user's last access timestamp.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from database.operations.users import update_user
        
        return await update_user(user_id, {
            'last_access': datetime.now()
        })
    
    except Exception as e:
        logger.error(f"Error refreshing user activity: {e}")
        return False