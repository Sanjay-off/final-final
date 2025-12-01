"""
Formatters for User Bot
Utility functions for formatting messages, captions, and user-facing text.
"""

import logging
from datetime import datetime
from typing import Optional

from shared.constants import (
    FORCE_SUB_TEMPLATE,
    VERIFICATION_TEMPLATE,
    VERIFIED_SUCCESS_TEMPLATE,
    BYPASS_DETECTED_TEMPLATE,
    ALREADY_VERIFIED_TEMPLATE,
    TOKEN_ERROR_TEMPLATE,
    LIMIT_REACHED_TEMPLATE,
    FILE_DELETED_TEMPLATE,
    AUTO_DELETE_WARNING
)

logger = logging.getLogger(__name__)


def format_force_sub_message(username: str) -> str:
    """
    Format force subscribe message.
    
    Args:
        username: User's first name or username
    
    Returns:
        Formatted force subscribe message
    """
    try:
        return FORCE_SUB_TEMPLATE.format(username=username)
    except Exception as e:
        logger.error(f"Error formatting force sub message: {e}")
        return (
            f"❝ » HEY, {username} ×~ ❞\n\n"
            "YOUR FILE IS READY ‼️ LOOKS LIKE YOU HAVEN'T SUBSCRIBED TO OUR CHANNELS YET,\n"
            "SUBSCRIBE NOW TO GET YOUR FILES."
        )


def format_verification_message(username: str) -> str:
    """
    Format verification required message.
    
    Args:
        username: User's first name or username
    
    Returns:
        Formatted verification message
    """
    try:
        return VERIFICATION_TEMPLATE.format(username=username)
    except Exception as e:
        logger.error(f"Error formatting verification message: {e}")
        return (
            f"⚡ HEY, {username} ×~\n\n"
            "» YOU NEED TO VERIFY A TOKEN TO GET FREE ACCESS FOR 1 DAY ✅\n\n"
            "» IF YOU DONT WANT TO OPEN SHORT LINKS THEN YOU CAN TAKE PREMIUM SERVICES"
        )


def format_file_caption(password: str) -> str:
    """
    Format file caption with password.
    
    Args:
        password: File password
    
    Returns:
        Formatted caption
    """
    return f"password - {password}"


def format_limit_reached_message(limit: int = 3) -> str:
    """
    Format file limit reached message.
    
    Args:
        limit: File access limit
    
    Returns:
        Formatted limit reached message
    """
    try:
        return LIMIT_REACHED_TEMPLATE.format(limit=limit)
    except Exception as e:
        logger.error(f"Error formatting limit reached message: {e}")
        return (
            f"⚠️ DAILY LIMIT REACHED\n\n"
            f"You have accessed your maximum of {limit} files for today. "
            f"To continue accessing files, please verify again.\n\n"
            f"Your verification period will reset, and you'll get {limit} new file access attempts.\n\n"
            "Click below to verify again. ⬇️"
        )


def format_verified_success_message() -> str:
    """
    Format verification success message.
    
    Returns:
        Formatted success message
    """
    return VERIFIED_SUCCESS_TEMPLATE


def format_bypass_detected_message() -> str:
    """
    Format bypass detected warning message.
    
    Returns:
        Formatted bypass warning message
    """
    return BYPASS_DETECTED_TEMPLATE


def format_already_verified_message() -> str:
    """
    Format already verified message.
    
    Returns:
        Formatted already verified message
    """
    return ALREADY_VERIFIED_TEMPLATE


def format_token_error_message() -> str:
    """
    Format token error message.
    
    Returns:
        Formatted token error message
    """
    return TOKEN_ERROR_TEMPLATE


def format_file_deleted_message() -> str:
    """
    Format file deleted notification message.
    
    Returns:
        Formatted file deleted message
    """
    return FILE_DELETED_TEMPLATE


def format_auto_delete_warning(minutes: int = 10) -> str:
    """
    Format auto-delete warning message.
    
    Args:
        minutes: Minutes until deletion
    
    Returns:
        Formatted warning message
    """
    try:
        return AUTO_DELETE_WARNING.format(minutes=minutes)
    except Exception as e:
        logger.error(f"Error formatting auto-delete warning: {e}")
        return (
            f"⚠️ TELEGRAM MF DONT LIKE IT SO....\n\n"
            f"YOUR FILES WILL BE DELETED WITHIN **{minutes} MINUTES**. "
            f"SO PLEASE FORWARD THEM TO ANY OTHER PLACE FOR FUTURE AVAILABILITY."
        )


def format_user_greeting(username: Optional[str], first_name: Optional[str] = None) -> str:
    """
    Format user greeting based on available info.
    
    Args:
        username: User's username
        first_name: User's first name
    
    Returns:
        Formatted greeting name
    """
    if first_name:
        return first_name
    elif username:
        return username
    else:
        return "User"


