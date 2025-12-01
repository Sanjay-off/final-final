"""
Settings Configuration
Loads all configuration from environment variables.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# BOT TOKENS
# ============================================================================

ADMIN_BOT_TOKEN: str = os.getenv('ADMIN_BOT_TOKEN', '')
USER_BOT_TOKEN: str = os.getenv('USER_BOT_TOKEN', '')
USER_BOT_USERNAME: str = os.getenv('USER_BOT_USERNAME', 'userbot')

if not ADMIN_BOT_TOKEN:
    raise ValueError("ADMIN_BOT_TOKEN is not set in environment variables")

if not USER_BOT_TOKEN:
    raise ValueError("USER_BOT_TOKEN is not set in environment variables")


# ============================================================================
# MONGODB CONFIGURATION
# ============================================================================

MONGODB_URI: str = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/telegram_bot_db')


# ============================================================================
# TELEGRAM CHANNELS
# ============================================================================

def parse_channel_id(channel_id_str: str) -> Optional[int]:
    """Parse channel ID from string to integer."""
    try:
        return int(channel_id_str) if channel_id_str else None
    except ValueError:
        return None


PRIVATE_STORAGE_CHANNEL_ID: Optional[int] = parse_channel_id(
    os.getenv('PRIVATE_STORAGE_CHANNEL_ID', '')
)
PUBLIC_GROUP_ID: Optional[int] = parse_channel_id(
    os.getenv('PUBLIC_GROUP_ID', '')
)

if not PRIVATE_STORAGE_CHANNEL_ID:
    raise ValueError("PRIVATE_STORAGE_CHANNEL_ID is not set or invalid")

if not PUBLIC_GROUP_ID:
    raise ValueError("PUBLIC_GROUP_ID is not set or invalid")


# ============================================================================
# ADMIN USER IDS
# ============================================================================

def parse_admin_ids(admin_ids_str: str) -> List[int]:
    """Parse admin IDs from comma-separated string."""
    if not admin_ids_str:
        return []
    
    try:
        return [int(uid.strip()) for uid in admin_ids_str.split(',') if uid.strip()]
    except ValueError:
        print("Warning: Invalid ADMIN_IDS format in .env file")
        return []


ADMIN_IDS: List[int] = parse_admin_ids(os.getenv('ADMIN_IDS', ''))

if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS is not set or empty. At least one admin is required.")


# ============================================================================
# VERIFICATION SETTINGS
# ============================================================================

VERIFICATION_SERVER_URL: str = os.getenv(
    'VERIFICATION_SERVER_URL',
    'http://localhost:5000'
)

VERIFICATION_TOKEN_EXPIRY: int = int(os.getenv('VERIFICATION_TOKEN_EXPIRY', '600'))  # seconds

ENCRYPTION_KEY: str = os.getenv('ENCRYPTION_KEY', '')

if not ENCRYPTION_KEY:
    print("Warning: ENCRYPTION_KEY is not set. Using default (INSECURE for production)")
    ENCRYPTION_KEY = 'default_insecure_key_change_this'


# ============================================================================
# SHORTLINK API
# ============================================================================

SHORTLINK_API_KEY: str = os.getenv('SHORTLINK_API_KEY', '')
SHORTLINK_BASE_URL: str = os.getenv('SHORTLINK_BASE_URL', '')

if not SHORTLINK_API_KEY:
    print("Warning: SHORTLINK_API_KEY is not set")

if not SHORTLINK_BASE_URL:
    print("Warning: SHORTLINK_BASE_URL is not set")


# ============================================================================
# FILE SETTINGS
# ============================================================================

FILE_PASSWORD: str = os.getenv('FILE_PASSWORD', 'default123')
FILE_ACCESS_LIMIT: int = int(os.getenv('FILE_ACCESS_LIMIT', '3'))
VERIFICATION_PERIOD_HOURS: int = int(os.getenv('VERIFICATION_PERIOD_HOURS', '24'))


# ============================================================================
# ADDITIONAL SETTINGS
# ============================================================================

# Debug mode
DEBUG: bool = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Log level
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO').upper()

# Maximum file size (in bytes) - default 2GB
MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', str(2 * 1024 * 1024 * 1024)))

# Allowed file extensions
ALLOWED_FILE_EXTENSIONS: List[str] = os.getenv(
    'ALLOWED_FILE_EXTENSIONS',
    'zip'
).split(',')

# Broadcast delay (seconds between messages)
BROADCAST_DELAY: float = float(os.getenv('BROADCAST_DELAY', '0.05'))

# Auto-delete time for files (minutes)
AUTO_DELETE_TIME: int = int(os.getenv('AUTO_DELETE_TIME', '10'))


# ============================================================================
# VALIDATION
# ============================================================================

def validate_settings() -> None:
    """
    Validate all critical settings.
    Raises ValueError if any critical setting is missing or invalid.
    """
    errors = []
    
    # Check bot tokens
    if not ADMIN_BOT_TOKEN or len(ADMIN_BOT_TOKEN) < 20:
        errors.append("Invalid ADMIN_BOT_TOKEN")
    
    if not USER_BOT_TOKEN or len(USER_BOT_TOKEN) < 20:
        errors.append("Invalid USER_BOT_TOKEN")
    
    # Check channel IDs
    if not PRIVATE_STORAGE_CHANNEL_ID or PRIVATE_STORAGE_CHANNEL_ID >= 0:
        errors.append("PRIVATE_STORAGE_CHANNEL_ID must be a negative integer")
    
    if not PUBLIC_GROUP_ID or PUBLIC_GROUP_ID >= 0:
        errors.append("PUBLIC_GROUP_ID must be a negative integer")
    
    # Check admin IDs
    if not ADMIN_IDS:
        errors.append("ADMIN_IDS must contain at least one admin")
    
    # Check MongoDB URI
    if not MONGODB_URI or not MONGODB_URI.startswith('mongodb'):
        errors.append("Invalid MONGODB_URI")
    
    # Check file settings
    if FILE_ACCESS_LIMIT < 1:
        errors.append("FILE_ACCESS_LIMIT must be at least 1")
    
    if VERIFICATION_PERIOD_HOURS < 1:
        errors.append("VERIFICATION_PERIOD_HOURS must be at least 1")
    
    if errors:
        error_message = "Configuration errors:\n" + "\n".join(f"  - {err}" for err in errors)
        raise ValueError(error_message)


def print_settings() -> None:
    """
    Print current settings (masking sensitive data).
    Useful for debugging configuration.
    """
    def mask_token(token: str) -> str:
        """Mask token for display."""
        if len(token) > 10:
            return token[:5] + '*' * (len(token) - 10) + token[-5:]
        return '*' * len(token)
    
    print("=" * 60)
    print("TELEGRAM FILE DISTRIBUTION SYSTEM - CONFIGURATION")
    print("=" * 60)
    print(f"Admin Bot Token: {mask_token(ADMIN_BOT_TOKEN)}")
    print(f"User Bot Token: {mask_token(USER_BOT_TOKEN)}")
    print(f"User Bot Username: @{USER_BOT_USERNAME}")
    print(f"MongoDB URI: {MONGODB_URI.split('@')[-1] if '@' in MONGODB_URI else MONGODB_URI}")
    print(f"Private Storage Channel: {PRIVATE_STORAGE_CHANNEL_ID}")
    print(f"Public Group ID: {PUBLIC_GROUP_ID}")
    print(f"Admin IDs: {ADMIN_IDS}")
    print(f"Verification Server: {VERIFICATION_SERVER_URL}")
    print(f"Verification Token Expiry: {VERIFICATION_TOKEN_EXPIRY}s")
    print(f"Encryption Key: {'[SET]' if ENCRYPTION_KEY else '[NOT SET]'}")
    print(f"Shortlink API Key: {'[SET]' if SHORTLINK_API_KEY else '[NOT SET]'}")
    print(f"Shortlink Base URL: {SHORTLINK_BASE_URL or '[NOT SET]'}")
    print(f"File Password: {FILE_PASSWORD}")
    print(f"File Access Limit: {FILE_ACCESS_LIMIT}")
    print(f"Verification Period: {VERIFICATION_PERIOD_HOURS}h")
    print(f"Max File Size: {MAX_FILE_SIZE / (1024**3):.2f} GB")
    print(f"Allowed Extensions: {', '.join(ALLOWED_FILE_EXTENSIONS)}")
    print(f"Debug Mode: {DEBUG}")
    print(f"Log Level: {LOG_LEVEL}")
    print("=" * 60)


# Validate settings on import
try:
    validate_settings()
except ValueError as e:
    print(f"\n⚠️  Configuration Error:\n{e}\n")
    print("Please check your .env file and ensure all required variables are set correctly.")
    raise


# ============================================================================
# EXPORT ALL SETTINGS
# ============================================================================

__all__ = [
    # Bot Configuration
    'ADMIN_BOT_TOKEN',
    'USER_BOT_TOKEN',
    'USER_BOT_USERNAME',
    
    # Database
    'MONGODB_URI',
    
    # Channels
    'PRIVATE_STORAGE_CHANNEL_ID',
    'PUBLIC_GROUP_ID',
    
    # Admins
    'ADMIN_IDS',
    
    # Verification
    'VERIFICATION_SERVER_URL',
    'VERIFICATION_TOKEN_EXPIRY',
    'ENCRYPTION_KEY',
    
    # Shortlink
    'SHORTLINK_API_KEY',
    'SHORTLINK_BASE_URL',
    
    # File Settings
    'FILE_PASSWORD',
    'FILE_ACCESS_LIMIT',
    'VERIFICATION_PERIOD_HOURS',
    
    # Additional
    'DEBUG',
    'LOG_LEVEL',
    'MAX_FILE_SIZE',
    'ALLOWED_FILE_EXTENSIONS',
    'BROADCAST_DELAY',
    'AUTO_DELETE_TIME',
    
    # Utilities
    'validate_settings',
    'print_settings',
]