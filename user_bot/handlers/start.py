"""
Start Handler for User Bot
Handles /start command and deep link parameters.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from database.operations import create_user, get_user_by_id
from shared.encryption import decode_url_safe
from user_bot.handlers.download import handle_download_request
from user_bot.handlers.verification import handle_verification_callback

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with deep link support."""
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    
    existing_user = await get_user_by_id(user_id)
    if not existing_user:
        await create_user(
            user_id=user_id,
            username=username,
            first_name=first_name
        )
    
    if context.args:
        await handle_deep_link(update, context, context.args[0])
    else:
        await send_welcome_message(update, context)


async def handle_deep_link(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    parameter: str
):
    """Handle deep link parameters."""
    try:
        decoded = decode_url_safe(parameter)
        
        if decoded.startswith('get-'):
            post_no = int(decoded.split('-', 1)[1])
            await handle_download_request(update, context, post_no)
        
        elif decoded.startswith('verify-'):
            token_id = decoded.split('-', 1)[1]
            await handle_verification_callback(update, context, token_id)
        
        else:
            logger.warning(f"Unknown deep link format: {decoded}")
            await send_welcome_message(update, context)
    
    except Exception as e:
        logger.error(f"Error handling deep link: {e}")
        await update.message.reply_text("❌ Invalid link.")


async def send_welcome_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """Send welcome message to user."""
    welcome_text = (
        "👋 *Welcome!*\n\n"
        "This bot provides access to files.\n\n"
        "Click the download button on any post in our channel to get files.\n\n"
        "You'll need to:\n"
        "✅ Subscribe to required channels\n"
        "✅ Complete verification (free for 24 hours)\n"
        "✅ Access up to 3 files per verification period"
    )
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN
    )


start_handler = CommandHandler('start', start_command)