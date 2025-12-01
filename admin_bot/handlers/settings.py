"""
Settings Handler for Admin Bot
Handles configuration settings like password, verification link, shortlink API, etc.
"""

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

from database.operations.settings import (
    set_setting,
    get_setting,
    get_all_settings
)
from admin_bot.middleware.auth import admin_only

# Conversation states
SET_PASSWORD, SET_VERIFY_LINK, SET_SHORTLINK_API = range(3)


@admin_only
async def set_password_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start setting file password."""
    await update.message.reply_text(
        "🔐 *Set File Password*\n\n"
        "This password will be used for all ZIP files.\n"
        "Users will see this in the file caption.\n\n"
        "Send me the new password:\n\n"
        "💡 Tips:\n"
        "• Keep it simple and memorable\n"
        "• Avoid special characters that might confuse users\n"
        "• Recommended: 8-20 characters\n\n"
        "Send /cancel to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SET_PASSWORD


async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save password."""
    password = update.message.text.strip()
    
    if len(password) < 4:
        await update.message.reply_text(
            "❌ Password too short! Minimum 4 characters.\n\n"
            "Please send a longer password or /cancel"
        )
        return SET_PASSWORD
    
    if len(password) > 50:
        await update.message.reply_text(
            "❌ Password too long! Maximum 50 characters.\n\n"
            "Please send a shorter password or /cancel"
        )
        return SET_PASSWORD
    
    # Save to database
    admin_id = update.effective_user.id
    
    try:
        result = await set_setting(
            setting_key='file_password',
            setting_value=password,
            updated_by=admin_id
        )
        
        if result:
            await update.message.reply_text(
                "✅ *Password Updated Successfully!*\n\n"
                f"New Password: `{password}`\n\n"
                "This password will be used for all new files.\n"
                "Users will see: `password - {password}` in file captions.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ Failed to update password. Please try again."
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error updating password: {str(e)}"
        )
    
    return ConversationHandler.END


