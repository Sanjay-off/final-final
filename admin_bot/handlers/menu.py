"""
Attachment Menu Handler for Admin Bot
Provides an intuitive attachment menu interface for all admin operations.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, MenuButton, MenuButtonCommands
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler
)
from telegram.constants import ParseMode

from admin_bot.middleware.auth import admin_only
from database.operations.users import get_all_users_count, get_verified_users_count
from database.operations.files import get_total_files_count


@admin_only
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main attachment menu with all options."""
    # Get statistics for display
    try:
        total_users = await get_all_users_count()
        verified_users = await get_verified_users_count()
        total_files = await get_total_files_count()
    except:
        total_users = 0
        verified_users = 0
        total_files = 0
    
    keyboard = [
        [
            InlineKeyboardButton("📁 File Management", callback_data="menu_files"),
            InlineKeyboardButton("📢 Broadcast", callback_data="menu_broadcast")
        ],
        [
            InlineKeyboardButton("👥 User Management", callback_data="menu_users"),
            InlineKeyboardButton("📺 Channel Management", callback_data="menu_channels")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("📈 Analytics", callback_data="menu_analytics")
        ],
        [
            InlineKeyboardButton("ℹ️ Help & Commands", callback_data="menu_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    menu_text = (
        "📋 *Admin Control Panel*\n\n"
        f"👥 Total Users: `{total_users}`\n"
        f"✅ Verified Users: `{verified_users}`\n"
        f"📁 Total Files: `{total_files}`\n\n"
        "Select a category to manage:"
    )
    
    if update.message:
        await update.message.reply_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.callback_query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )


@admin_only
async def show_files_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show file management submenu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("⬆️ Upload New File", callback_data="action_upload")],
        [InlineKeyboardButton("📋 List All Files", callback_data="action_list_files")],
        [InlineKeyboardButton("✏️ Edit File", callback_data="action_edit_file")],
        [InlineKeyboardButton("🗑️ Delete File", callback_data="action_delete_file")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📁 *File Management*\n\n"
        "Manage your ZIP files and posts.\n\n"
        "What would you like to do?",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def show_broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show broadcast submenu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📨 Broadcast to All", callback_data="broadcast_all")],
        [InlineKeyboardButton("✅ Broadcast to Verified", callback_data="broadcast_verified")],
        [InlineKeyboardButton("🔥 Broadcast to Active", callback_data="broadcast_active")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📢 *Broadcast Message*\n\n"
        "Send messages to your users based on different criteria.\n\n"
        "Select broadcast type:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def show_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user management submenu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("📊 View Statistics", callback_data="action_stats"),
            InlineKeyboardButton("✅ Verified Users", callback_data="action_verified_list")
        ],
        [
            InlineKeyboardButton("➕ Verify User", callback_data="action_verify_user"),
            InlineKeyboardButton("🔍 Search User", callback_data="action_search_user")
        ],
        [
            InlineKeyboardButton("🔄 Reset User Limit", callback_data="action_reset_limit")
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "👥 *User Management*\n\n"
        "Manage users, verify manually, and view statistics.\n\n"
        "Select an option:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def show_channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show channel management submenu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("➕ Add New Channel", callback_data="channel_add")],
        [InlineKeyboardButton("📋 List All Channels", callback_data="channel_list")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📺 *Channel Management*\n\n"
        "Manage force subscribe channels.\n\n"
        "⚠️ Remember: User Bot must be admin in all channels!\n\n"
        "Select an option:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings submenu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔐 Set File Password", callback_data="setting_password")],
        [InlineKeyboardButton("🎥 Set How to Verify Link", callback_data="setting_verify_link")],
        [InlineKeyboardButton("🔗 Set Shortlink API", callback_data="setting_shortlink")],
        [InlineKeyboardButton("👁️ View All Settings", callback_data="setting_view_all")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ *Settings*\n\n"
        "Configure bot settings and parameters.\n\n"
        "Select a setting to modify:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def show_analytics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show analytics submenu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📅 Daily Statistics", callback_data="analytics_daily")],
        [InlineKeyboardButton("🏆 Top Files", callback_data="analytics_top_files")],
        [InlineKeyboardButton("👤 Active Users", callback_data="analytics_active")],
        [InlineKeyboardButton("📊 Full Report", callback_data="analytics_full")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📈 *Analytics*\n\n"
        "View detailed statistics and reports.\n\n"
        "Select a report:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


@admin_only
async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help and commands."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_text = (
        "ℹ️ *Help & Commands*\n\n"
        "*File Management:*\n"
        "/upload - Upload a new ZIP file\n"
        "/listfiles - List all uploaded files\n\n"
        "*Broadcasting:*\n"
        "/broadcast - Broadcast message to users\n\n"
        "*User Management:*\n"
        "/stats - View user statistics\n"
        "/verifiedusers - List verified users\n"
        "/verifyuser <user_id> <hours> - Manually verify user\n"
        "/unverifyuser <user_id> - Remove verification\n"
        "/userinfo <user_id> - Get user details\n"
        "/resetuserlimit <user_id> - Reset file access limit\n\n"
        "*Channel Management:*\n"
        "/channels - Manage force subscribe channels\n\n"
        "*Settings:*\n"
        "/setpassword <password> - Set file password\n"
        "/sethowtoverify - Set verification tutorial link\n"
        "/setshorlink <api_key> - Set shortlink API\n"
        "/viewsettings - View all settings\n\n"
        "*Quick Access:*\n"
        "/menu - Open this admin menu\n"
        "/cancel - Cancel current operation\n\n"
        "💡 *Tips:*\n"
        "• Use the menu buttons for easier navigation\n"
        "• Commands can be typed directly anytime\n"
        "• User Bot must be admin in force sub channels\n"
        "• Keep your tokens and API keys secure"
    )
    
    await query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


