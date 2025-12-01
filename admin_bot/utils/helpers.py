"""
Helper Utilities for Admin Bot
General purpose helper functions for common operations.
"""

import base64
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Any, Tuple
from telegram.constants import MessageLimit


def encode_deep_link(data: str) -> str:
    """
    Encode data for Telegram deep link.
    
    Args:
        data: Data to encode (e.g., "get-12345")
    
    Returns:
        Base64 encoded string safe for deep links
    """
    try:
        encoded = base64.urlsafe_b64encode(data.encode()).decode()
        # Remove padding for cleaner links
        return encoded.rstrip('=')
    except Exception as e:
        print(f"Error encoding deep link: {e}")
        return data


def decode_deep_link(encoded_data: str) -> str:
    """
    Decode data from Telegram deep link.
    
    Args:
        encoded_data: Base64 encoded string
    
    Returns:
        Decoded string
    """
    try:
        # Add padding back if needed
        padding = 4 - (len(encoded_data) % 4)
        if padding != 4:
            encoded_data += '=' * padding
        
        decoded = base64.urlsafe_b64decode(encoded_data.encode()).decode()
        return decoded
    except Exception as e:
        print(f"Error decoding deep link: {e}")
        return encoded_data


def generate_unique_id(prefix: str = "", length: int = 16) -> str:
    """
    Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of random part
    
    Returns:
        Unique ID string
    """
    random_part = secrets.token_hex(length // 2)
    
    if prefix:
        return f"{prefix}_{random_part}"
    
    return random_part


def calculate_expiry_time(hours: int, from_time: Optional[datetime] = None) -> datetime:
    """
    Calculate expiry time from now or specified time.
    
    Args:
        hours: Hours until expiry
        from_time: Starting time (defaults to now)
    
    Returns:
        Expiry datetime
    """
    if from_time is None:
        from_time = datetime.now()
    
    return from_time + timedelta(hours=hours)


def is_expired(expires_at: datetime) -> bool:
    """
    Check if a datetime has expired.
    
    Args:
        expires_at: Expiry datetime
    
    Returns:
        True if expired, False otherwise
    """
    if not expires_at:
        return True
    
    return datetime.now() > expires_at


def split_message(text: str, max_length: int = MessageLimit.MAX_TEXT_LENGTH) -> List[str]:
    """
    Split long message into multiple parts.
    
    Args:
        text: Text to split
        max_length: Maximum length per message (default: Telegram limit)
    
    Returns:
        List of message parts
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    # Split by lines to avoid breaking sentences
    lines = text.split('\n')
    
    for line in lines:
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + '\n'
        else:
            if current_part:
                parts.append(current_part.rstrip())
            
            # If single line is too long, split it
            if len(line) > max_length:
                for i in range(0, len(line), max_length):
                    parts.append(line[i:i + max_length])
                current_part = ""
            else:
                current_part = line + '\n'
    
    if current_part:
        parts.append(current_part.rstrip())
    
    return parts


def paginate_list(items: List[Any], page: int = 1, items_per_page: int = 10) -> Tuple[List[Any], int]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Current page number (1-indexed)
        items_per_page: Number of items per page
    
    Returns:
        Tuple of (paginated_items, total_pages)
    """
    total_items = len(items)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # Ensure page is within bounds
    page = max(1, min(page, total_pages if total_pages > 0 else 1))
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    paginated_items = items[start_idx:end_idx]
    
    return paginated_items, total_pages


def get_current_timestamp() -> int:
    """
    Get current Unix timestamp.
    
    Returns:
        Current timestamp in seconds
    """
    return int(datetime.now().timestamp())


def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """
    Mask sensitive data (e.g., API keys, tokens).
    
    Args:
        data: Sensitive data to mask
        show_chars: Number of characters to show at start and end
    
    Returns:
        Masked string
    """
    if not data or len(data) <= show_chars * 2:
        return '*' * len(data)
    
    visible_start = data[:show_chars]
    visible_end = data[-show_chars:]
    masked_middle = '*' * (len(data) - show_chars * 2)
    
    return f"{visible_start}{masked_middle}{visible_end}"


def generate_hash(data: str, algorithm: str = 'sha256') -> str:
    """
    Generate hash of data.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (md5, sha1, sha256)
    
    Returns:
        Hexadecimal hash string
    """
    if algorithm == 'md5':
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(data.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(data.encode()).hexdigest()
    else:
        return hashlib.sha256(data.encode()).hexdigest()


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def parse_time_string(time_str: str) -> Optional[int]:
    """
    Parse time string to hours.
    
    Args:
        time_str: Time string (e.g., "24h", "2d", "1w")
    
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


def format_deep_link_url(bot_username: str, start_parameter: str) -> str:
    """
    Format deep link URL for bot.
    
    Args:
        bot_username: Bot username (without @)
        start_parameter: Start parameter (already encoded)
    
    Returns:
        Complete deep link URL
    """
    return f"https://t.me/{bot_username}?start={start_parameter}"


def extract_user_id_from_mention(mention: str) -> Optional[int]:
    """
    Extract user ID from mention text.
    
    Args:
        mention: Mention text (e.g., "@username" or "123456789")
    
    Returns:
        User ID as integer, or None if not found
    """
    # Remove @ if present
    mention = mention.strip().lstrip('@')
    
    # Try to parse as integer
    try:
        return int(mention)
    except ValueError:
        return None


def get_time_until(target_time: datetime) -> dict:
    """
    Get detailed time until target datetime.
    
    Args:
        target_time: Target datetime
    
    Returns:
        Dictionary with days, hours, minutes, seconds
    """
    if not target_time:
        return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
    
    now = datetime.now()
    
    if target_time < now:
        return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
    
    delta = target_time - now
    
    days = delta.days
    seconds = delta.seconds
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    return {
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }


def is_valid_user_id(user_id: Any) -> bool:
    """
    Check if user ID is valid.
    
    Args:
        user_id: User ID to check
    
    Returns:
        True if valid, False otherwise
    """
    try:
        uid = int(user_id)
        # Telegram user IDs are positive integers
        return uid > 0
    except (ValueError, TypeError):
        return False


def merge_dicts(*dicts: dict) -> dict:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Name of file
    
    Returns:
        File extension (lowercase, without dot)
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ""


def is_zip_file(filename: str) -> bool:
    """
    Check if filename is a ZIP file.
    
    Args:
        filename: Name of file
    
    Returns:
        True if ZIP file, False otherwise
    """
    return get_file_extension(filename) == 'zip'


def calculate_success_rate(success: int, total: int) -> float:
    """
    Calculate success rate percentage.
    
    Args:
        success: Number of successful operations
        total: Total operations
    
    Returns:
        Success rate as percentage (0-100)
    """
    if total == 0:
        return 0.0
    
    return (success / total) * 100


def generate_verification_token() -> str:
    """
    Generate a secure verification token.
    
    Returns:
        Random verification token
    """
    return secrets.token_urlsafe(32)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
    
    Returns:
        Result of division or default
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