@admin_only
async def set_verify_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start setting verification tutorial link."""
    await update.message.reply_text(
        "🎥 *Set 'How to Verify' Link*\n\n"
        "This link will be shown when users click the 'How to Verify' button.\n\n"
        "Send me the Telegram message link:\n\n"
        "Format: `https://t.me/c/CHANNEL_ID/MESSAGE_ID`\n"
        "Or: `https://t.me/channel_username/MESSAGE_ID`\n\n"
        "💡 How to get the link:\n"
        "1. Post your verification tutorial video in a channel\n"
        "2. Right-click the message → Copy Link\n"
        "3. Paste it here\n\n"
        "Send /cancel to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SET_VERIFY_LINK


async def receive_verify_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save verification tutorial link."""
    link = update.message.text.strip()
    
    # Validate link format
    if not link.startswith('https://t.me/'):
        await update.message.reply_text(
            "❌ Invalid link format!\n\n"
            "Please send a valid Telegram link:\n"
            "• https://t.me/c/CHANNEL_ID/MESSAGE_ID\n"
            "• https://t.me/channel_username/MESSAGE_ID\n\n"
            "Send /cancel to cancel."
        )
        return SET_VERIFY_LINK
    
    # Save to database
    admin_id = update.effective_user.id
    
    try:
        result = await set_setting(
            setting_key='how_to_verify_link',
            setting_value=link,
            updated_by=admin_id
        )
        
        if result:
            await update.message.reply_text(
                "✅ *Verification Tutorial Link Updated!*\n\n"
                f"Link: {link}\n\n"
                "Users will see this link when they click 'How to Verify' button.",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        else:
            await update.message.reply_text(
                "❌ Failed to update link. Please try again."
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error updating link: {str(e)}"
        )
    
    return ConversationHandler.END


@admin_only
async def set_shortlink_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start setting shortlink API credentials."""
    await update.message.reply_text(
        "🔗 *Set Shortlink API*\n\n"
        "Configure your shortlink service API credentials.\n\n"
        "Send me the API key:\n\n"
        "Example: `abc123xyz456`\n\n"
        "💡 Where to find:\n"
        "• Login to your shortlink service\n"
        "• Go to API/Developer section\n"
        "• Copy your API key\n\n"
        "Send /cancel to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return SET_SHORTLINK_API


async def receive_shortlink_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and save shortlink API key."""
    api_key = update.message.text.strip()
    
    if len(api_key) < 10:
        await update.message.reply_text(
            "❌ API key seems too short!\n\n"
            "Please send a valid API key or /cancel"
        )
        return SET_SHORTLINK_API
    
    # Save to database
    admin_id = update.effective_user.id
    
    try:
        result = await set_setting(
            setting_key='shortlink_api_key',
            setting_value=api_key,
            updated_by=admin_id
        )
        
        if result:
            # Hide middle part of API key for security
            masked_key = api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
            
            await update.message.reply_text(
                "✅ *Shortlink API Key Updated!*\n\n"
                f"API Key: `{masked_key}`\n\n"
                "⚠️ Keep your API key secure!\n"
                "The key is now saved and will be used for verification links.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ Failed to update API key. Please try again."
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error updating API key: {str(e)}"
        )
    
    return ConversationHandler.END


@admin_only
async def view_settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all current settings."""
    try:
        settings = await get_all_settings()
        
        if not settings:
            await update.message.reply_text(
                "⚙️ *Current Settings*\n\n"
                "No settings configured yet.\n\n"
                "Use the following commands to configure:\n"
                "/setpassword - Set file password\n"
                "/sethowtoverify - Set verification tutorial link\n"
                "/setshorlink - Set shortlink API",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        message = "⚙️ *Current Settings*\n\n"
        
        setting_names = {
            'file_password': '🔐 File Password',
            'how_to_verify_link': '🎥 How to Verify Link',
            'shortlink_api_key': '🔗 Shortlink API Key',
            'verification_period_hours': '⏰ Verification Period',
            'file_access_limit': '📊 File Access Limit'
        }
        
        for setting in settings:
            key = setting['setting_key']
            value = setting['setting_value']
            
            # Format display name
            display_name = setting_names.get(key, key.replace('_', ' ').title())
            
            # Mask sensitive data
            if 'api' in key.lower() or 'key' in key.lower():
                if len(value) > 8:
                    value = value[:4] + '*' * (len(value) - 8) + value[-4:]
            
            message += f"*{display_name}:*\n`{value}`\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔐 Change Password", callback_data="change_password")],
            [InlineKeyboardButton("🎥 Change Verify Link", callback_data="change_verify_link")],
            [InlineKeyboardButton("🔗 Change Shortlink API", callback_data="change_shortlink")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error fetching settings: {str(e)}"
        )


async def quick_change_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quick setting change from inline buttons."""
    query = update.callback_query
    await query.answer()
    
    action_commands = {
        'change_password': '/setpassword',
        'change_verify_link': '/sethowtoverify',
        'change_shortlink': '/setshorlink'
    }
    
    command = action_commands.get(query.data)
    
    if command:
        await query.edit_message_text(
            f"💡 To change this setting, use:\n`{command}`",
            parse_mode=ParseMode.MARKDOWN
        )


@admin_only
async def get_setting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get a specific setting value."""
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: `/getsetting <setting_key>`\n\n"
            "Available keys:\n"
            "• file_password\n"
            "• how_to_verify_link\n"
            "• shortlink_api_key\n"
            "• verification_period_hours\n"
            "• file_access_limit",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    setting_key = context.args[0]
    
    try:
        setting = await get_setting(setting_key)
        
        if setting:
            value = setting['setting_value']
            
            # Mask sensitive data
            if 'api' in setting_key.lower() or 'key' in setting_key.lower():
                if len(value) > 8:
                    value = value[:4] + '*' * (len(value) - 8) + value[-4:]
            
            await update.message.reply_text(
                f"⚙️ *Setting: {setting_key}*\n\n"
                f"Value: `{value}`\n"
                f"Last Updated: {setting.get('updated_at', 'N/A')}",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                f"❌ Setting '{setting_key}' not found.\n\n"
                "Use /viewsettings to see all configured settings."
            )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error fetching setting: {str(e)}"
        )


async def cancel_setting_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel setting operation."""
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END


# Create conversation handlers
set_password_handler = ConversationHandler(
    entry_points=[CommandHandler('setpassword', set_password_command)],
    states={
        SET_PASSWORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel_setting_operation)],
    name="set_password_conversation",
    persistent=False
)

set_verify_link_handler = ConversationHandler(
    entry_points=[CommandHandler('sethowtoverify', set_verify_link_command)],
    states={
        SET_VERIFY_LINK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_verify_link)
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel_setting_operation)],
    name="set_verify_link_conversation",
    persistent=False
)

set_shortlink_handler = ConversationHandler(
    entry_points=[CommandHandler('setshorlink', set_shortlink_command)],
    states={
        SET_SHORTLINK_API: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_shortlink_api)
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel_setting_operation)],
    name="set_shortlink_conversation",
    persistent=False
)

# Create main settings handler
settings_handler = [
    CommandHandler('viewsettings', view_settings_command),
    CommandHandler('getsetting', get_setting_command),
    CallbackQueryHandler(quick_change_setting, pattern='^change_'),
    set_password_handler,
    set_verify_link_handler,
    set_shortlink_handler
]