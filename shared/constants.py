"""
Shared Constants
Application-wide constants used by both admin and user bots.
"""

# ============================================================================
# BOT INFORMATION
# ============================================================================

ADMIN_BOT_NAME = "Admin Bot"
USER_BOT_NAME = "User Bot"
SYSTEM_NAME = "Telegram File Distribution System"
VERSION = "1.0.0"


# ============================================================================
# TOKEN STATUS CONSTANTS
# ============================================================================

STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_EXPIRED = "expired"


# ============================================================================
# VERIFICATION SETTINGS
# ============================================================================

DEFAULT_VERIFICATION_HOURS = 24
DEFAULT_FILE_ACCESS_LIMIT = 3
MIN_VERIFICATION_HOURS = 1
MAX_VERIFICATION_HOURS = 8760  # 365 days


# ============================================================================
# FILE SETTINGS
# ============================================================================

MAX_FILE_SIZE_GB = 2
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024 * 1024  # 2GB in bytes
ALLOWED_FILE_EXTENSIONS = ['zip']
DEFAULT_FILE_PASSWORD = "default123"


# ============================================================================
# TIME CONSTANTS (in various units)
# ============================================================================

AUTO_DELETE_MINUTES = 10
AUTO_DELETE_SECONDS = 10 * 60
TOKEN_EXPIRY_SECONDS = 600  # 10 minutes
VERIFICATION_COUNTDOWN_SECONDS = 5
BROADCAST_DELAY_SECONDS = 0.05


# ============================================================================
# LIMITS
# ============================================================================

MAX_BROADCAST_USERS = 10000
MAX_CHANNELS_PER_BOT = 20
MAX_POST_NUMBER = 99999999
MIN_POST_NUMBER = 1
MAX_BUTTON_TEXT_LENGTH = 64
MAX_CONTEXT_LENGTH = 200
MAX_EXTRA_MESSAGE_LENGTH = 300
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 50


# ============================================================================
# EMOJIS
# ============================================================================

EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"
EMOJI_FILE = "📁"
EMOJI_VERIFIED = "✅"
EMOJI_UNVERIFIED = "❌"
EMOJI_DOWNLOAD = "⬇️"
EMOJI_UPLOAD = "⬆️"
EMOJI_BROADCAST = "📢"
EMOJI_STATS = "📊"
EMOJI_SETTINGS = "⚙️"
EMOJI_CHANNEL = "📺"
EMOJI_USER = "👤"
EMOJI_ADMIN = "👑"
EMOJI_TIME = "⏰"
EMOJI_EXPIRED = "⏰"
EMOJI_PENDING = "⏳"
EMOJI_LOCK = "🔐"
EMOJI_FIRE = "🔥"
EMOJI_CHECK = "✓"
EMOJI_CROSS = "✗"
EMOJI_SKULL = "💀"
EMOJI_ALERT = "🚨"
EMOJI_REFRESH = "🔄"
EMOJI_BACK = "🔙"
EMOJI_CLOSE = "❌"
EMOJI_MENU = "📋"


# ============================================================================
# MESSAGE TEMPLATES
# ============================================================================

POST_TEMPLATE = """Post - {{{post_no}}} 💀

Context:{{{context}}}

❝ {extra_message} ❞"""

FORCE_SUB_TEMPLATE = """❝ » HEY, {username} ×~ ❞

YOUR FILE IS READY ‼️ LOOKS LIKE YOU HAVEN'T SUBSCRIBED TO OUR CHANNELS YET,
SUBSCRIBE NOW TO GET YOUR FILES."""

VERIFICATION_TEMPLATE = """⚡ HEY, {username} ×~

» YOU NEED TO VERIFY A TOKEN TO GET FREE ACCESS FOR 1 DAY ✅

» IF YOU DONT WANT TO OPEN SHORT LINKS THEN YOU CAN TAKE PREMIUM SERVICES"""

VERIFIED_SUCCESS_TEMPLATE = "✅ VERIFIED SUCCESSFULLY"

BYPASS_DETECTED_TEMPLATE = """🚨 BYPASS DETECTED 🚨

HOW MANY TIMES HAVE I TOLD YOU, DON'T TRY TO OUTSMART YOUR DAD 😡🔥

NOW BE A GOOD BOY AND SOLVE IT AGAIN, AND THIS TIME DON'T GET SMART‼️ 💀 💣"""

