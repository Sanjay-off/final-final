"""
Admin Bot Package
Main package for the Telegram admin bot that handles file uploads,
user management, broadcasting, and system configuration.
"""

__version__ = "1.0.0"
__author__ = "Admin Bot System"
__description__ = "Telegram file distribution system - Admin bot"

# Package metadata
ADMIN_BOT_NAME = "Admin Bot"
ADMIN_BOT_VERSION = __version__

# Import main bot components for easy access
from .bot import start_admin_bot, stop_admin_bot, get_admin_application

__all__ = [
    'start_admin_bot',
    'stop_admin_bot', 
    'get_admin_application',
    '__version__',
    'ADMIN_BOT_NAME',
    'ADMIN_BOT_VERSION',
]