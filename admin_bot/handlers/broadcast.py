"""
Broadcast Handler for Admin Bot
Handles broadcasting messages to users with different filters.
"""

import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from telegram.constants import ParseMode

from database.operations.users import get_all_users, get_verified_users, get_active_users
from admin_bot.middleware.auth import admin_only

# Conversation states
BROADCAST_TYPE, BROADCAST_MESSAGE = range(2)


@admin_only
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start broadcast conversation - show broadcast type selection."""
    keyboard = [
        [InlineKeyboardButton("📨 Broadcast to All Users", callback_data="broadcast_all")],
        [InlineKeyboardButton("✅ Broadcast to Verified Users", callback_data="broadcast_verified")],
        [InlineKeyboardButton("🔥 Broadcast to Active Users (Last 7 Days)", callback_data="broadcast_active")],
        [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📢 *Broadcast Message*\n\n"
        "Select the type of broadcast you want to send:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return BROADCAST_TYPE


async def broadcast_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast type selection."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "broadcast_cancel":
        await query.edit_message_text("❌ Broadcast cancelled.")
        return ConversationHandler.END
    
    # Store broadcast type
    context.user_data['broadcast_type'] = query.data
    
    type_names = {
        'broadcast_all': 'All Users',
        'broadcast_verified': 'Verified Users Only',
        'broadcast_active': 'Active Users (Last 7 Days)'
    }
    
    await query.edit_message_text(
        f"📝 *Broadcast Type:* {type_names.get(query.data)}\n\n"
        "Now send me the message you want to broadcast.\n\n"
        "💡 You can send:\n"
        "• Text messages\n"
        "• Messages with images\n"
        "• Messages with videos\n"
        "• Messages with documents\n"
        "• Messages with formatting (Markdown/HTML)\n\n"
        "Send /cancel to cancel the broadcast.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return BROADCAST_MESSAGE


async def broadcast_message_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the broadcast message and start sending."""
    broadcast_type = context.user_data.get('broadcast_type')
    
    if not broadcast_type:
        await update.message.reply_text("❌ Error: Broadcast type not found. Please start again with /broadcast")
        return ConversationHandler.END
    
    # Show confirmation
    keyboard = [
        [InlineKeyboardButton("✅ Confirm & Send", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Store message details
    context.user_data['broadcast_message'] = update.message
    
    type_names = {
        'broadcast_all': 'All Users',
        'broadcast_verified': 'Verified Users Only',
        'broadcast_active': 'Active Users (Last 7 Days)'
    }
    
    await update.message.reply_text(
        f"📢 *Broadcast Preview*\n\n"
        f"*Type:* {type_names.get(broadcast_type)}\n"
        f"*Message Type:* {update.message.effective_attachment or 'Text'}\n\n"
        "⚠️ This message will be sent to users. Confirm?",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return BROADCAST_TYPE


async def broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and execute broadcast."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "broadcast_cancel":
        await query.edit_message_text("❌ Broadcast cancelled.")
        context.user_data.clear()
        return ConversationHandler.END
    
    broadcast_type = context.user_data.get('broadcast_type')
    broadcast_message = context.user_data.get('broadcast_message')
    
    if not broadcast_type or not broadcast_message:
        await query.edit_message_text("❌ Error: Missing broadcast data. Please start again.")
        return ConversationHandler.END
    
    # Get users based on type
    if broadcast_type == 'broadcast_all':
        users = await get_all_users()
        type_name = "All Users"
    elif broadcast_type == 'broadcast_verified':
        users = await get_verified_users()
        type_name = "Verified Users"
    elif broadcast_type == 'broadcast_active':
        since_date = datetime.now() - timedelta(days=7)
        users = await get_active_users(since_date)
        type_name = "Active Users (Last 7 Days)"
    else:
        await query.edit_message_text("❌ Invalid broadcast type.")
        return ConversationHandler.END
    
    total_users = len(users)
    
    if total_users == 0:
        await query.edit_message_text(f"⚠️ No users found in category: {type_name}")
        return ConversationHandler.END
    
    # Start broadcasting
    status_message = await query.edit_message_text(
        f"📤 *Broadcasting to {type_name}*\n\n"
        f"Total Users: {total_users}\n"
        f"Progress: 0/{total_users}\n"
        f"Success: 0\n"
        f"Failed: 0\n\n"
        f"⏳ Please wait...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    success_count = 0
    failed_count = 0
    blocked_count = 0
    
    # Broadcast to users
    for index, user in enumerate(users, 1):
        try:
            # Copy message to user
            await broadcast_message.copy(chat_id=user['user_id'])
            success_count += 1
            
        except Exception as e:
            error_str = str(e).lower()
            if 'blocked' in error_str or 'user is deactivated' in error_str:
                blocked_count += 1
            failed_count += 1
        
        # Update progress every 10 users or on last user
        if index % 10 == 0 or index == total_users:
            try:
                await status_message.edit_text(
                    f"📤 *Broadcasting to {type_name}*\n\n"
                    f"Total Users: {total_users}\n"
                    f"Progress: {index}/{total_users}\n"
                    f"✅ Success: {success_count}\n"
                    f"❌ Failed: {failed_count}\n"
                    f"🚫 Blocked: {blocked_count}\n\n"
                    f"{'⏳ In progress...' if index < total_users else '✅ Completed!'}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass  # Ignore edit errors
        
        # Small delay to avoid rate limits
        await asyncio.sleep(0.05)
    
    # Final summary
    await status_message.edit_text(
        f"✅ *Broadcast Completed!*\n\n"
        f"*Type:* {type_name}\n"
        f"*Total Users:* {total_users}\n"
        f"*Successfully Sent:* {success_count}\n"
        f"*Failed:* {failed_count}\n"
        f"*Blocked Bot:* {blocked_count}\n\n"
        f"*Success Rate:* {(success_count/total_users*100):.1f}%",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel broadcast conversation."""
    context.user_data.clear()
    await update.message.reply_text("❌ Broadcast cancelled.")
    return ConversationHandler.END


# Create conversation handler
broadcast_handler = ConversationHandler(
    entry_points=[CommandHandler('broadcast', broadcast_command)],
    states={
        BROADCAST_TYPE: [
            CallbackQueryHandler(broadcast_type_selection, pattern='^broadcast_'),
            CallbackQueryHandler(broadcast_confirm, pattern='^broadcast_confirm$')
        ],
        BROADCAST_MESSAGE: [
            MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_message_received),
            CallbackQueryHandler(broadcast_confirm, pattern='^broadcast_confirm$'),
            CallbackQueryHandler(broadcast_type_selection, pattern='^broadcast_cancel$')
        ]
    },
    fallbacks=[CommandHandler('cancel', broadcast_cancel)],
    name="broadcast_conversation",
    persistent=False
)