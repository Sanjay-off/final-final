"""
Configuration Package
Manages all configuration settings, environment variables, and database connections.
"""

from .settings import (
    # Bot Tokens
    ADMIN_BOT_TOKEN,
    USER_BOT_TOKEN,
    USER_BOT_USERNAME,
    
    # MongoDB
    MONGODB_URI,
    
    # Telegram Channels
    PRIVATE_STORAGE_CHANNEL_ID,
    PUBLIC_GROUP_ID,
    
    # Admin IDs
    ADMIN_IDS,
    
    # Verification Settings
    VERIFICATION_SERVER_URL,
    VERIFICATION_TOKEN_EXPIRY,
    ENCRYPTION_KEY,
    
    # Shortlink API
    SHORTLINK_API_KEY,
    SHORTLINK_BASE_URL,
    
    # File Settings
    FILE_PASSWORD,
    FILE_ACCESS_LIMIT,
    VERIFICATION_PERIOD_HOURS,
)

from .database import (
    get_database,
    connect_database,
    close_database,
    get_collection,
)

__all__ = [
    # Settings
    'ADMIN_BOT_TOKEN',
    'USER_BOT_TOKEN',
    'USER_BOT_USERNAME',
    'MONGODB_URI',
    'PRIVATE_STORAGE_CHANNEL_ID',
    'PUBLIC_GROUP_ID',
    'ADMIN_IDS',
    'VERIFICATION_SERVER_URL',
    'VERIFICATION_TOKEN_EXPIRY',
    'ENCRYPTION_KEY',
    'SHORTLINK_API_KEY',
    'SHORTLINK_BASE_URL',
    'FILE_PASSWORD',
    'FILE_ACCESS_LIMIT',
    'VERIFICATION_PERIOD_HOURS',
    
    # Database
    'get_database',
    'connect_database',
    'close_database',
    'get_collection',
]