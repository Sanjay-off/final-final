"""
Attachment Menu Builders for Admin Bot
Provides telegram attachment menu (bot menu button) functionality.
"""

from telegram import MenuButton, MenuButtonCommands, MenuButtonWebApp, WebAppInfo
from typing import Optional


def get_menu_button(menu_type: str = "commands") -> MenuButton:
    """
    Get menu button configuration.
    
    Args:
        menu_type: Type of menu button ('commands', 'webapp', 'default')
    
    Returns:
        MenuButton object
    """
    if menu_type == "commands":
        return MenuButtonCommands()
    elif menu_type == "default":
        return MenuButton(type="default")
    else:
        return MenuButtonCommands()


def build_attachment_menu() -> dict:
    """
    Build the attachment menu structure for admin bot.
    This defines the menu that appears when users click the bot menu button.
    
    Returns:
        Dictionary containing menu configuration
    """
    menu_config = {
        "menu_button": {
            "type": "commands"
        },
        "commands": [
            {
                "command": "menu",
                "description": "📋 Open main admin menu"
            },
            {
                "command": "upload",
                "description": "⬆️ Upload a new ZIP file"
            },
            {
                "command": "broadcast",
                "description": "📢 Broadcast message to users"
            },
            {
                "command": "stats",
                "description": "📊 View system statistics"
            },
            {
                "command": "channels",
                "description": "📺 Manage force subscribe channels"
            },
            {
                "command": "verifiedusers",
                "description": "✅ List verified users"
            },
            {
                "command": "verifyuser",
                "description": "➕ Manually verify a user"
            },
            {
                "command": "setpassword",
                "description": "🔐 Set file password"
            },
            {
                "command": "sethowtoverify",
                "description": "🎥 Set verification tutorial link"
            },
            {
                "command": "viewsettings",
                "description": "⚙️ View all settings"
            },
            {
                "command": "dailystats",
                "description": "📅 Daily statistics report"
            },
            {
                "command": "topfiles",
                "description": "🏆 Most downloaded files"
            },
            {
                "command": "activeusers",
                "description": "👤 Active users today"
            },
            {
                "command": "userinfo",
                "description": "🔍 Get user information"
            },
            {
                "command": "resetuserlimit",
                "description": "🔄 Reset user file limit"
            },
            {
                "command": "unverifyuser",
                "description": "❌ Remove user verification"
            },
            {
                "command": "help",
                "description": "ℹ️ Show all commands"
            },
            {
                "command": "about",
                "description": "ℹ️ About this bot system"
            },
            {
                "command": "cancel",
                "description": "❌ Cancel current operation"
            }
        ]
    }
    
    return menu_config


def get_admin_commands() -> list:
    """
    Get list of admin bot commands for BotFather.
    This is the command list you should set in BotFather.
    
    Returns:
        List of command dictionaries
    """
    commands = [
        {"command": "start", "description": "Start the admin bot"},
        {"command": "menu", "description": "Open main admin menu"},
        {"command": "help", "description": "Show all commands"},
        
        # File Management
        {"command": "upload", "description": "Upload a new ZIP file"},
        {"command": "listfiles", "description": "List all uploaded files"},
        
        # Broadcasting
        {"command": "broadcast", "description": "Broadcast message to users"},
        
        # User Management
        {"command": "stats", "description": "View system statistics"},
        {"command": "verifiedusers", "description": "List verified users"},
        {"command": "verifyuser", "description": "Verify user: /verifyuser <id> <hours>"},
        {"command": "unverifyuser", "description": "Unverify user: /unverifyuser <id>"},
        {"command": "userinfo", "description": "Get user info: /userinfo <id>"},
        {"command": "resetuserlimit", "description": "Reset limit: /resetuserlimit <id>"},
        {"command": "activeusers", "description": "Show active users today"},
        {"command": "dailystats", "description": "Daily statistics report"},
        {"command": "topfiles", "description": "Most downloaded files"},
        
        # Channel Management
        {"command": "channels", "description": "Manage force subscribe channels"},
        
        # Settings
        {"command": "setpassword", "description": "Set file password"},
        {"command": "sethowtoverify", "description": "Set verification tutorial link"},
        {"command": "setshorlink", "description": "Set shortlink API key"},
        {"command": "viewsettings", "description": "View all settings"},
        
        # Other
        {"command": "about", "description": "About this bot system"},
        {"command": "cancel", "description": "Cancel current operation"},
    ]
    
    return commands


def get_commands_text() -> str:
    """
    Get formatted text of all commands for BotFather.
    Copy this output and paste it in BotFather when setting commands.
    
    Returns:
        Formatted command list string
    """
    commands = get_admin_commands()
    
    text = "# Admin Bot Commands for BotFather\n"
    text += "# Copy everything below this line and paste in BotFather\n\n"
    
    for cmd in commands:
        text += f"{cmd['command']} - {cmd['description']}\n"
    
    return text


def get_quick_access_commands() -> list:
    """
    Get list of most frequently used commands for quick access.
    
    Returns:
        List of command names
    """
    return [
        "menu",
        "upload",
        "broadcast",
        "stats",
        "channels",
        "verifyuser",
        "help"
    ]


def get_commands_by_category() -> dict:
    """
    Get commands organized by category.
    
    Returns:
        Dictionary with categories as keys and command lists as values
    """
    return {
        "File Management": [
            "/upload - Upload a new ZIP file",
            "/listfiles - List all uploaded files",
            "/editfile <post_no> - Edit file details",
            "/deletefile <post_no> - Delete a file"
        ],
        "Broadcasting": [
            "/broadcast - Start broadcast wizard"
        ],
        "User Management": [
            "/stats - View overall statistics",
            "/verifiedusers - List verified users",
            "/verifyuser <user_id> <hours> - Manually verify user",
            "/unverifyuser <user_id> - Remove verification",
            "/userinfo <user_id> - Get user details",
            "/resetuserlimit <user_id> - Reset file access count",
            "/extendverification <user_id> <hours> - Extend verification",
            "/bulkverify <hours> <id1> <id2>... - Verify multiple users",
            "/activeusers - Active users today",
            "/dailystats - Daily statistics report"
        ],
        "Channel Management": [
            "/channels - Manage force subscribe channels"
        ],
        "Settings": [
            "/setpassword <password> - Set file password",
            "/sethowtoverify - Set verification tutorial link",
            "/setshorlink <api_key> - Set shortlink API key",
            "/viewsettings - View all settings",
            "/getsetting <key> - Get specific setting"
        ],
        "Analytics": [
            "/topfiles - Most downloaded files",
            "/analytics - Detailed analytics report"
        ],
        "General": [
            "/menu - Open main menu",
            "/start - Show welcome message",
            "/help - Show all commands",
            "/about - About this system",
            "/cancel - Cancel current operation",
            "/ping - Check bot status"
        ]
    }


def format_commands_help() -> str:
    """
    Format all commands as help text.
    
    Returns:
        Formatted help text string
    """
    categories = get_commands_by_category()
    
    help_text = "📚 *Admin Bot Commands*\n\n"
    
    for category, commands in categories.items():
        help_text += f"*{category}:*\n"
        for cmd in commands:
            help_text += f"{cmd}\n"
        help_text += "\n"
    
    help_text += "*💡 Tips:*\n"
    help_text += "• Use /menu for visual navigation\n"
    help_text += "• Commands work during conversations\n"
    help_text += "• User Bot must be admin in force sub channels\n"
    
    return help_text