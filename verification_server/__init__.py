"""
Verification Server Package
Web server for handling user verification flow with bypass detection.
"""

__version__ = "1.0.0"
__author__ = "Verification Server System"
__description__ = "Telegram verification server with bypass detection"

# Package metadata
SERVER_NAME = "Verification Server"
SERVER_VERSION = __version__

# Import main app components
from .app import create_app, run_server

__all__ = [
    'create_app',
    'run_server',
    '__version__',
    'SERVER_NAME',
    'SERVER_VERSION',
]