"""
Token Utilities for Verification Server
Handles token validation and processing for the verification server.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from shared.encryption import decode_url_safe, encode_url_safe
from database.operations.verification import (
    get_verification_token,
    is_token_valid
)

logger = logging.getLogger(__name__)


def decode_token_from_request(encrypted_token: str) -> Optional[str]:
    """
    Decode token from URL parameter.
    
    Args:
        encrypted_token: Encrypted token from URL
    
    Returns:
        Decoded token ID or None if error
    """
    try:
        token_id = decode_url_safe(encrypted_token)
        return token_id
    
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None


def encode_token_for_response(token_id: str) -> Optional[str]:
    """
    Encode token for URL/response.
    
    Args:
        token_id: Token ID to encode
    
    Returns:
        Encoded token or None if error
    """
    try:
        encoded = encode_url_safe(token_id)
        return encoded
    
    except Exception as e:
        logger.error(f"Error encoding token: {e}")
        return None


async def validate_verification_token(
    token_id: str,
    expected_user_id: int = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validate verification token comprehensively.
    
    Args:
        token_id: Token ID to validate
        expected_user_id: Expected user ID (optional)
    
    Returns:
        Tuple of (is_valid: bool, reason: str, token_data: dict or None)
    """
    try:
        # Get token from database
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return False, "token_not_found", None
        
        # Check expiry
        if token_record['expires_at'] < datetime.now():
            return False, "token_expired", token_record
        
        # Check status
        if token_record['status'] == 'completed':
            return False, "token_already_used", token_record
        
        # Check user ID if provided
        if expected_user_id and token_record['user_id'] != expected_user_id:
            return False, "user_mismatch", token_record
        
        # Token is valid
        return True, "valid", token_record
    
    except Exception as e:
        logger.error(f"Error validating token: {e}", exc_info=True)
        return False, "validation_error", None


async def get_token_metadata(token_id: str) -> Optional[Dict[str, Any]]:
    """
    Get token metadata without full validation.
    
    Args:
        token_id: Token ID
    
    Returns:
        Token metadata dictionary or None
    """
    try:
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return None
        
        time_elapsed = (datetime.now() - token_record['created_at']).total_seconds()
        time_remaining = (token_record['expires_at'] - datetime.now()).total_seconds()
        
        return {
            'token_id': token_record['token_id'],
            'user_id': token_record['user_id'],
            'status': token_record['status'],
            'created_at': token_record['created_at'].isoformat(),
            'expires_at': token_record['expires_at'].isoformat(),
            'time_elapsed': int(time_elapsed),
            'time_remaining': int(max(0, time_remaining)),
            'is_expired': time_remaining <= 0
        }
    
    except Exception as e:
        logger.error(f"Error getting token metadata: {e}")
        return None


def extract_token_from_url(url: str) -> Optional[str]:
    """
    Extract token parameter from URL.
    
    Args:
        url: Full URL string
    
    Returns:
        Token parameter value or None
    """
    try:
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        token = params.get('token', [None])[0]
        return token
    
    except Exception as e:
        logger.error(f"Error extracting token from URL: {e}")
        return None


async def check_token_eligibility(token_id: str) -> Tuple[bool, str]:
    """
    Check if token is eligible for verification completion.
    
    Args:
        token_id: Token ID
    
    Returns:
        Tuple of (is_eligible: bool, reason: str)
    """
    try:
        is_valid = await is_token_valid(token_id)
        
        if not is_valid:
            token_record = await get_verification_token(token_id)
            
            if not token_record:
                return False, "token_not_found"
            
            if token_record['expires_at'] < datetime.now():
                return False, "token_expired"
            
            if token_record['status'] == 'completed':
                return False, "already_completed"
            
            if token_record['status'] != 'in_progress':
                return False, f"invalid_status_{token_record['status']}"
            
            return False, "validation_failed"
        
        return True, "eligible"
    
    except Exception as e:
        logger.error(f"Error checking token eligibility: {e}")
        return False, "check_error"


def sanitize_token_input(token_input: str) -> Optional[str]:
    """
    Sanitize token input from user.
    
    Args:
        token_input: Raw token input
    
    Returns:
        Sanitized token or None if invalid
    """
    try:
        if not token_input:
            return None
        
        # Remove whitespace
        token = token_input.strip()
        
        # Basic validation
        if len(token) < 10 or len(token) > 500:
            return None
        
        # Remove potentially malicious characters
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_=')
        if not all(c in allowed_chars for c in token):
            return None
        
        return token
    
    except Exception as e:
        logger.error(f"Error sanitizing token: {e}")
        return None