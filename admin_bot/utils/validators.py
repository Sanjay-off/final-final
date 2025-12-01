"""
Validators for Admin Bot
Input validation functions for user data, files, URLs, and other inputs.
"""

import re
from typing import Tuple, Optional
from urllib.parse import urlparse


def validate_user_id(user_id: any) -> Tuple[bool, str]:
    """
    Validate Telegram user ID.
    
    Args:
        user_id: User ID to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        uid = int(user_id)
        
        if uid <= 0:
            return False, "User ID must be a positive number"
        
        if uid > 9999999999:  # Telegram max user ID (reasonable upper bound)
            return False, "User ID is too large"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, "User ID must be a valid number"


def validate_post_number(post_no: any) -> Tuple[bool, str]:
    """
    Validate post number.
    
    Args:
        post_no: Post number to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        pno = int(post_no)
        
        if pno <= 0:
            return False, "Post number must be a positive number"
        
        if pno > 99999999:  # Reasonable upper bound
            return False, "Post number is too large"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, "Post number must be a valid number"


def validate_hours(hours: any, min_hours: int = 1, max_hours: int = 8760) -> Tuple[bool, str]:
    """
    Validate hours for verification period.
    
    Args:
        hours: Hours to validate
        min_hours: Minimum allowed hours (default: 1)
        max_hours: Maximum allowed hours (default: 8760 = 365 days)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        hrs = int(hours)
        
        if hrs < min_hours:
            return False, f"Hours must be at least {min_hours}"
        
        if hrs > max_hours:
            return False, f"Hours cannot exceed {max_hours} ({max_hours // 24} days)"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, "Hours must be a valid number"


def validate_file_size(size_bytes: int, max_size_bytes: int = 2 * 1024 * 1024 * 1024) -> Tuple[bool, str]:
    """
    Validate file size.
    
    Args:
        size_bytes: File size in bytes
        max_size_bytes: Maximum allowed size in bytes (default: 2GB)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if size_bytes <= 0:
        return False, "File size must be greater than 0"
    
    if size_bytes > max_size_bytes:
        max_size_mb = max_size_bytes / (1024 * 1024)
        return False, f"File size exceeds maximum of {max_size_mb:.0f} MB"
    
    return True, ""


def validate_file_type(filename: str, allowed_extensions: list = None) -> Tuple[bool, str]:
    """
    Validate file type by extension.
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions (default: ['zip'])
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if allowed_extensions is None:
        allowed_extensions = ['zip']
    
    if not filename:
        return False, "Filename is empty"
    
    # Get file extension
    if '.' not in filename:
        return False, "File has no extension"
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension not in allowed_extensions:
        return False, f"File type .{extension} not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    return True, ""


def validate_channel_username(username: str) -> Tuple[bool, str]:
    """
    Validate Telegram channel username or ID.
    
    Args:
        username: Channel username or ID
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Channel username/ID is empty"
    
    username = username.strip()
    
    # Check if it's a channel ID (starts with -100)
    if username.startswith('-100'):
        try:
            channel_id = int(username)
            if len(username) < 13:  # Minimum length for channel IDs
                return False, "Channel ID is too short"
            return True, ""
        except ValueError:
            return False, "Invalid channel ID format"
    
    # Check if it's a username (starts with @)
    if username.startswith('@'):
        username = username[1:]  # Remove @
    
    # Validate username format
    if not re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
        return False, "Username must be 5-32 characters (letters, numbers, underscores only)"
    
    return True, ""


def validate_url(url: str, allowed_schemes: list = None) -> Tuple[bool, str]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        allowed_schemes: List of allowed schemes (default: ['http', 'https'])
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    if not url:
        return False, "URL is empty"
    
    try:
        result = urlparse(url)
        
        if not result.scheme:
            return False, "URL must include scheme (http:// or https://)"
        
        if result.scheme not in allowed_schemes:
            return False, f"URL scheme must be one of: {', '.join(allowed_schemes)}"
        
        if not result.netloc:
            return False, "URL must include domain"
        
        return True, ""
    
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def validate_password(password: str, min_length: int = 4, max_length: int = 50) -> Tuple[bool, str]:
    """
    Validate password.
    
    Args:
        password: Password to validate
        min_length: Minimum password length (default: 4)
        max_length: Maximum password length (default: 50)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is empty"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if len(password) > max_length:
        return False, f"Password must not exceed {max_length} characters"
    
    # Check for whitespace at start or end
    if password != password.strip():
        return False, "Password cannot have leading or trailing spaces"
    
    return True, ""


def is_valid_telegram_link(url: str) -> bool:
    """
    Check if URL is a valid Telegram link.
    
    Args:
        url: URL to check
    
    Returns:
        True if valid Telegram link, False otherwise
    """
    if not url:
        return False
    
    # Valid Telegram link patterns
    patterns = [
        r'^https://t\.me/',           # Standard links
        r'^https://telegram\.me/',     # Alternative domain
        r'^https://telegram\.dog/',    # Alternative domain
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    
    return False


def validate_telegram_link(url: str) -> Tuple[bool, str]:
    """
    Validate Telegram link.
    
    Args:
        url: URL to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is empty"
    
    if not is_valid_telegram_link(url):
        return False, "URL must be a valid Telegram link (https://t.me/...)"
    
    return True, ""


