"""
Callbacks Handler for User Bot
Handles inline button callbacks.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


async def close_message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle close button callback."""
    query = update.callback_query
    await query.answer()
    
    try:
        await query.message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")


async def generic_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle generic callbacks."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "close":
        try:
            await query.message.delete()
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
    else:
        logger.warning(f"Unhandled callback: {callback_data}")


callbacks_handler = [
    CallbackQueryHandler(close_message_callback, pattern='^close$'),
    CallbackQueryHandler(generic_callback_handler),
]