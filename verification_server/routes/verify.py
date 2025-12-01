"""
Verification Routes for Verification Server
Handles user verification flow and token validation.
"""

import logging
from flask import Blueprint, request, render_template, redirect
from datetime import datetime

from database.operations.verification import (
    get_verification_token,
    mark_token_completed
)
from database.operations.users import verify_user_manually
from shared.encryption import decode_url_safe, encode_url_safe
from shared.utils import build_deep_link
from config.settings import USER_BOT_USERNAME, VERIFICATION_PERIOD_HOURS

logger = logging.getLogger(__name__)

# Create blueprint
verify_routes = Blueprint('verify', __name__)


@verify_routes.route('/verify', methods=['GET'])
async def verification_page():
    """
    Display verification countdown page.
    
    Query params:
        token: Encrypted verification token
    
    Returns:
        HTML verification page with countdown
    """
    try:
        # Get encrypted token from query params
        encrypted_token = request.args.get('token')
        
        if not encrypted_token:
            logger.warning("Verification page accessed without token")
            return render_template('error.html',
                                 error_message="Invalid verification link. Token missing."), 400
        
        # Decode token
        try:
            token_id = decode_url_safe(encrypted_token)
        except Exception as e:
            logger.error(f"Token decode error: {e}")
            return render_template('error.html',
                                 error_message="Invalid token format."), 400
        
        # Get token from database
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            logger.warning(f"Token not found: {token_id}")
            return render_template('error.html',
                                 error_message="Token not found or expired."), 404
        
        # Check if token is expired
        if token_record['expires_at'] < datetime.now():
            logger.warning(f"Token expired: {token_id}")
            return render_template('error.html',
                                 error_message="Verification link has expired. Please request a new one."), 410
        
        # Check if token already completed
        if token_record['status'] == 'completed':
            logger.warning(f"Token already used: {token_id}")
            return render_template('error.html',
                                 error_message="This verification link has already been used."), 410
        
        # Check if token is in correct state
        if token_record['status'] != 'in_progress':
            logger.warning(f"Token not in progress state: {token_id}, status: {token_record['status']}")
            return render_template('error.html',
                                 error_message="Invalid verification state. Please try again."), 400
        
        # Generate redirect URL to bot
        user_id = token_record['user_id']
        deep_link_data = f"verify-{token_id}"
        encoded_data = encode_url_safe(deep_link_data)
        redirect_url = build_deep_link(USER_BOT_USERNAME, encoded_data)
        
        logger.info(f"Displaying verification page for user {user_id}, token: {token_id}")
        
        # Render verification page with countdown
        return render_template('verify.html',
                             redirect_url=redirect_url,
                             countdown_seconds=5)
    
    except Exception as e:
        logger.error(f"Error in verification page: {e}", exc_info=True)
        return render_template('error.html',
                             error_message="An error occurred. Please try again."), 500


@verify_routes.route('/complete', methods=['POST'])
async def complete_verification():
    """
    Complete verification (called by bot after validation).
    
    JSON body:
        token_id: Token ID to complete
        user_id: User ID for validation
    
    Returns:
        JSON response with completion status
    """
    try:
        data = request.get_json()
        
        if not data:
            return {'status': 'error', 'message': 'No data provided'}, 400
        
        token_id = data.get('token_id')
        user_id = data.get('user_id')
        
        if not token_id or not user_id:
            return {'status': 'error', 'message': 'Missing token_id or user_id'}, 400
        
        # Get token from database
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return {'status': 'error', 'message': 'Token not found'}, 404
        
        # Validate user_id matches
        if token_record['user_id'] != user_id:
            logger.warning(f"User ID mismatch for token {token_id}")
            return {'status': 'error', 'message': 'User ID mismatch'}, 403
        
        # Check if already completed
        if token_record['status'] == 'completed':
            return {'status': 'already_completed', 'message': 'Token already used'}, 200
        
        # Mark token as completed
        await mark_token_completed(token_id)
        
        # Verify user
        await verify_user_manually(
            user_id=user_id,
            hours=VERIFICATION_PERIOD_HOURS,
            verified_by=0  # 0 indicates automatic verification
        )
        
        logger.info(f"Completed verification for user {user_id}, token: {token_id}")
        
        return {
            'status': 'success',
            'message': 'Verification completed',
            'verified_until': datetime.now().isoformat()
        }, 200
    
    except Exception as e:
        logger.error(f"Error completing verification: {e}", exc_info=True)
        return {'status': 'error', 'message': 'Internal server error'}, 500


@verify_routes.route('/status', methods=['GET'])
async def check_status():
    """
    Check verification status for a token.
    
    Query params:
        token: Token ID
    
    Returns:
        JSON response with token status
    """
    try:
        token_id = request.args.get('token')
        
        if not token_id:
            return {'status': 'error', 'message': 'Token required'}, 400
        
        # Try to decode if it's encrypted
        try:
            token_id = decode_url_safe(token_id)
        except:
            pass  # Already decoded or plain token
        
        token_record = await get_verification_token(token_id)
        
        if not token_record:
            return {'status': 'not_found'}, 404
        
        is_expired = token_record['expires_at'] < datetime.now()
        
        return {
            'status': 'found',
            'token_status': token_record['status'],
            'is_expired': is_expired,
            'created_at': token_record['created_at'].isoformat(),
            'expires_at': token_record['expires_at'].isoformat()
        }, 200
    
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return {'status': 'error', 'message': str(e)}, 500