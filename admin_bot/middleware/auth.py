"""
Authentication Middleware for Admin Bot
Provides admin-only access control and authorization checks.
"""

import os
from functools import wraps
from typing import List, Callable
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.settings import ADMIN_IDS


def get_admin_list() -> List[int]:
    """
    Get list of admin user IDs from environment variable.
    
    Returns:
        List of admin user IDs
    """
    if isinstance(ADMIN_IDS, list):
        return ADMIN_IDS
    
    if isinstance(ADMIN_IDS, str):
        # Parse comma-separated string
        try:
            return [int(uid.strip()) for uid in ADMIN_IDS.split(',') if uid.strip()]
        except ValueError:
            print("Error: Invalid ADMIN_IDS format in environment variables")
            return []
    
    return []


async def is_admin(user_id: int) -> bool:
    """
    Check if a user ID is in the admin list.
    
    Args:
        user_id: Telegram user ID to check
    
    Returns:
        True if user is admin, False otherwise
    """
    admin_list = get_admin_list()
    return user_id in admin_list


async def check_admin_access(user_id: int) -> tuple[bool, str]:
    """
    Check admin access and return status with message.
    
    Args:
        user_id: Telegram user ID to check
    
    Returns:
        Tuple of (is_allowed, message)
    """
    if await is_admin(user_id):
        return True, "Access granted"
    else:
        return False, "Access denied: You are not authorized to use this bot"


def admin_only(func: Callable) -> Callable:
    """
    Decorator to restrict handler access to admins only.
    
    Usage:
        @admin_only
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Handler code here
    
    Args:
        func: Handler function to wrap
    
    Returns:
        Wrapped handler function
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # Get user ID from update
        user_id = None
        
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        elif update.effective_user:
            user_id = update.effective_user.id
        
        if not user_id:
            # Could not determine user ID
            return
        
        # Check if user is admin
        if not await is_admin(user_id):
            # Send access denied message
            access_denied_message = (
                "⛔ *Access Denied*\n\n"
                "This bot is restricted to administrators only.\n\n"
                "If you believe this is an error, please contact the bot owner."
            )
            
            if update.message:
                await update.message.reply_text(
                    access_denied_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            elif update.callback_query:
                await update.callback_query.answer(
                    "⛔ Access Denied: Admin only",
                    show_alert=True
                )
            
            return
        
        # User is admin, execute handler
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def require_admin(user_id: int) -> bool:
    """
    Synchronous version of admin check.
    Useful for non-async contexts.
    
    Args:
        user_id: Telegram user ID to check
    
    Returns:
        True if user is admin, False otherwise
    """
    admin_list = get_admin_list()
    return user_id in admin_list


class AdminFilter:
    """
    Custom filter class for filtering admin users.
    Can be used with MessageHandler filters.
    
    Usage:
        from telegram.ext import MessageHandler
        admin_filter = AdminFilter()
        handler = MessageHandler(filters.TEXT & admin_filter, callback)
    """
    
    def __call__(self, update: Update) -> bool:
        """
        Filter function to check if user is admin.
        
        Args:
            update: Telegram update object
        
        Returns:
            True if user is admin, False otherwise
        """
        if update.effective_user:
            return require_admin(update.effective_user.id)
        return False


def get_admin_count() -> int:
    """
    Get total number of admins.
    
    Returns:
        Number of admin users
    """
    return len(get_admin_list())


def add_admin(user_id: int) -> bool:
    """
    Add a user to admin list (requires manual update in .env file).
    This is a helper function that returns instructions.
    
    Args:
        user_id: User ID to add
    
    Returns:
        False (requires manual configuration)
    """
    print(f"To add admin {user_id}, update ADMIN_IDS in .env file:")
    current_admins = get_admin_list()
    current_admins.append(user_id)
    print(f"ADMIN_IDS={','.join(map(str, current_admins))}")
    return False


def log_admin_access(user_id: int, username: str = None, action: str = None):
    """
    Log admin access for security auditing.
    
    Args:
        user_id: Admin user ID
        username: Admin username (optional)
        action: Action being performed (optional)
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] Admin Access - ID: {user_id}"
    
    if username:
        log_entry += f" | Username: @{username}"
    
    if action:
        log_entry += f" | Action: {action}"
    
    # Log to console (in production, should log to file or database)
    print(log_entry)


async def verify_admin_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Verify admin access and log the attempt.
    
    Args:
        update: Telegram update object
        context: Telegram context object
    
    Returns:
        True if admin, False otherwise
    """
    user = update.effective_user
    
    if not user:
        return False
    
    is_admin_user = await is_admin(user.id)
    
    # Log access attempt
    log_admin_access(
        user_id=user.id,
        username=user.username,
        action="access_attempt"
    )
    
    return is_admin_user