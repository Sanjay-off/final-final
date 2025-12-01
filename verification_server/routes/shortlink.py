"""
Shortlink Routes for Verification Server
Handles shortlink redirects and tracking.
"""

import logging
from flask import Blueprint, request, redirect, render_template
from datetime import datetime

from database.operations.verification import (
    get_verification_token,
    mark_token_in_progress
)
from shared.encryption import decode_url_safe

logger = logging.getLogger(__name__)

# Create blueprint
shortlink_routes = Blueprint('shortlink', __name__)


@shortlink_routes.route('/redirect', methods=['GET'])
async def handle_redirect():
    """
    Handle shortlink redirect with token tracking.
    
    Query params:
        token: Encrypted verification token
    
    Returns:
        Redirect to verification page or error
    """
    try:
        # Get encrypted token from query params
        encrypted_token = request.args.get('token')
        
        if not encrypted_token:
            logger.warning("Redirect request without token")
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
        
        # Mark token as in progress
        await mark_token_in_progress(token_id)
        
        # Redirect to verification page
        verification_url = f"/verify?token={encrypted_token}"
        
        logger.info(f"Redirecting to verification page for token: {token_id}")
        
        return redirect(verification_url)
    
    except Exception as e:
        logger.error(f"Error in redirect handler: {e}", exc_info=True)
        return render_template('error.html',
                             error_message="An error occurred. Please try again."), 500


@shortlink_routes.route('/track', methods=['POST'])
async def track_click():
    """
    Track shortlink click (optional analytics endpoint).
    
    Returns:
        JSON response with tracking status
    """
    try:
        data = request.get_json()
        token_id = data.get('token_id')
        
        if token_id:
            logger.info(f"Tracked click for token: {token_id}")
        
        return {'status': 'tracked'}, 200
    
    except Exception as e:
        logger.error(f"Error tracking click: {e}")
        return {'status': 'error', 'message': str(e)}, 500


@shortlink_routes.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSON response with server status
    """
    return {
        'status': 'healthy',
        'service': 'verification_server',
        'timestamp': datetime.now().isoformat()
    }, 200