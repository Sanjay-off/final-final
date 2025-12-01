"""
Shared Package
Contains utilities, constants, and helper functions shared between bots.
"""

from .constants import (
    # Bot Names
    ADMIN_BOT_NAME,
    USER_BOT_NAME,
    
    # Status Constants
    STATUS_PENDING,
    STATUS_IN_PROGRESS,
    STATUS_COMPLETED,
    STATUS_EXPIRED,
    
    # Verification
    DEFAULT_VERIFICATION_HOURS,
    DEFAULT_FILE_ACCESS_LIMIT,
    MIN_VERIFICATION_HOURS,
    MAX_VERIFICATION_HOURS,
    
    # File Limits
    MAX_FILE_SIZE_GB,
    MAX_FILE_SIZE_BYTES,
    ALLOWED_FILE_EXTENSIONS,
    
    # Time Constants
    AUTO_DELETE_MINUTES,
    TOKEN_EXPIRY_SECONDS,
    
    # Message Formats
    POST_TEMPLATE,
    FORCE_SUB_TEMPLATE,
    VERIFICATION_TEMPLATE,
    
    # Emojis
    EMOJI_SUCCESS,
    EMOJI_ERROR,
    EMOJI_WARNING,
    EMOJI_INFO,
    EMOJI_FILE,
    EMOJI_VERIFIED,
    EMOJI_DOWNLOAD,
)

from .utils import (
    # String utilities
    clean_text,
    truncate_string,
    generate_random_string,
    
    # Time utilities
    get_current_time,
    format_time_remaining,
    calculate_expiry,
    
    # Validation
    is_valid_telegram_id,
    is_valid_channel_id,
    
    # Formatting
    format_file_size,
    format_number_with_commas,
)

from .encryption import (
    # Encryption/Decryption
    encrypt_data,
    decrypt_data,
    
    # Token generation
    generate_token,
    generate_verification_token,
    
    # Hashing
    hash_string,
    verify_hash,
)

__version__ = "1.0.0"

__all__ = [
    # Constants - Bot Names
    'ADMIN_BOT_NAME',
    'USER_BOT_NAME',
    
    # Constants - Status
    'STATUS_PENDING',
    'STATUS_IN_PROGRESS',
    'STATUS_COMPLETED',
    'STATUS_EXPIRED',
    
    # Constants - Verification
    'DEFAULT_VERIFICATION_HOURS',
    'DEFAULT_FILE_ACCESS_LIMIT',
    'MIN_VERIFICATION_HOURS',
    'MAX_VERIFICATION_HOURS',
    
    # Constants - File Limits
    'MAX_FILE_SIZE_GB',
    'MAX_FILE_SIZE_BYTES',
    'ALLOWED_FILE_EXTENSIONS',
    
    # Constants - Time
    'AUTO_DELETE_MINUTES',
    'TOKEN_EXPIRY_SECONDS',
    
    # Constants - Templates
    'POST_TEMPLATE',
    'FORCE_SUB_TEMPLATE',
    'VERIFICATION_TEMPLATE',
    
    # Constants - Emojis
    'EMOJI_SUCCESS',
    'EMOJI_ERROR',
    'EMOJI_WARNING',
    'EMOJI_INFO',
    'EMOJI_FILE',
    'EMOJI_VERIFIED',
    'EMOJI_DOWNLOAD',
    
    # Utils - String
    'clean_text',
    'truncate_string',
    'generate_random_string',
    
    # Utils - Time
    'get_current_time',
    'format_time_remaining',
    'calculate_expiry',
    
    # Utils - Validation
    'is_valid_telegram_id',
    'is_valid_channel_id',
    
    # Utils - Formatting
    'format_file_size',
    'format_number_with_commas',
    
    # Encryption
    'encrypt_data',
    'decrypt_data',
    'generate_token',
    'generate_verification_token',
    'hash_string',
    'verify_hash',
]