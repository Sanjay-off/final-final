"""
Download Handler for User Bot
Handles file download requests and delivery.
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database.operations import (
    get_file_by_post_no,
    get_user_by_id,
    increment_download_count,
    increment_user_file_access
)
from user_bot.utils.force_sub import check_force_subscribe
from user_bot.utils.verification import check_user_verification
from config.settings import PRIVATE_STORAGE_CHANNEL_ID
from shared.constants import (
    BUTTON_CLICK_HERE,
    BUTTON_CLOSE,
    AUTO_DELETE_WARNING,
    FILE_DELETED_TEMPLATE,
    LIMIT_REACHED_TEMPLATE
)

logger = logging.getLogger(__name__)


async def send_file_to_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    post_no: int
):
    """Send file to user with auto-delete."""
    user_id = update.effective_user.id
    
    file_record = await get_file_by_post_no(post_no)
    if not file_record:
        await update.message.reply_text("❌ File not found.")
        return
    
    user = await get_user_by_id(user_id)
    if not user:
        await update.message.reply_text("❌ User record not found.")
        return
    
    files_accessed = user.get('files_accessed_count', 0)
    if files_accessed >= 3:
        await show_limit_reached(update, context)
        return
    
    try:
        file_caption = f"password - {file_record['password']}"
        
        file_msg = await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=PRIVATE_STORAGE_CHANNEL_ID,
            message_id=file_record['storage_message_id'],
            caption=file_caption
        )
        
        warning_msg = await update.message.reply_text(
            AUTO_DELETE_WARNING.format(minutes=10),
            parse_mode=ParseMode.MARKDOWN
        )
        
        await increment_download_count(post_no)
        await increment_user_file_access(user_id, post_no)
        
        await asyncio.sleep(600)
        
        try:
            await file_msg.delete()
            await warning_msg.delete()
            
            await send_deleted_message(update, context, post_no)
        except Exception as e:
            logger.error(f"Error deleting messages: {e}")
    
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await update.message.reply_text("❌ Error sending file.")


async def send_deleted_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    post_no: int
):
    """Send message after file deletion."""
    from shared.utils import build_deep_link
    from shared.encryption import encode_url_safe
    from config.settings import USER_BOT_USERNAME
    
    deep_link_data = f"get-{post_no}"
    encoded_data = encode_url_safe(deep_link_data)
    deep_link = build_deep_link(USER_BOT_USERNAME, encoded_data)
    
    keyboard = [
        [InlineKeyboardButton(BUTTON_CLICK_HERE, url=deep_link)],
        [InlineKeyboardButton(BUTTON_CLOSE, callback_data="close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=FILE_DELETED_TEMPLATE,
        reply_markup=reply_markup
    )


async def show_limit_reached(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """Show limit reached message with verification option."""
    from user_bot.keyboards.inline import verification_keyboard
    
    message = LIMIT_REACHED_TEMPLATE.format(limit=3)
    keyboard = verification_keyboard()
    
    await update.message.reply_text(
        message,
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_download_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    post_no: int
):
    """Handle download request with all checks."""
    user_id = update.effective_user.id
    
    force_sub_passed = await check_force_subscribe(update, context)
    if not force_sub_passed:
        return
    
    verification_passed = await check_user_verification(update, context)
    if not verification_passed:
        return
    
    await send_file_to_user(update, context, post_no)


download_handler = []