ALREADY_VERIFIED_TEMPLATE = "✅ ALREADY VERIFIED"

TOKEN_ERROR_TEMPLATE = "❌ TOKEN ERROR OR EXPIRED"

LIMIT_REACHED_TEMPLATE = """⚠️ DAILY LIMIT REACHED

You have accessed your maximum of {limit} files for today. To continue accessing files, please verify again.

Your verification period will reset, and you'll get {limit} new file access attempts.

Click below to verify again. ⬇️"""

FILE_DELETED_TEMPLATE = """PREVIOUS MESSAGE WAS DELETED 🗑️

IF YOU WANT TO GET THE FILES AGAIN, THEN CLICK [♻️ CLICK HERE] BUTTON BELOW ELSE CLOSE THIS MESSAGE."""

AUTO_DELETE_WARNING = """⚠️ TELEGRAM MF DONT LIKE IT SO....

YOUR FILES WILL BE DELETED WITHIN **{minutes} MINUTES**. SO PLEASE FORWARD THEM TO ANY OTHER PLACE FOR FUTURE AVAILABILITY."""


# ============================================================================
# BUTTON TEXTS
# ============================================================================

BUTTON_DOWNLOAD = "⬇️ DOWNLOAD ⬇️"
BUTTON_VERIFY_NOW = "• VERIFY NOW •"
BUTTON_HOW_TO_VERIFY = "• HOW TO VERIFY •"
BUTTON_TRY_AGAIN = "• TRY AGAIN •"
BUTTON_CLICK_HERE = "♻️ CLICK HERE"
BUTTON_CLOSE = "CLOSE ✖️"
BUTTON_BACK = "🔙 Back"
BUTTON_CANCEL = "❌ Cancel"
BUTTON_CONFIRM = "✅ Confirm"


# ============================================================================
# ACTION TYPES (for logging)
# ============================================================================

ACTION_START_BOT = "start_bot"
ACTION_UPLOAD_FILE = "upload_file"
ACTION_DELETE_FILE = "delete_file"
ACTION_VERIFY_USER = "verify_user"
ACTION_UNVERIFY_USER = "unverify_user"
ACTION_RESET_LIMIT = "reset_user_limit"
ACTION_BROADCAST = "broadcast"
ACTION_ADD_CHANNEL = "add_channel"
ACTION_REMOVE_CHANNEL = "remove_channel"
ACTION_UPDATE_SETTING = "update_setting"
ACTION_DOWNLOAD_FILE = "download_file"
ACTION_VERIFICATION_SUCCESS = "verification_success"
ACTION_VERIFICATION_FAILED = "verification_failed"
ACTION_BYPASS_DETECTED = "bypass_detected"


# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_INVALID_FILE_TYPE = "Invalid file type. Only ZIP files are allowed."
ERROR_FILE_TOO_LARGE = "File too large. Maximum size is {max_size}GB."
ERROR_POST_NUMBER_EXISTS = "Post number already exists."
ERROR_INVALID_POST_NUMBER = "Invalid post number."
ERROR_FILE_NOT_FOUND = "File not found."
ERROR_USER_NOT_FOUND = "User not found."
ERROR_CHANNEL_NOT_FOUND = "Channel not found."
ERROR_INVALID_USER_ID = "Invalid user ID."
ERROR_INVALID_HOURS = "Invalid hours. Must be between {min} and {max}."
ERROR_DATABASE_ERROR = "Database error occurred."
ERROR_PERMISSION_DENIED = "Permission denied. Admin only."
ERROR_NOT_SUBSCRIBED = "You must subscribe to all channels first."
ERROR_NOT_VERIFIED = "You need to verify first."
ERROR_LIMIT_REACHED = "You have reached your daily file limit."
ERROR_TOKEN_INVALID = "Invalid or expired token."
ERROR_UNKNOWN = "An unknown error occurred."


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_FILE_UPLOADED = "File uploaded successfully!"
SUCCESS_FILE_DELETED = "File deleted successfully!"
SUCCESS_USER_VERIFIED = "User verified successfully!"
SUCCESS_USER_UNVERIFIED = "User unverified successfully!"
SUCCESS_LIMIT_RESET = "File limit reset successfully!"
SUCCESS_BROADCAST_SENT = "Broadcast sent successfully!"
SUCCESS_CHANNEL_ADDED = "Channel added successfully!"
SUCCESS_CHANNEL_REMOVED = "Channel removed successfully!"
SUCCESS_SETTING_UPDATED = "Setting updated successfully!"


