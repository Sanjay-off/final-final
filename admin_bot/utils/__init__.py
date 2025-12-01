"""
Admin Bot Utils Package
Contains utility functions for validation, formatting, and helper operations.
"""

from .validators import (
    validate_user_id,
    validate_post_number,
    validate_hours,
    validate_file_size,
    validate_file_type,
    validate_channel_username,
    validate_url,
    validate_password,
    is_valid_telegram_link
)

from .formatters import (
    format_file_size,
    format_datetime,
    format_duration,
    format_number,
    format_percentage,
    truncate_text,
    escape_markdown,
    format_user_mention,
    format_verification_status,
    format_time_remaining
)

from .helpers import (
    encode_deep_link,
    decode_deep_link,
    generate_unique_id,
    calculate_expiry_time,
    is_expired,
    split_message,
    paginate_list,
    get_current_timestamp,
    mask_sensitive_data
)

__all__ = [
    # Validators
    'validate_user_id',
    'validate_post_number',
    'validate_hours',
    'validate_file_size',
    'validate_file_type',
    'validate_channel_username',
    'validate_url',
    'validate_password',
    'is_valid_telegram_link',
    
    # Formatters
    'format_file_size',
    'format_datetime',
    'format_duration',
    'format_number',
    'format_percentage',
    'truncate_text',
    'escape_markdown',
    'format_user_mention',
    'format_verification_status',
    'format_time_remaining',
    
    # Helpers
    'encode_deep_link',
    'decode_deep_link',
    'generate_unique_id',
    'calculate_expiry_time',
    'is_expired',
    'split_message',
    'paginate_list',
    'get_current_timestamp',
    'mask_sensitive_data',
]