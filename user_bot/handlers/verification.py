"""
Verification Handler for User Bot
Handles verification flow and token validation.
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from database.operations import (
    get_verification_token,
    mark_token_completed,
    verify_user_manually,
    get_user_by_id,
    create_verification_token,
    mark_token_in_progress
)
from user_bot.keyboards.inline import verification_keyboard
from shared.constants import (
    VERIFICATION_TEMPLATE,
    VERIFIED_SUCCESS_TEMPLATE,
    BYPASS_DETECTED_TEMPLATE,
    ALREADY_VERIFIED_TEMPLATE,
    TOKEN_ERROR_TEMPLATE,
    BUTTON_VERIFY_NOW,
    BUTTON_HOW_TO_VERIFY
)
from shared.encryption import generate_verification_token, encode_url_safe
from shared.utils import build_deep_link
from config.settings import (
    USER_BOT_USERNAME,
    VERIFICATION_TOKEN_EXPIRY,
    VERIFICATION_PERIOD_HOURS
)
from database.operations.settings import get_setting_value

logger = logging.getLogger(__name__)


async def show_verification_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """Show verification screen with buttons."""
    user = update.effective_user
    username = user.first_name or user.username or "User"
    
    message = VERIFICATION_TEMPLATE.format(username=username)
    keyboard = verification_keyboard()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_verify_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle verify now button."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    user = await get_user_by_id(user_id)
    if user and user.get('is_verified'):
        expires_at = user.get('expires_at')
        if expires_at and expires_at > datetime.now():
            await query.edit_message_text(
                ALREADY_VERIFIED_TEMPLATE,
                parse_mode=ParseMode.MARKDOWN
            )
            return
    
    token_id = generate_verification_token()
    
    await create_verification_token(
        token_id=token_id,
        user_id=user_id,
        expiry_seconds=VERIFICATION_TOKEN_EXPIRY
    )
    
    # Get shortlink API credentials from settings
    shortlink_api = await get_setting_value('shortlink_api_key')
    shortlink_base = await get_setting_value('shortlink_base_url')
    
    if not shortlink_api or not shortlink_base:
        await query.edit_message_text("❌ Verification service not configured.")
        return
    
    verification_link = await generate_shortlink(token_id, user_id)
    
    if not verification_link:
        await query.edit_message_text("❌ Error generating verification link.")
        return
    
    keyboard = [[InlineKeyboardButton("🔗 Click to Verify", url=verification_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔐 *Verification Link Generated*\n\n"
        "Click the button below to verify:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def generate_shortlink(token_id: str, user_id: int) -> str:
    """Generate shortlink for verification."""
    import requests
    
    try:
        shortlink_api = await get_setting_value('shortlink_api_key')
        shortlink_base = await get_setting_value('shortlink_base_url')
        
        encoded_token = encode_url_safe(f"verify-{token_id}")
        destination_url = build_deep_link(USER_BOT_USERNAME, encoded_token)
        
        # Use appropriate API format based on base_url
        if 'just2earn.com' in shortlink_base:
            # Just2Earn API format: GET request
            response = requests.get(
                f"{shortlink_base}/api",
                params={
                    'api': shortlink_api,
                    'url': destination_url
                },
                timeout=10
            )
        elif 'get2short.com' in shortlink_base:
            # Get2Short API format: GET request
            response = requests.get(
                f"{shortlink_base}/api",
                params={
                    'api': shortlink_api,
                    'url': destination_url
                },
                timeout=10
            )
        else:
            # Legacy format: POST request
            response = requests.post(
                f"{shortlink_base}/api",
                json={
                    'url': destination_url,
                    'api': shortlink_api
                },
                timeout=10
            )
        
        if response.status_code == 200:
            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError:
                # If not JSON, try to extract URL from text response
                if response.text.startswith('http'):
                    return response.text
                return None
            
            # Handle different response formats
            shortlink = None
            
            # Check for common response field names
            for field in ['short_url', 'shorturl', 'short', 'link', 'url']:
                if field in data:
                    shortlink = data[field]
                    break
            
            # If still no shortlink, check if the response itself is the shortlink
            if not shortlink and isinstance(data, str) and data.startswith('http'):
                shortlink = data
            
            if shortlink and shortlink.startswith('http'):
                return shortlink
        
        return None
    
    except Exception as e:
        logger.error(f"Error generating shortlink: {e}")
        return None


async def handle_verification_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    token_id: str
):
    """Handle verification callback from deep link."""
    user_id = update.effective_user.id
    
    token = await get_verification_token(token_id)
    
    if not token:
        await update.message.reply_text(
            TOKEN_ERROR_TEMPLATE,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if token['user_id'] != user_id:
        await update.message.reply_text(
            TOKEN_ERROR_TEMPLATE,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if token['expires_at'] < datetime.now():
        await update.message.reply_text(
            TOKEN_ERROR_TEMPLATE,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if token['status'] == 'completed':
        await update.message.reply_text(
            TOKEN_ERROR_TEMPLATE,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if token['status'] != 'in_progress':
        await update.message.reply_text(
            BYPASS_DETECTED_TEMPLATE,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    time_elapsed = (datetime.now() - token['created_at']).total_seconds()
    if time_elapsed < 5:
        await update.message.reply_text(
            BYPASS_DETECTED_TEMPLATE,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await mark_token_completed(token_id)
    
    hours = await get_setting_value('verification_period_hours', default='24')
    await verify_user_manually(
        user_id=user_id,
        hours=int(hours),
        verified_by=0
    )
    
    await update.message.reply_text(
        VERIFIED_SUCCESS_TEMPLATE,
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_how_to_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle how to verify button."""
    query = update.callback_query
    await query.answer()
    
    how_to_verify_link = await get_setting_value('how_to_verify_link')
    
    if not how_to_verify_link:
        await query.answer("Tutorial link not configured.", show_alert=True)
        return
    
    keyboard = [[InlineKeyboardButton("📺 Watch Tutorial", url=how_to_verify_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📺 *How to Verify*\n\n"
        "Click the button below to watch the verification tutorial:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


verification_handler = [
    CallbackQueryHandler(handle_verify_now, pattern='^verify_now$'),
    CallbackQueryHandler(handle_how_to_verify, pattern='^how_to_verify$'),
]