# ============================================================================
# REGEX PATTERNS
# ============================================================================

TELEGRAM_LINK_PATTERN = r'^https://t\.me/'
CHANNEL_ID_PATTERN = r'^-100\d{10,}$'
USERNAME_PATTERN = r'^@?[a-zA-Z0-9_]{5,32}$'


# ============================================================================
# DEEP LINK PREFIXES
# ============================================================================

DEEP_LINK_PREFIX_GET = "get-"
DEEP_LINK_PREFIX_VERIFY = "verify-"


# ============================================================================
# COLLECTION NAMES (reference)
# ============================================================================

COLLECTION_FILES = "files"
COLLECTION_USERS = "users_verification"
COLLECTION_TOKENS = "verification_tokens"
COLLECTION_CHANNELS = "force_sub_channels"
COLLECTION_SETTINGS = "admin_settings"
COLLECTION_LOGS = "admin_logs"


# ============================================================================
# CACHE KEYS (if caching is implemented)
# ============================================================================

CACHE_PREFIX_USER = "user:"
CACHE_PREFIX_FILE = "file:"
CACHE_PREFIX_TOKEN = "token:"
CACHE_PREFIX_CHANNEL = "channel:"
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour


# ============================================================================
# HTTP STATUS CODES (for verification server)
# ============================================================================

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_ERROR = 500


# ============================================================================
# EXPORT ALL
# ============================================================================