def validate_text_length(text: str, min_length: int = 1, max_length: int = 4096, field_name: str = "Text") -> Tuple[bool, str]:
    """
    Validate text length.
    
    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        field_name: Name of field for error message
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, f"{field_name} is empty"
    
    text_length = len(text.strip())
    
    if text_length < min_length:
        return False, f"{field_name} must be at least {min_length} characters"
    
    if text_length > max_length:
        return False, f"{field_name} must not exceed {max_length} characters"
    
    return True, ""


def validate_api_key(api_key: str, min_length: int = 10) -> Tuple[bool, str]:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        min_length: Minimum key length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is empty"
    
    if len(api_key) < min_length:
        return False, f"API key seems too short (minimum {min_length} characters)"
    
    # Check for suspicious patterns
    if api_key.isspace():
        return False, "API key cannot be only whitespace"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate Telegram username format.
    
    Args:
        username: Username to validate (with or without @)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is empty"
    
    # Remove @ if present
    if username.startswith('@'):
        username = username[1:]
    
    # Telegram username rules: 5-32 chars, alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]{5,32}$', username):
        return False, "Username must be 5-32 characters (letters, numbers, underscores only)"
    
    # Cannot start with number
    if username[0].isdigit():
        return False, "Username cannot start with a number"
    
    return True, ""


def validate_button_text(text: str, max_length: int = 64) -> Tuple[bool, str]:
    """
    Validate inline button text.
    
    Args:
        text: Button text to validate
        max_length: Maximum button text length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, "Button text is empty"
    
    if len(text) > max_length:
        return False, f"Button text must not exceed {max_length} characters"
    
    # Check for control characters
    if any(ord(char) < 32 for char in text):
        return False, "Button text contains invalid characters"
    
    return True, ""


def validate_callback_data(data: str, max_length: int = 64) -> Tuple[bool, str]:
    """
    Validate callback query data.
    
    Args:
        data: Callback data to validate
        max_length: Maximum callback data length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Callback data is empty"
    
    if len(data) > max_length:
        return False, f"Callback data must not exceed {max_length} bytes"
    
    return True, ""


def validate_message_id(message_id: any) -> Tuple[bool, str]:
    """
    Validate Telegram message ID.
    
    Args:
        message_id: Message ID to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        mid = int(message_id)
        
        if mid <= 0:
            return False, "Message ID must be a positive number"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, "Message ID must be a valid number"


def validate_channel_id(channel_id: any) -> Tuple[bool, str]:
    """
    Validate Telegram channel/group ID.
    
    Args:
        channel_id: Channel ID to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        cid = int(channel_id)
        
        # Channels and groups have negative IDs
        if cid >= 0:
            return False, "Channel/Group ID must be negative"
        
        # Channel IDs typically start with -100
        if not str(cid).startswith('-100'):
            return False, "Channel ID must start with -100"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, "Channel ID must be a valid number"


def validate_positive_number(number: any, field_name: str = "Number") -> Tuple[bool, str]:
    """
    Validate that a value is a positive number.
    
    Args:
        number: Number to validate
        field_name: Name of field for error message
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        num = float(number)
        
        if num <= 0:
            return False, f"{field_name} must be a positive number"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"


def validate_file_caption(caption: str, max_length: int = 1024) -> Tuple[bool, str]:
    """
    Validate file caption length.
    
    Args:
        caption: Caption to validate
        max_length: Maximum caption length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not caption:
        return True, ""  # Caption is optional
    
    if len(caption) > max_length:
        return False, f"Caption must not exceed {max_length} characters"
    
    return True, ""


def sanitize_and_validate(text: str, min_length: int = 1, max_length: int = 1000, field_name: str = "Input") -> Tuple[bool, str, str]:
    """
    Sanitize and validate text input.
    
    Args:
        text: Text to sanitize and validate
        min_length: Minimum length
        max_length: Maximum length
        field_name: Name of field for error message
    
    Returns:
        Tuple of (is_valid, error_message, sanitized_text)
    """
    if not text:
        return False, f"{field_name} is empty", ""
    
    # Sanitize
    sanitized = text.strip()
    sanitized = sanitized.replace('\x00', '')  # Remove null bytes
    
    # Validate length
    if len(sanitized) < min_length:
        return False, f"{field_name} must be at least {min_length} characters", sanitized
    
    if len(sanitized) > max_length:
        return False, f"{field_name} must not exceed {max_length} characters", sanitized
    
    return True, "", sanitized