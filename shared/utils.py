"""
Shared Utility Functions
Common utility functions used by both admin and user bots.
"""

import re
import string
import secrets
from datetime import datetime, timedelta
from typing import Optional, Union


# ============================================================================
# STRING UTILITIES
# ============================================================================

def clean_text(text: str) -> str:
    """
    Clean and sanitize text input.
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    return text


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
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


def generate_random_string(length: int = 16, include_special: bool = False) -> str:
    """
    Generate random string.
    
    Args:
        length: Length of string
        include_special: Include special characters
    
    Returns:
        Random string
    """
    if include_special:
        chars = string.ascii_letters + string.digits + string.punctuation
    else:
        chars = string.ascii_letters + string.digits
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def slugify(text: str) -> str:
    """
    Convert text to slug (URL-friendly).
    
    Args:
        text: Text to slugify
    
    Returns:
        Slugified text
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def capitalize_words(text: str) -> str:
    """
    Capitalize first letter of each word.
    
    Args:
        text: Text to capitalize
    
    Returns:
        Capitalized text
    """
    return ' '.join(word.capitalize() for word in text.split())


# ============================================================================
# TIME UTILITIES
# ============================================================================

def get_current_time() -> datetime:
    """
    Get current datetime.
    
    Returns:
        Current datetime
    """
    return datetime.now()


def format_time_remaining(expires_at: datetime) -> str:
    """
    Format time remaining until expiry.
    
    Args:
        expires_at: Expiry datetime
    
    Returns:
        Formatted time string (e.g., "2h 30m", "1d 5h")
    """
    if not expires_at:
        return "N/A"
    
    now = datetime.now()
    
    if expires_at < now:
        return "Expired"
    
    delta = expires_at - now
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes}m"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        if hours > 0:
            return f"{days}d {hours}h"
        return f"{days}d"


def calculate_expiry(hours: int, from_time: Optional[datetime] = None) -> datetime:
    """
    Calculate expiry datetime from hours.
    
    Args:
        hours: Hours until expiry
        from_time: Starting time (defaults to now)
    
    Returns:
        Expiry datetime
    """
    if from_time is None:
        from_time = datetime.now()
    
    return from_time + timedelta(hours=hours)


def is_expired(expires_at: Optional[datetime]) -> bool:
    """
    Check if datetime has expired.
    
    Args:
        expires_at: Expiry datetime
    
    Returns:
        True if expired, False otherwise
    """
    if not expires_at:
        return True
    
    return datetime.now() > expires_at


def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime to format
        format_string: Format string
    
    Returns:
        Formatted datetime string
    """
    if not dt:
        return "N/A"
    
    if isinstance(dt, str):
        return dt
    
    try:
        return dt.strftime(format_string)
    except:
        return str(dt)


def parse_time_string(time_str: str) -> Optional[int]:
    """
    Parse time string to hours (e.g., "24h", "2d", "1w").
    
    Args:
        time_str: Time string
    
    Returns:
        Hours as integer, or None if invalid
    """
    time_str = time_str.lower().strip()
    
    try:
        if time_str.endswith('h'):
            return int(time_str[:-1])
        elif time_str.endswith('d'):
            return int(time_str[:-1]) * 24
        elif time_str.endswith('w'):
            return int(time_str[:-1]) * 24 * 7
        else:
            # Assume hours if no unit
            return int(time_str)
    except ValueError:
        return None


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def is_valid_telegram_id(user_id: Union[int, str]) -> bool:
    """
    Validate Telegram user ID.
    
    Args:
        user_id: User ID to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        uid = int(user_id)
        return 0 < uid <= 9999999999
    except (ValueError, TypeError):
        return False