def format_verification_status(
    is_verified: bool,
    expires_at: Optional[datetime] = None,
    files_accessed: int = 0,
    files_limit: int = 3
) -> str:
    """
    Format verification status message.
    
    Args:
        is_verified: Whether user is verified
        expires_at: Verification expiry datetime
        files_accessed: Number of files accessed
        files_limit: File access limit
    
    Returns:
        Formatted status message
    """
    if not is_verified:
        return "❌ Not Verified\n\nYou need to verify to access files."
    
    if not expires_at:
        return "✅ Verified\n\nVerification status unknown."
    
    now = datetime.now()
    
    if expires_at < now:
        return "⏰ Verification Expired\n\nPlease verify again to access files."
    
    # Calculate time remaining
    time_diff = expires_at - now
    hours_left = int(time_diff.total_seconds() / 3600)
    minutes_left = int((time_diff.total_seconds() % 3600) / 60)
    
    time_str = f"{hours_left}h {minutes_left}m" if hours_left > 0 else f"{minutes_left}m"
    
    files_remaining = max(0, files_limit - files_accessed)
    
    status = (
        f"✅ Verified\n\n"
        f"Time Remaining: {time_str}\n"
        f"Files Accessed: {files_accessed}/{files_limit}\n"
        f"Files Remaining: {files_remaining}"
    )
    
    return status


def format_time_remaining(expires_at: datetime) -> str:
    """
    Format time remaining until expiry.
    
    Args:
        expires_at: Expiry datetime
    
    Returns:
        Formatted time string (e.g., "5h 30m", "45m")
    """
    if not expires_at:
        return "N/A"
    
    now = datetime.now()
    
    if expires_at < now:
        return "Expired"
    
    time_diff = expires_at - now
    total_seconds = int(time_diff.total_seconds())
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def format_welcome_message(username: str) -> str:
    """
    Format welcome message for new users.
    
    Args:
        username: User's name
    
    Returns:
        Formatted welcome message
    """
    return (
        f"👋 Welcome, {username}!\n\n"
        "This bot provides access to ZIP files.\n\n"
        "To download files:\n"
        "1. Subscribe to all required channels\n"
        "2. Complete verification (free for 24 hours)\n"
        "3. Access up to 3 files per verification period\n\n"
        "Click the download button on any post in our channel to get started!"
    )


def format_help_message() -> str:
    """
    Format help message.
    
    Returns:
        Formatted help message
    """
    return (
        "ℹ️ *Help & Information*\n\n"
        "*How to download files:*\n"
        "1. Click download button on any post\n"
        "2. Subscribe to all channels\n"
        "3. Complete verification\n"
        "4. Get your file\n\n"
        "*Verification:*\n"
        "• Free for 24 hours\n"
        "• Access up to 3 files\n"
        "• Quick and easy process\n\n"
        "*File Access:*\n"
        "• Files auto-delete after 10 minutes\n"
        "• Forward files to save them\n"
        "• Re-download available\n\n"
        "Need help? Contact support!"
    )


def format_error_message(error_type: str = "general") -> str:
    """
    Format error message based on error type.
    
    Args:
        error_type: Type of error
    
    Returns:
        Formatted error message
    """
    error_messages = {
        "general": "❌ An error occurred. Please try again later.",
        "file_not_found": "❌ File not found. The file may have been removed.",
        "not_subscribed": "❌ Please subscribe to all channels first.",
        "not_verified": "❌ Please complete verification first.",
        "limit_reached": "❌ You've reached your file access limit. Please verify again.",
        "expired": "❌ Your verification has expired. Please verify again.",
        "invalid_link": "❌ Invalid download link. Please use the link from our channel.",
        "server_error": "❌ Server error. Please try again in a few minutes.",
        "maintenance": "⚠️ Bot is under maintenance. Please try again later."
    }
    
    return error_messages.get(error_type, error_messages["general"])


def format_statistics_message(
    total_downloads: int,
    verified_users: int,
    total_files: int
) -> str:
    """
    Format statistics message (for admins or public stats).
    
    Args:
        total_downloads: Total number of downloads
        verified_users: Number of verified users
        total_files: Total number of files
    
    Returns:
        Formatted statistics message
    """
    return (
        "📊 *Bot Statistics*\n\n"
        f"📥 Total Downloads: {total_downloads:,}\n"
        f"✅ Verified Users: {verified_users:,}\n"
        f"📁 Total Files: {total_files:,}\n"
    )


def format_post_notification(post_no: int, context: str) -> str:
    """
    Format new post notification.
    
    Args:
        post_no: Post number
        context: Post context/title
    
    Returns:
        Formatted notification
    """
    return (
        f"🆕 *New File Available!*\n\n"
        f"Post #{post_no}\n"
        f"{context}\n\n"
        "Click the download button to get the file!"
    )


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted file size (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format timestamp for display.
    
    Args:
        dt: Datetime object (defaults to now)
    
    Returns:
        Formatted timestamp
    """
    if not dt:
        dt = datetime.now()
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram Markdown.
    
    Args:
        text: Text to escape
    
    Returns:
        Escaped text
    """
    if not text:
        return ""
    
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text