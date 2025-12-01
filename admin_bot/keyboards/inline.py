"""
Inline Keyboard Builders for Admin Bot
Contains reusable inline keyboard layouts for various admin operations.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Optional


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the main menu keyboard."""
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
    return InlineKeyboardMarkup(keyboard)


def files_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the file management submenu keyboard."""
    keyboard = [
        [InlineKeyboardButton("⬆️ Upload New File", callback_data="action_upload")],
        [InlineKeyboardButton("📋 List All Files", callback_data="action_list_files")],
        [InlineKeyboardButton("✏️ Edit File", callback_data="action_edit_file")],
        [InlineKeyboardButton("🗑️ Delete File", callback_data="action_delete_file")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def broadcast_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the broadcast submenu keyboard."""
    keyboard = [
        [InlineKeyboardButton("📨 Broadcast to All Users", callback_data="broadcast_all")],
        [InlineKeyboardButton("✅ Broadcast to Verified Users", callback_data="broadcast_verified")],
        [InlineKeyboardButton("🔥 Broadcast to Active Users (Last 7 Days)", callback_data="broadcast_active")],
        [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def users_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the user management submenu keyboard."""
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
    return InlineKeyboardMarkup(keyboard)


def channels_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the channel management submenu keyboard."""
    keyboard = [
        [InlineKeyboardButton("➕ Add New Channel", callback_data="channel_add")],
        [InlineKeyboardButton("📋 List All Channels", callback_data="channel_list")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def settings_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the settings submenu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🔐 Set File Password", callback_data="setting_password")],
        [InlineKeyboardButton("🎥 Set How to Verify Link", callback_data="setting_verify_link")],
        [InlineKeyboardButton("🔗 Set Shortlink API", callback_data="setting_shortlink")],
        [InlineKeyboardButton("👁️ View All Settings", callback_data="setting_view_all")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def analytics_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the analytics submenu keyboard."""
    keyboard = [
        [InlineKeyboardButton("📅 Daily Statistics", callback_data="analytics_daily")],
        [InlineKeyboardButton("🏆 Top Files", callback_data="analytics_top_files")],
        [InlineKeyboardButton("👤 Active Users", callback_data="analytics_active")],
        [InlineKeyboardButton("📊 Full Report", callback_data="analytics_full")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def confirmation_keyboard(confirm_data: str, cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """
    Build a confirmation keyboard.
    
    Args:
        confirm_data: Callback data for confirm button
        cancel_data: Callback data for cancel button
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=confirm_data),
            InlineKeyboardButton("❌ Cancel", callback_data=cancel_data)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard(cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """
    Build a simple cancel keyboard.
    
    Args:
        cancel_data: Callback data for cancel button
    """
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data=cancel_data)]]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Build a back to main menu keyboard."""
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]]
    return InlineKeyboardMarkup(keyboard)


def pagination_keyboard(
    page: int,
    total_pages: int,
    prefix: str,
    show_back: bool = True
) -> InlineKeyboardMarkup:
    """
    Build a pagination keyboard.
    
    Args:
        page: Current page number (1-indexed)
        total_pages: Total number of pages
        prefix: Callback data prefix (e.g., "files_page_")
        show_back: Whether to show back to menu button
    """
    buttons = []
    
    # Navigation buttons
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{prefix}{page-1}"))
    
    nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="page_info"))
    
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"{prefix}{page+1}"))
    
    buttons.append(nav_row)
    
    # Back button
    if show_back:
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="menu_main")])
    
    return InlineKeyboardMarkup(buttons)


def channel_action_keyboard(channel_id: str, is_active: bool) -> InlineKeyboardMarkup:
    """
    Build keyboard for channel actions.
    
    Args:
        channel_id: Channel database ID
        is_active: Current active status
    """
    status_emoji = "✅" if is_active else "❌"
    keyboard = [
        [
            InlineKeyboardButton(
                f"{status_emoji} Toggle Status",
                callback_data=f"channel_toggle_{channel_id}"
            ),
            InlineKeyboardButton("🗑️ Delete", callback_data=f"channel_delete_{channel_id}")
        ],
        [InlineKeyboardButton("🔙 Back to List", callback_data="channel_list")]
    ]
    return InlineKeyboardMarkup(keyboard)


def file_action_keyboard(post_no: int) -> InlineKeyboardMarkup:
    """
    Build keyboard for file actions.
    
    Args:
        post_no: File post number
    """
    keyboard = [
        [
            InlineKeyboardButton("✏️ Edit", callback_data=f"file_edit_{post_no}"),
            InlineKeyboardButton("🗑️ Delete", callback_data=f"file_delete_{post_no}")
        ],
        [InlineKeyboardButton("📊 Statistics", callback_data=f"file_stats_{post_no}")],
        [InlineKeyboardButton("🔙 Back to List", callback_data="action_list_files")]
    ]
    return InlineKeyboardMarkup(keyboard)


def user_action_keyboard(user_id: int, is_verified: bool) -> InlineKeyboardMarkup:
    """
    Build keyboard for user actions.
    
    Args:
        user_id: User's Telegram ID
        is_verified: User's verification status
    """
    keyboard = []
    
    if is_verified:
        keyboard.append([
            InlineKeyboardButton("❌ Unverify", callback_data=f"user_unverify_{user_id}"),
            InlineKeyboardButton("⏰ Extend", callback_data=f"user_extend_{user_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("✅ Verify 24h", callback_data=f"user_verify_24_{user_id}"),
            InlineKeyboardButton("✅ Verify 48h", callback_data=f"user_verify_48_{user_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🔄 Reset Limit", callback_data=f"user_reset_{user_id}")
    ])
    keyboard.append([
        InlineKeyboardButton("🔙 Back", callback_data="action_verified_list")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard for broadcast confirmation."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm & Send", callback_data="broadcast_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def stats_refresh_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard for statistics with refresh option."""
    keyboard = [
        [
            InlineKeyboardButton("📅 Daily Stats", callback_data="stats_daily"),
            InlineKeyboardButton("🏆 Top Files", callback_data="stats_top_files")
        ],
        [
            InlineKeyboardButton("👤 Active Users", callback_data="stats_active"),
            InlineKeyboardButton("✅ Verified List", callback_data="stats_verified")
        ],
        [InlineKeyboardButton("🔄 Refresh", callback_data="stats_refresh")],
        [InlineKeyboardButton("❌ Close", callback_data="stats_close")]
    ]
    return InlineKeyboardMarkup(keyboard)


def help_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard for help menu."""
    keyboard = [
        [InlineKeyboardButton("📋 Main Menu", callback_data="menu_main")],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_inline_keyboard(buttons: List[List[dict]]) -> InlineKeyboardMarkup:
    """
    Build a custom inline keyboard from a button configuration.
    
    Args:
        buttons: List of rows, each row is a list of button dicts with 'text' and 'callback_data' or 'url'
        
    Example:
        buttons = [
            [{'text': 'Button 1', 'callback_data': 'btn1'}, {'text': 'Button 2', 'url': 'https://...'}],
            [{'text': 'Button 3', 'callback_data': 'btn3'}]
        ]
    """
    keyboard = []
    
    for row in buttons:
        button_row = []
        for btn in row:
            if 'url' in btn:
                button_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
            elif 'callback_data' in btn:
                button_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']))
        
        if button_row:
            keyboard.append(button_row)
    
    return InlineKeyboardMarkup(keyboard)


def yes_no_keyboard(yes_data: str, no_data: str) -> InlineKeyboardMarkup:
    """
    Build a simple yes/no keyboard.
    
    Args:
        yes_data: Callback data for yes button
        no_data: Callback data for no button
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data=yes_data),
            InlineKeyboardButton("❌ No", callback_data=no_data)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def close_keyboard(close_data: str = "close") -> InlineKeyboardMarkup:
    """
    Build a simple close keyboard.
    
    Args:
        close_data: Callback data for close button
    """
    keyboard = [[InlineKeyboardButton("❌ Close", callback_data=close_data)]]
    return InlineKeyboardMarkup(keyboard)