def is_valid_channel_id(channel_id: Union[int, str]) -> bool:
    """
    Validate Telegram channel/group ID.
    
    Args:
        channel_id: Channel ID to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        cid = int(channel_id)
        # Channels and groups have negative IDs starting with -100
        return str(cid).startswith('-100') and len(str(cid)) >= 13
    except (ValueError, TypeError):
        return False


def is_valid_username(username: str) -> bool:
    """
    Validate Telegram username.
    
    Args:
        username: Username to validate (with or without @)
    
    Returns:
        True if valid, False otherwise
    """
    if not username:
        return False
    
    # Remove @ if present
    if username.startswith('@'):
        username = username[1:]
    
    # Telegram username rules: 5-32 chars, alphanumeric and underscore
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    
    if not re.match(pattern, username):
        return False
    
    # Cannot start with number
    if username[0].isdigit():
        return False
    
    return True


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False
    
    # Simple URL pattern
    pattern = r'^https?://[\w\-.]+(:\d+)?(/.*)?$'
    return bool(re.match(pattern, url))


# ============================================================================
# FORMATTING UTILITIES
# ============================================================================

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
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


def format_number_with_commas(number: Union[int, float], decimals: int = 0) -> str:
    """
    Format number with thousand separators.
    
    Args:
        number: Number to format
        decimals: Number of decimal places
    
    Returns:
        Formatted number string
    """
    if decimals > 0:
        return f"{number:,.{decimals}f}"
    else:
        return f"{int(number):,}"


def format_percentage(value: float, total: float, decimals: int = 1) -> str:
    """
    Calculate and format percentage.
    
    Args:
        value: Value
        total: Total value
        decimals: Decimal places
    
    Returns:
        Formatted percentage string
    """
    if total == 0:
        return "0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.{decimals}f}%"


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        if hours > 0:
            return f"{days}d {hours}h"
        return f"{days}d"


# ============================================================================
# LIST UTILITIES
# ============================================================================

def chunk_list(items: list, chunk_size: int) -> list:
    """
    Split list into chunks.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def deduplicate_list(items: list) -> list:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        items: List with potential duplicates
    
    Returns:
        List without duplicates
    """
    seen = set()
    result = []
    
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result


# ============================================================================
# TELEGRAM UTILITIES
# ============================================================================

def extract_command_args(text: str) -> tuple:
    """
    Extract command and arguments from message text.
    
    Args:
        text: Message text
    
    Returns:
        Tuple of (command, args_list)
    """
    parts = text.split()
    
    if not parts:
        return "", []
    
    command = parts[0].lstrip('/')
    args = parts[1:] if len(parts) > 1 else []
    
    return command, args


def escape_markdown_v2(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    
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


def build_deep_link(bot_username: str, start_parameter: str) -> str:
    """
    Build Telegram deep link.
    
    Args:
        bot_username: Bot username (without @)
        start_parameter: Start parameter
    
    Returns:
        Deep link URL
    """
    return f"https://t.me/{bot_username}?start={start_parameter}"


# ============================================================================
# MISCELLANEOUS
# ============================================================================

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
    
    Returns:
        Result or default
    """
    if denominator == 0:
        return default
    
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max.
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
    
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def get_plural(count: int, singular: str, plural: str) -> str:
    """
    Get singular or plural form based on count.
    
    Args:
        count: Number of items
        singular: Singular form
        plural: Plural form
    
    Returns:
        Appropriate form
    """
    return singular if count == 1 else plural


__all__ = [
    # String utilities
    'clean_text',
    'truncate_string',
    'generate_random_string',
    'slugify',
    'capitalize_words',
    
    # Time utilities
    'get_current_time',
    'format_time_remaining',
    'calculate_expiry',
    'is_expired',
    'format_datetime',
    'parse_time_string',
    
    # Validation
    'is_valid_telegram_id',
    'is_valid_channel_id',
    'is_valid_username',
    'is_valid_url',
    
    # Formatting
    'format_file_size',
    'format_number_with_commas',
    'format_percentage',
    'format_duration',
    
    # List utilities
    'chunk_list',
    'deduplicate_list',
    
    # Telegram utilities
    'extract_command_args',
    'escape_markdown_v2',
    'build_deep_link',
    
    # Miscellaneous
    'safe_divide',
    'clamp',
    'get_plural',
]