# Callback handler for menu navigation
async def menu_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu navigation callbacks."""
    query = update.callback_query
    
    menu_routes = {
        'menu_main': show_main_menu,
        'menu_files': show_files_menu,
        'menu_broadcast': show_broadcast_menu,
        'menu_users': show_users_menu,
        'menu_channels': show_channels_menu,
        'menu_settings': show_settings_menu,
        'menu_analytics': show_analytics_menu,
        'menu_help': show_help_menu
    }
    
    handler = menu_routes.get(query.data)
    if handler:
        await handler(update, context)
    else:
        await query.answer("⚠️ This option is not yet implemented", show_alert=True)


# Action placeholder handler
async def action_placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Placeholder for actions that redirect to other handlers."""
    query = update.callback_query
    await query.answer()
    
    action_messages = {
        'action_upload': "Please use /upload command to upload files",
        'action_list_files': "Please use /listfiles command to view all files",
        'action_edit_file': "Please use /editfile <post_no> command",
        'action_delete_file': "Please use /deletefile <post_no> command",
        'action_stats': "Please use /stats command",
        'action_verified_list': "Please use /verifiedusers command",
        'action_verify_user': "Please use /verifyuser <user_id> <hours> command",
        'action_search_user': "Please use /userinfo <user_id> command",
        'action_reset_limit': "Please use /resetuserlimit <user_id> command",
        'setting_password': "Please use /setpassword <password> command",
        'setting_verify_link': "Please use /sethowtoverify command",
        'setting_shortlink': "Please use /setshorlink <api_key> command",
        'setting_view_all': "Please use /viewsettings command",
        'analytics_daily': "Please use /dailystats command",
        'analytics_top_files': "Please use /topfiles command",
        'analytics_active': "Please use /activeusers command",
        'analytics_full': "Please use /stats command for full report"
    }
    
    message = action_messages.get(query.data, "This feature is being implemented")
    
    await query.answer(message, show_alert=True)


# Create menu handler
menu_handler = [
    CommandHandler('menu', show_main_menu),
    CallbackQueryHandler(menu_navigation_handler, pattern='^menu_'),
    CallbackQueryHandler(action_placeholder, pattern='^(action_|setting_|analytics_)')
]