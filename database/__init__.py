"""
Database Package
Main package for database operations, models, and migrations.
"""

# Import database connection functions
from config.database import (
    get_database,
    connect_database,
    close_database,
    get_collection,
    test_connection,
    get_database_stats
)

# Import database models
from .models import (
    FileModel,
    UserVerificationModel,
    VerificationTokenModel,
    ForceSubChannelModel,
    AdminSettingModel,
    AdminLogModel
)

# Import database operations - Files
from .operations.files import (
    add_file,
    get_file_by_post_no,
    get_file_by_id,
    get_all_files,
    update_file,
    delete_file,
    increment_download_count,
    get_total_files_count,
    get_total_downloads_count,
    get_most_downloaded_files,
)

# Import database operations - Users
from .operations.users import (
    get_user_by_id,
    create_user,
    update_user,
    get_all_users,
    get_all_users_count,
    get_verified_users,
    get_verified_users_count,
    get_active_users,
    verify_user_manually,
    unverify_user,
    reset_user_file_limit,
    increment_user_file_access,
)

# Import database operations - Verification
from .operations.verification import (
    create_verification_token,
    get_verification_token,
    update_token_status,
    mark_token_completed,
    is_token_valid,
    cleanup_expired_tokens,
)

# Import database operations - Channels
from .operations.channels import (
    add_channel,
    get_channel_by_id,
    get_all_channels,
    get_active_channels,
    remove_channel,
    toggle_channel_status,
)

# Import database operations - Settings
from .operations.settings import (
    get_setting,
    get_setting_value,
    set_setting,
    get_all_settings,
    get_all_settings_dict,
)

# Import database operations - Logs
from .operations.logs import (
    log_admin_action,
    get_admin_logs,
    get_logs_by_admin,
    get_recent_logs,
    cleanup_old_logs,
)

# Import migrations
from .migrations.init_db import (
    initialize_database,
    get_database_status,
    print_database_status
)

__version__ = "1.0.0"

__all__ = [
    # Database connection
    'get_database',
    'connect_database',
    'close_database',
    'get_collection',
    'test_connection',
    'get_database_stats',
    
    # Models
    'FileModel',
    'UserVerificationModel',
    'VerificationTokenModel',
    'ForceSubChannelModel',
    'AdminSettingModel',
    'AdminLogModel',
    
    # Files operations
    'add_file',
    'get_file_by_post_no',
    'get_file_by_id',
    'get_all_files',
    'update_file',
    'delete_file',
    'increment_download_count',
    'get_total_files_count',
    'get_total_downloads_count',
    'get_most_downloaded_files',
    
    # Users operations
    'get_user_by_id',
    'create_user',
    'update_user',
    'get_all_users',
    'get_all_users_count',
    'get_verified_users',
    'get_verified_users_count',
    'get_active_users',
    'verify_user_manually',
    'unverify_user',
    'reset_user_file_limit',
    'increment_user_file_access',
    
    # Verification operations
    'create_verification_token',
    'get_verification_token',
    'update_token_status',
    'mark_token_completed',
    'is_token_valid',
    'cleanup_expired_tokens',
    
    # Channels operations
    'add_channel',
    'get_channel_by_id',
    'get_all_channels',
    'get_active_channels',
    'remove_channel',
    'toggle_channel_status',
    
    # Settings operations
    'get_setting',
    'get_setting_value',
    'set_setting',
    'get_all_settings',
    'get_all_settings_dict',
    
    # Logs operations
    'log_admin_action',
    'get_admin_logs',
    'get_logs_by_admin',
    'get_recent_logs',
    'cleanup_old_logs',
    
    # Migrations
    'initialize_database',
    'get_database_status',
    'print_database_status',
]