__all__ = [
    # Bot Info
    'ADMIN_BOT_NAME',
    'USER_BOT_NAME',
    'SYSTEM_NAME',
    'VERSION',
    
    # Status
    'STATUS_PENDING',
    'STATUS_IN_PROGRESS',
    'STATUS_COMPLETED',
    'STATUS_EXPIRED',
    
    # Verification
    'DEFAULT_VERIFICATION_HOURS',
    'DEFAULT_FILE_ACCESS_LIMIT',
    'MIN_VERIFICATION_HOURS',
    'MAX_VERIFICATION_HOURS',
    
    # File Settings
    'MAX_FILE_SIZE_GB',
    'MAX_FILE_SIZE_BYTES',
    'ALLOWED_FILE_EXTENSIONS',
    'DEFAULT_FILE_PASSWORD',
    
    # Time Constants
    'AUTO_DELETE_MINUTES',
    'AUTO_DELETE_SECONDS',
    'TOKEN_EXPIRY_SECONDS',
    'VERIFICATION_COUNTDOWN_SECONDS',
    'BROADCAST_DELAY_SECONDS',
    
    # Limits
    'MAX_BROADCAST_USERS',
    'MAX_CHANNELS_PER_BOT',
    'MAX_POST_NUMBER',
    'MIN_POST_NUMBER',
    'MAX_BUTTON_TEXT_LENGTH',
    'MAX_CONTEXT_LENGTH',
    'MAX_EXTRA_MESSAGE_LENGTH',
    'MIN_PASSWORD_LENGTH',
    'MAX_PASSWORD_LENGTH',
    
    # Emojis
    'EMOJI_SUCCESS',
    'EMOJI_ERROR',
    'EMOJI_WARNING',
    'EMOJI_INFO',
    'EMOJI_FILE',
    'EMOJI_VERIFIED',
    'EMOJI_UNVERIFIED',
    'EMOJI_DOWNLOAD',
    'EMOJI_UPLOAD',
    'EMOJI_BROADCAST',
    'EMOJI_STATS',
    'EMOJI_SETTINGS',
    'EMOJI_CHANNEL',
    'EMOJI_USER',
    'EMOJI_ADMIN',
    'EMOJI_TIME',
    'EMOJI_EXPIRED',
    'EMOJI_PENDING',
    'EMOJI_LOCK',
    'EMOJI_FIRE',
    'EMOJI_CHECK',
    'EMOJI_CROSS',
    'EMOJI_SKULL',
    'EMOJI_ALERT',
    'EMOJI_REFRESH',
    'EMOJI_BACK',
    'EMOJI_CLOSE',
    'EMOJI_MENU',
    
    # Templates
    'POST_TEMPLATE',
    'FORCE_SUB_TEMPLATE',
    'VERIFICATION_TEMPLATE',
    'VERIFIED_SUCCESS_TEMPLATE',
    'BYPASS_DETECTED_TEMPLATE',
    'ALREADY_VERIFIED_TEMPLATE',
    'TOKEN_ERROR_TEMPLATE',
    'LIMIT_REACHED_TEMPLATE',
    'FILE_DELETED_TEMPLATE',
    'AUTO_DELETE_WARNING',
    
    # Buttons
    'BUTTON_DOWNLOAD',
    'BUTTON_VERIFY_NOW',
    'BUTTON_HOW_TO_VERIFY',
    'BUTTON_TRY_AGAIN',
    'BUTTON_CLICK_HERE',
    'BUTTON_CLOSE',
    'BUTTON_BACK',
    'BUTTON_CANCEL',
    'BUTTON_CONFIRM',
    
    # Actions
    'ACTION_START_BOT',
    'ACTION_UPLOAD_FILE',
    'ACTION_DELETE_FILE',
    'ACTION_VERIFY_USER',
    'ACTION_UNVERIFY_USER',
    'ACTION_RESET_LIMIT',
    'ACTION_BROADCAST',
    'ACTION_ADD_CHANNEL',
    'ACTION_REMOVE_CHANNEL',
    'ACTION_UPDATE_SETTING',
    'ACTION_DOWNLOAD_FILE',
    'ACTION_VERIFICATION_SUCCESS',
    'ACTION_VERIFICATION_FAILED',
    'ACTION_BYPASS_DETECTED',
    
    # Error Messages
    'ERROR_INVALID_FILE_TYPE',
    'ERROR_FILE_TOO_LARGE',
    'ERROR_POST_NUMBER_EXISTS',
    'ERROR_INVALID_POST_NUMBER',
    'ERROR_FILE_NOT_FOUND',
    'ERROR_USER_NOT_FOUND',
    'ERROR_CHANNEL_NOT_FOUND',
    'ERROR_INVALID_USER_ID',
    'ERROR_INVALID_HOURS',
    'ERROR_DATABASE_ERROR',
    'ERROR_PERMISSION_DENIED',
    'ERROR_NOT_SUBSCRIBED',
    'ERROR_NOT_VERIFIED',
    'ERROR_LIMIT_REACHED',
    'ERROR_TOKEN_INVALID',
    'ERROR_UNKNOWN',
    
    # Success Messages
    'SUCCESS_FILE_UPLOADED',
    'SUCCESS_FILE_DELETED',
    'SUCCESS_USER_VERIFIED',
    'SUCCESS_USER_UNVERIFIED',
    'SUCCESS_LIMIT_RESET',
    'SUCCESS_BROADCAST_SENT',
    'SUCCESS_CHANNEL_ADDED',
    'SUCCESS_CHANNEL_REMOVED',
    'SUCCESS_SETTING_UPDATED',
    
    # Patterns
    'TELEGRAM_LINK_PATTERN',
    'CHANNEL_ID_PATTERN',
    'USERNAME_PATTERN',
    
    # Deep Links
    'DEEP_LINK_PREFIX_GET',
    'DEEP_LINK_PREFIX_VERIFY',
    
    # Collections
    'COLLECTION_FILES',
    'COLLECTION_USERS',
    'COLLECTION_TOKENS',
    'COLLECTION_CHANNELS',
    'COLLECTION_SETTINGS',
    'COLLECTION_LOGS',
    
    # Cache
    'CACHE_PREFIX_USER',
    'CACHE_PREFIX_FILE',
    'CACHE_PREFIX_TOKEN',
    'CACHE_PREFIX_CHANNEL',
    'CACHE_TTL_SHORT',
    'CACHE_TTL_MEDIUM',
    'CACHE_TTL_LONG',
    
    # HTTP
    'HTTP_OK',
    'HTTP_BAD_REQUEST',
    'HTTP_UNAUTHORIZED',
    'HTTP_FORBIDDEN',
    'HTTP_NOT_FOUND',
    'HTTP_TOO_MANY_REQUESTS',
    'HTTP_INTERNAL_ERROR',
]