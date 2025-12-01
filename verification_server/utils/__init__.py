"""
Verification Server Utils Package
Contains utility functions for token validation and bypass detection.
"""

from .token import (
    validate_verification_token,
    decode_token_from_request,
    encode_token_for_response,
)

from .bypass_check import (
    detect_bypass_attempt,
    check_token_timing,
    validate_token_state,
    is_suspicious_activity,
)

__all__ = [
    # Token utilities
    'validate_verification_token',
    'decode_token_from_request',
    'encode_token_for_response',
    
    # Bypass detection
    'detect_bypass_attempt',
    'check_token_timing',
    'validate_token_state',
    'is_suspicious_activity',
]