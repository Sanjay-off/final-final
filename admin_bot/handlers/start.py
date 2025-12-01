"""
Start Handler for Admin Bot
Handles the /start command and initial bot interaction for admins.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from admin_bot.middleware.auth import admin_only, is_admin
from database.operations.logs import log_admin_action


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show welcome message for admins."""
    user = update.effective_user
    user_id = user.id
    
    # Check if user is admin
    if not await is_admin(user_id):
        await update.message.reply_text(
            "⛔ *Access Denied*\n\n"
            "This bot is restricted to administrators only.\n\n"
            "If you believe this is an error, please contact the bot owner.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Log admin access
    try:
        await log_admin_action(
            admin_id=user_id,
            action='start_bot',
            details={'username': user.username, 'first_name': user.first_name}
        )
    except:
        pass  # Don't fail if logging fails
    
    # Create welcome keyboard
    keyboard = [
        [
            InlineKeyboardButton("📁 File Management", callback_data="menu_files"),
            InlineKeyboardButton("📢 Broadcast", callback_data="menu_broadcast")
        ],
        [
            InlineKeyboardButton("👥 User Management", callback_data="menu_users"),
            InlineKeyboardButton("📺 Channels", callback_data="menu_channels")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("📈 Analytics", callback_data="menu_analytics")
        ],
        [
            InlineKeyboardButton("📋 Main Menu", callback_data="menu_main"),
            InlineKeyboardButton("ℹ️ Help", callback_data="menu_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        f"👋 *Welcome, {user.first_name}!*\n\n"
        "🤖 *Admin Control Panel*\n\n"
        "This is your admin bot for managing the file distribution system.\n\n"
        "*Quick Access:*\n"
        "• Upload files and manage posts\n"
        "• Broadcast messages to users\n"
        "• Manage force subscribe channels\n"
        "• View statistics and analytics\n"
        "• Configure bot settings\n\n"
        "*Getting Started:*\n"
        "Use the menu below or type /help for all commands.\n\n"
        "💡 *Tip:* Use /menu anytime to access the main menu."
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message with all available commands."""
    help_text = (
        "📚 *Admin Bot Commands*\n\n"
        
        "*📁 File Management:*\n"
        "/upload - Upload a new ZIP file\n"
        "/listfiles - List all uploaded files\n"
        "/editfile <post_no> - Edit file details\n"
        "/deletefile <post_no> - Delete a file\n\n"
        
        "*📢 Broadcasting:*\n"
        "/broadcast - Start broadcast wizard\n"
        "• Broadcast to all users\n"
        "• Broadcast to verified users only\n"
        "• Broadcast to active users (last 7 days)\n\n"
        
        "*👥 User Management:*\n"
        "/stats - View overall statistics\n"
        "/verifiedusers - List verified users\n"
        "/verifyuser <user_id> <hours> - Manually verify user\n"
        "/unverifyuser <user_id> - Remove user verification\n"
        "/userinfo <user_id> - Get user details\n"
        "/resetuserlimit <user_id> - Reset file access count\n"
        "/dailystats - Daily statistics report\n"
        "/activeusers - Active users today\n\n"
        
        "*📺 Channel Management:*\n"
        "/channels - Manage force subscribe channels\n"
        "• Add new channels\n"
        "• List all channels\n"
        "• Toggle channel status\n"
        "• Delete channels\n\n"
        
        "*⚙️ Settings:*\n"
        "/setpassword <password> - Set file password\n"
        "/sethowtoverify - Set verification tutorial link\n"
        "/setshorlink <api_key> - Set shortlink API key\n"
        "/viewsettings - View all current settings\n"
        "/getsetting <key> - Get specific setting\n\n"
        
        "*📈 Analytics:*\n"
        "/topfiles - Most downloaded files\n"
        "/analytics - Detailed analytics report\n\n"
        
        "*⚡ Quick Commands:*\n"
        "/menu - Open main menu\n"
        "/start - Show welcome message\n"
        "/cancel - Cancel current operation\n\n"
        
        "*💡 Tips:*\n"
        "• Use inline menus for easier navigation\n"
        "• All commands work while in conversation mode\n"
        "• User Bot must be admin in force sub channels\n"
        "• Keep your API keys and tokens secure\n"
        "• Regular backups are recommended\n\n"
        
        "*⚠️ Important:*\n"
        "• Only authorized admins can use this bot\n"
        "• All actions are logged for security\n"
        "• Changes are applied immediately\n\n"
        
        "Need more help? Use /menu to navigate visually."
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Main Menu", callback_data="menu_main")],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


async def help_close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close help message."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Help menu closed.")


@admin_only
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show information about the bot system."""
    about_text = (
        "ℹ️ *About This System*\n\n"
        
        "*Telegram File Distribution System*\n"
        "Version: 1.0.0\n\n"
        
        "*Components:*\n"
        "• Admin Bot - File and user management\n"
        "• User Bot - File distribution to users\n"
        "• Verification Server - User verification system\n"
        "• MongoDB Database - Data storage\n\n"
        
        "*Features:*\n"
        "✅ Secure file distribution\n"
        "✅ Force subscribe channels\n"
        "✅ User verification system\n"
        "✅ Auto-delete messages (10 min)\n"
        "✅ File access limits (3 files/day)\n"
        "✅ Broadcast messaging\n"
        "✅ Real-time analytics\n"
        "✅ Bypass detection\n\n"
        
        "*Security:*\n"
        "• Admin-only access control\n"
        "• Encrypted verification tokens\n"
        "• Action logging\n"
        "• API key masking\n\n"
        
        "*System Status:* 🟢 Online\n"
        "*Database:* 🟢 Connected\n\n"
        
        "For technical support, contact the system administrator."
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 Main Menu", callback_data="menu_main")],
        [InlineKeyboardButton("📚 Help", callback_data="menu_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        about_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any ongoing operation."""
    # Clear user data
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ *Operation Cancelled*\n\n"
        "All ongoing operations have been cancelled.\n"
        "You can start fresh with any command.",
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if bot is responsive."""
    await update.message.reply_text(
        "🏓 *Pong!*\n\n"
        "Bot is online and responsive.\n"
        f"Your ID: `{update.effective_user.id}`",
        parse_mode=ParseMode.MARKDOWN
    )


# Create start handler
start_handler = [
    CommandHandler('start', start_command),
    CommandHandler('help', help_command),
    CommandHandler('about', about_command),
    CommandHandler('cancel', cancel_command),
    CommandHandler('ping', ping_command),
    CallbackQueryHandler(help_close_callback, pattern='^help_close$')
]