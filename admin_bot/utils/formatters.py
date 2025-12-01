"""
Formatters for Admin Bot
Utility functions for formatting data, text, numbers, and dates.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import re


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted file size string (e.g., "1.5 MB", "2.3 GB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object to format
        format_string: Format string (default: YYYY-MM-DD HH:MM:SS)
    
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


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string (e.g., "2h 30m", "1d 5h")
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


def format_number(number: Union[int, float], decimals: int = 0) -> str:
    """
    Format number with thousands separator.
    
    Args:
        number: Number to format
        decimals: Number of decimal places
    
    Returns:
        Formatted number string (e.g., "1,234", "1,234.56")
    """
    if decimals > 0:
        return f"{number:,.{decimals}f}"
    else:
        return f"{int(number):,}"


def format_percentage(value: float, total: float, decimals: int = 1) -> str:
    """
    Calculate and format percentage.
    
    Args:
        value: Value to calculate percentage for
        total: Total value
        decimals: Number of decimal places
    
    Returns:
        Formatted percentage string (e.g., "75.5%")
    """
    if total == 0:
        return "0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.{decimals}f}%"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
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


def escape_markdown(text: str, version: int = 2) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    
    Args:
        text: Text to escape
        version: Markdown version (1 or 2)
    
    Returns:
        Escaped text
    """
    if not text:
        return ""
    
    if version == 2:
        # MarkdownV2 special characters
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
    else:
        # Markdown (v1) special characters
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
    
    return text


def format_user_mention(user_id: int, username: Optional[str] = None, first_name: Optional[str] = None) -> str:
    """
    Format user mention for display.
    
    Args:
        user_id: User's Telegram ID
        username: User's username (optional)
        first_name: User's first name (optional)
    
    Returns:
        Formatted user mention
    """
    if username:
        return f"@{username}"
    elif first_name:
        return f"{first_name} (`{user_id}`)"
    else:
        return f"User `{user_id}`"


def format_verification_status(is_verified: bool, expires_at: Optional[datetime] = None) -> str:
    """
    Format verification status with emoji and details.
    
    Args:
        is_verified: Whether user is verified
        expires_at: Expiry datetime (optional)
    
    Returns:
        Formatted status string
    """
    if not is_verified:
        return "❌ Not Verified"
    
    if not expires_at:
        return "✅ Verified"
    
    now = datetime.now()
    
    if expires_at < now:
        return "⏰ Expired"
    
    time_left = expires_at - now
    hours_left = int(time_left.total_seconds() / 3600)
    
    if hours_left < 1:
        minutes_left = int(time_left.total_seconds() / 60)
        return f"⚠️ Expiring Soon ({minutes_left}m left)"
    elif hours_left < 24:
        return f"✅ Active ({hours_left}h left)"
    else:
        days_left = hours_left // 24
        return f"✅ Active ({days_left}d left)"


def format_time_remaining(expires_at: datetime) -> str:
    """
    Format time remaining until expiry.
    
    Args:
        expires_at: Expiry datetime
    
    Returns:
        Formatted time remaining string
    """
    if not expires_at:
        return "N/A"
    
    now = datetime.now()
    
    if expires_at < now:
        return "Expired"
    
    time_left = expires_at - now
    total_seconds = int(time_left.total_seconds())
    
    return format_duration(total_seconds)


def format_timestamp(timestamp: Optional[datetime] = None, relative: bool = False) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: Datetime object (defaults to now)
        relative: Whether to show relative time (e.g., "2 hours ago")
    
    Returns:
        Formatted timestamp string
    """
    if not timestamp:
        timestamp = datetime.now()
    
    if relative:
        now = datetime.now()
        diff = now - timestamp
        
        if diff.total_seconds() < 60:
            return "just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days < 30:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        else:
            return format_datetime(timestamp, "%Y-%m-%d")
    
    return format_datetime(timestamp)


def format_list_items(items: list, max_items: int = 10, numbered: bool = True) -> str:
    """
    Format a list of items for display.
    
    Args:
        items: List of items to format
        max_items: Maximum items to show
        numbered: Whether to number items
    
    Returns:
        Formatted list string
    """
    if not items:
        return "No items"
    
    result = []
    display_items = items[:max_items]
    
    for idx, item in enumerate(display_items, 1):
        if numbered:
            result.append(f"{idx}. {item}")
        else:
            result.append(f"• {item}")
    
    if len(items) > max_items:
        result.append(f"\n... and {len(items) - max_items} more")
    
    return "\n".join(result)


def format_key_value(key: str, value: str, inline: bool = False) -> str:
    """
    Format key-value pair for display.
    
    Args:
        key: Key name
        value: Value
        inline: Whether to format inline or on separate lines
    
    Returns:
        Formatted key-value string
    """
    if inline:
        return f"{key}: {value}"
    else:
        return f"*{key}:*\n{value}"


def format_stats_row(label: str, value: Union[int, str], emoji: str = "") -> str:
    """
    Format statistics row.
    
    Args:
        label: Label text
        value: Value to display
        emoji: Optional emoji prefix
    
    Returns:
        Formatted stats row
    """
    emoji_str = f"{emoji} " if emoji else ""
    
    if isinstance(value, int):
        value_str = format_number(value)
    else:
        value_str = str(value)
    
    return f"{emoji_str}{label}: `{value_str}`"


def format_button_text(text: str, max_length: int = 30) -> str:
    """
    Format text for button labels.
    
    Args:
        text: Button text
        max_length: Maximum button text length
    
    Returns:
        Formatted button text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 2] + "..."


def format_code_block(text: str, language: str = "") -> str:
    """
    Format text as code block.
    
    Args:
        text: Text to format
        language: Programming language for syntax highlighting
    
    Returns:
        Formatted code block
    """
    if language:
        return f"```{language}\n{text}\n```"
    else:
        return f"```\n{text}\n```"


def format_inline_code(text: str) -> str:
    """
    Format text as inline code.
    
    Args:
        text: Text to format
    
    Returns:
        Formatted inline code
    """
    return f"`{text}`"


def format_bold(text: str) -> str:
    """Format text as bold (Markdown)."""
    return f"*{text}*"


def format_italic(text: str) -> str:
    """Format text as italic (Markdown)."""
    return f"_{text}_"


def format_quote(text: str) -> str:
    """Format text as quote block."""
    lines = text.split('\n')
    return '\n'.join(f"> {line}" for line in lines)


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Cleaned filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename