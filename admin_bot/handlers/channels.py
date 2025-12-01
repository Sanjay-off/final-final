"""
Force Subscribe Channels Handler for Admin Bot
Handles adding, removing, listing, and managing force subscribe channels.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode

from database.operations.channels import (
    add_channel,
    remove_channel,
    get_all_channels,
    toggle_channel_status,
    update_channel,
    get_channel_by_id
)
from admin_bot.middleware.auth import admin_only

# Conversation states
CHANNEL_USERNAME, CHANNEL_LINK, CHANNEL_BUTTON_TEXT = range(3)


@admin_only
async def channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show channels management menu."""
    keyboard = [
        [InlineKeyboardButton("➕ Add New Channel", callback_data="channel_add")],
        [InlineKeyboardButton("📋 List All Channels", callback_data="channel_list")],
        [InlineKeyboardButton("❌ Close", callback_data="channel_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📺 *Force Subscribe Channels Management*\n\n"
        "Manage channels that users must subscribe to before accessing files.\n\n"
        "Select an option:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def add_channel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new force subscribe channel."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "➕ *Add Force Subscribe Channel*\n\n"
        "Step 1/3: Send me the channel username or ID\n\n"
        "Examples:\n"
        "• @yourchannel\n"
        "• -1001234567890\n\n"
        "⚠️ Make sure the User Bot is added as admin in this channel!\n\n"
        "Send /cancel to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CHANNEL_USERNAME


async def receive_channel_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive channel username/ID and validate."""
    channel_input = update.message.text.strip()
    
    # Validate format
    if not (channel_input.startswith('@') or channel_input.startswith('-100')):
        await update.message.reply_text(
            "❌ Invalid format!\n\n"
            "Please send:\n"
            "• Channel username (e.g., @yourchannel)\n"
            "• Channel ID (e.g., -1001234567890)\n\n"
            "Send /cancel to cancel."
        )
        return CHANNEL_USERNAME
    
    # Try to verify channel exists (basic check)
    try:
        # Store channel username
        context.user_data['channel_username'] = channel_input
        
        await update.message.reply_text(
            "✅ Channel username received!\n\n"
            "Step 2/3: Send me the channel invite link\n\n"
            "Example:\n"
            "• https://t.me/yourchannel\n"
            "• https://t.me/+AbC123XyZ\n\n"
            "Send /cancel to cancel."
        )
        
        return CHANNEL_LINK
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error validating channel: {str(e)}\n\n"
            "Please try again or send /cancel"
        )
        return CHANNEL_USERNAME


async def receive_channel_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive channel link."""
    channel_link = update.message.text.strip()
    
    # Validate link format
    if not channel_link.startswith('https://t.me/'):
        await update.message.reply_text(
            "❌ Invalid link format!\n\n"
            "Please send a valid Telegram link:\n"
            "• https://t.me/yourchannel\n"
            "• https://t.me/+AbC123XyZ\n\n"
            "Send /cancel to cancel."
        )
        return CHANNEL_LINK
    
    context.user_data['channel_link'] = channel_link
    
    await update.message.reply_text(
        "✅ Channel link received!\n\n"
        "Step 3/3: Send me the button text for this channel\n\n"
        "This text will appear on the button that users click to join.\n\n"
        "Examples:\n"
        "• BACKUP CHANNEL\n"
        "• MAIN CHANNEL\n"
        "• JOIN NOW\n\n"
        "Send /cancel to cancel."
    )
    
    return CHANNEL_BUTTON_TEXT


async def receive_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive button text and save channel."""
    button_text = update.message.text.strip()
    
    if len(button_text) > 50:
        await update.message.reply_text(
            "❌ Button text too long! Maximum 50 characters.\n\n"
            "Please send a shorter text or /cancel"
        )
        return CHANNEL_BUTTON_TEXT
    
    # Get stored data
    channel_username = context.user_data.get('channel_username')
    channel_link = context.user_data.get('channel_link')
    admin_id = update.effective_user.id
    
    # Save to database
    try:
        result = await add_channel(
            channel_username=channel_username,
            channel_link=channel_link,
            button_text=button_text,
            added_by=admin_id
        )
        
        if result:
            await update.message.reply_text(
                "✅ *Channel Added Successfully!*\n\n"
                f"*Channel:* {channel_username}\n"
                f"*Link:* {channel_link}\n"
                f"*Button Text:* {button_text}\n\n"
                "Users will now need to subscribe to this channel to access files.\n\n"
                "⚠️ Make sure User Bot is admin in this channel!",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ Failed to add channel. It might already exist.\n\n"
                "Use /channels to try again."
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error adding channel: {str(e)}\n\n"
            "Please try again with /channels"
        )
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all force subscribe channels."""
    query = update.callback_query
    await query.answer()
    
    channels = await get_all_channels()
    
    if not channels:
        await query.edit_message_text(
            "📋 *Force Subscribe Channels*\n\n"
            "No channels added yet.\n\n"
            "Use the 'Add New Channel' option to add your first channel.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Create message with channels list
    message = "📋 *Force Subscribe Channels*\n\n"
    
    keyboard = []
    for idx, channel in enumerate(channels, 1):
        status_emoji = "✅" if channel.get('is_active', True) else "❌"
        message += (
            f"{idx}. {status_emoji} *{channel['button_text']}*\n"
            f"   Channel: `{channel['channel_username']}`\n"
            f"   Link: {channel['channel_link']}\n"
            f"   Order: {channel.get('order', idx)}\n\n"
        )
        
        # Add buttons for each channel
        keyboard.append([
            InlineKeyboardButton(
                f"{'✅' if channel.get('is_active', True) else '❌'} Toggle #{idx}",
                callback_data=f"channel_toggle_{channel['_id']}"
            ),
            InlineKeyboardButton(
                f"🗑️ Delete #{idx}",
                callback_data=f"channel_delete_{channel['_id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="channel_menu")])
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="channel_close")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def toggle_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle channel active status."""
    query = update.callback_query
    await query.answer()
    
    channel_id = query.data.split('_')[-1]
    
    try:
        result = await toggle_channel_status(channel_id)
        
        if result:
            await query.answer("✅ Channel status updated!", show_alert=True)
            # Refresh the list
            await list_channels(update, context)
        else:
            await query.answer("❌ Failed to update channel status", show_alert=True)
    
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


async def delete_channel_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask for confirmation before deleting channel."""
    query = update.callback_query
    await query.answer()
    
    channel_id = query.data.split('_')[-1]
    
    # Get channel details
    channel = await get_channel_by_id(channel_id)
    
    if not channel:
        await query.answer("❌ Channel not found", show_alert=True)
        return
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f"channel_delete_confirm_{channel_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="channel_list")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚠️ *Delete Channel Confirmation*\n\n"
        f"Are you sure you want to delete this channel?\n\n"
        f"*Channel:* {channel['channel_username']}\n"
        f"*Button Text:* {channel['button_text']}\n\n"
        "This action cannot be undone!",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def delete_channel_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute channel deletion."""
    query = update.callback_query
    await query.answer()
    
    channel_id = query.data.split('_')[-1]
    
    try:
        result = await remove_channel(channel_id)
        
        if result:
            await query.answer("✅ Channel deleted successfully!", show_alert=True)
            # Refresh the list
            await list_channels(update, context)
        else:
            await query.answer("❌ Failed to delete channel", show_alert=True)
    
    except Exception as e:
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


async def show_channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show channels menu again."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("➕ Add New Channel", callback_data="channel_add")],
        [InlineKeyboardButton("📋 List All Channels", callback_data="channel_list")],
        [InlineKeyboardButton("❌ Close", callback_data="channel_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📺 *Force Subscribe Channels Management*\n\n"
        "Manage channels that users must subscribe to before accessing files.\n\n"
        "Select an option:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def close_channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close channels menu."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("✅ Channels menu closed.")


async def cancel_channel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel channel operation."""
    context.user_data.clear()
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END


# Create conversation handler for adding channels
add_channel_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_channel_start, pattern='^channel_add$')],
    states={
        CHANNEL_USERNAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel_username)
        ],
        CHANNEL_LINK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel_link)
        ],
        CHANNEL_BUTTON_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_button_text)
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel_channel_operation)],
    name="add_channel_conversation",
    persistent=False
)

# Create main channels handler
channels_handler = [
    CommandHandler('channels', channels_menu),
    CallbackQueryHandler(list_channels, pattern='^channel_list$'),
    CallbackQueryHandler(toggle_channel, pattern='^channel_toggle_'),
    CallbackQueryHandler(delete_channel_confirm, pattern='^channel_delete_[^_]+$'),
    CallbackQueryHandler(delete_channel_execute, pattern='^channel_delete_confirm_'),
    CallbackQueryHandler(show_channels_menu, pattern='^channel_menu$'),
    CallbackQueryHandler(close_channels_menu, pattern='^channel_close$'),
    add_channel_handler
]