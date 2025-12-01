"""
User Bot Package
Main package for the Telegram user bot that handles file distribution,
verification, and force subscribe checks.
"""

__version__ = "1.0.0"
__author__ = "User Bot System"
__description__ = "Telegram file distribution system - User bot"

# Package metadata
USER_BOT_NAME = "User Bot"
USER_BOT_VERSION = __version__

# Import main bot components for easy access
from .bot import start_user_bot, stop_user_bot, get_user_application

__all__ = [
    'start_user_bot',
    'stop_user_bot',
    'get_user_application',
    '__version__',
    'USER_BOT_NAME',
    'USER_BOT_VERSION',
]