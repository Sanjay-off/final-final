"""
Bypass Detection Utilities
Implements security checks to detect verification bypass attempts.
"""

import logging
from datetime import datetime
from typing import Tuple, Dict, Any

from database.operations.verification import get_verification_token

logger = logging.getLogger(__name__)


async def detect_bypass_attempt(token_id: str, user_id: int) -> Tuple[bool, str]:
    """
    Detect if user is attempting to bypass verification.
    
    Args:
        token_id: Token ID to check
        user_id: User's Telegram ID
    
    Returns:
        Tuple of (is_bypass: bool, reason: str)
    """
    try:
        # Get token record
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return True, "token_not_found"
        
        # Check 1: Token belongs to user
        if token_record['user_id'] != user_id:
            logger.warning(f"Token user mismatch: token user {token_record['user_id']}, request user {user_id}")
            return True, "user_mismatch"
        
        # Check 2: Token not expired
        if token_record['expires_at'] < datetime.now():
            logger.warning(f"Expired token used: {token_id}")
            return True, "token_expired"
        
        # Check 3: Token not already completed
        if token_record['status'] == 'completed':
            logger.warning(f"Reused token detected: {token_id}")
            return True, "token_reused"
        
        # Check 4: Token timing (bypass detection)
        timing_check, timing_reason = await check_token_timing(token_record)
        if not timing_check:
            return True, timing_reason
        
        # Check 5: Token state validation
        state_check, state_reason = await validate_token_state(token_record)
        if not state_check:
            return True, state_reason
        
        # All checks passed
        return False, "valid"
    
    except Exception as e:
        logger.error(f"Error in bypass detection: {e}", exc_info=True)
        return True, "error"


async def check_token_timing(token_record: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check token timing to detect bypass attempts.
    
    Args:
        token_record: Token record from database
    
    Returns:
        Tuple of (is_valid: bool, reason: str)
    """
    try:
        created_at = token_record['created_at']
        now = datetime.now()
        
        # Calculate time elapsed
        time_elapsed = (now - created_at).total_seconds()
        
        # Check 1: Too fast (less than 5 seconds - likely bypass)
        if time_elapsed < 5:
            logger.warning(f"Token verification too fast: {time_elapsed}s")
            return False, "too_fast"
        
        # Check 2: Token must be in 'in_progress' state for at least 3 seconds
        # (user must have loaded the verification page)
        updated_at = token_record.get('updated_at')
        if updated_at:
            state_time = (now - updated_at).total_seconds()
            if state_time < 3:
                logger.warning(f"Token state changed too quickly: {state_time}s")
                return False, "state_change_too_fast"
        
        return True, "valid_timing"
    
    except Exception as e:
        logger.error(f"Error checking token timing: {e}")
        return False, "timing_check_error"


async def validate_token_state(token_record: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate token state is correct for verification.
    
    Args:
        token_record: Token record from database
    
    Returns:
        Tuple of (is_valid: bool, reason: str)
    """
    try:
        status = token_record['status']
        
        # Token must be in 'in_progress' state
        # This means user loaded the verification page
        if status != 'in_progress':
            logger.warning(f"Invalid token state for verification: {status}")
            return False, f"invalid_state_{status}"
        
        return True, "valid_state"
    
    except Exception as e:
        logger.error(f"Error validating token state: {e}")
        return False, "state_validation_error"


async def is_suspicious_activity(
    user_id: int,
    token_id: str,
    request_info: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Check for suspicious activity patterns.
    
    Args:
        user_id: User's Telegram ID
        token_id: Token ID
        request_info: Request information (IP, user agent, etc.)
    
    Returns:
        Tuple of (is_suspicious: bool, reason: str)
    """
    try:
        # Check 1: Multiple rapid requests from same user
        # This would require session/cache tracking
        # Placeholder for future implementation
        
        # Check 2: Unusual request patterns
        # Could check user agent, referrer, etc.
        # Placeholder for future implementation
        
        # For now, return not suspicious
        return False, "no_suspicious_activity"
    
    except Exception as e:
        logger.error(f"Error checking suspicious activity: {e}")
        return False, "activity_check_error"


def calculate_bypass_score(checks: Dict[str, bool]) -> float:
    """
    Calculate bypass probability score based on various checks.
    
    Args:
        checks: Dictionary of check results
    
    Returns:
        Bypass probability score (0.0 to 1.0)
    """
    try:
        failed_checks = sum(1 for passed in checks.values() if not passed)
        total_checks = len(checks)
        
        if total_checks == 0:
            return 0.0
        
        return failed_checks / total_checks
    
    except Exception as e:
        logger.error(f"Error calculating bypass score: {e}")
        return 1.0  # Assume bypass on error


async def log_bypass_attempt(
    user_id: int,
    token_id: str,
    reason: str,
    additional_info: Dict[str, Any] = None
) -> None:
    """
    Log bypass attempt for security monitoring.
    
    Args:
        user_id: User's Telegram ID
        token_id: Token ID
        reason: Bypass detection reason
        additional_info: Additional context information
    """
    try:
        log_data = {
            'user_id': user_id,
            'token_id': token_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'additional_info': additional_info or {}
        }
        
        logger.warning(f"Bypass attempt detected: {log_data}")
        
        # Could store in database for analysis
        # await store_security_log(log_data)
    
    except Exception as e:
        logger.error(f"Error logging bypass attempt: {e}")


async def get_bypass_statistics(user_id: int = None) -> Dict[str, Any]:
    """
    Get bypass attempt statistics.
    
    Args:
        user_id: Optional user ID to filter by
    
    Returns:
        Dictionary with bypass statistics
    """
    try:
        # Placeholder for future implementation
        # Would query security logs from database
        
        return {
            'total_attempts': 0,
            'by_reason': {},
            'by_user': {}
        }
    
    except Exception as e:
        logger.error(f"Error getting bypass statistics: {e}")
        return {}