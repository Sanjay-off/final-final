"""
User Bot Utils Package
Contains utility functions for file management, verification, force subscribe, and formatting.
"""

from .force_sub import (
    check_user_subscribed,
    get_unsubscribed_channels,
    build_force_sub_message,
)

from .verification import (
    is_user_verified,
    check_verification_status,
    generate_verification_link,
)

from .token import (
    generate_token,
    encrypt_token,
    decrypt_token,
    validate_token,
)

from .file_manager import (
    send_file_with_autodelete,
    schedule_file_deletion,
    delete_messages,
    send_file_deleted_notification,
)

from .formatters import (
    format_force_sub_message,
    format_verification_message,
    format_file_caption,
    format_limit_reached_message,
    format_verified_success_message,
    format_bypass_detected_message,
)

__all__ = [
    # Force Subscribe
    'check_user_subscribed',
    'get_unsubscribed_channels',
    'build_force_sub_message',
    
    # Verification
    'is_user_verified',
    'check_verification_status',
    'generate_verification_link',
    
    # Token
    'generate_token',
    'encrypt_token',
    'decrypt_token',
    'validate_token',
    
    # File Manager
    'send_file_with_autodelete',
    'schedule_file_deletion',
    'delete_messages',
    'send_file_deleted_notification',
    
    # Formatters
    'format_force_sub_message',
    'format_verification_message',
    'format_file_caption',
    'format_limit_reached_message',
    'format_verified_success_message',
    'format_bypass_detected_message',
]