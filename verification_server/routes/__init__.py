"""
Verification Server Routes Package
Contains all route handlers for the verification server.
"""

from .verify import verify_routes
from .shortlink import shortlink_routes

__all__ = [
    'verify_routes',
    'shortlink_routes',
]