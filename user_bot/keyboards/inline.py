"""
Inline Keyboard Builders for User Bot
Contains reusable inline keyboard layouts for user interactions.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any


def force_subscribe_keyboard(channels: List[Dict[str, Any]], try_again_link: str) -> InlineKeyboardMarkup:
    """
    Build force subscribe keyboard with channel buttons.
    
    Args:
        channels: List of channel dictionaries with 'button_text' and 'channel_link'
        try_again_link: Deep link for try again button
    
    Returns:
        InlineKeyboardMarkup with channel buttons and try again button
    """
    keyboard = []
    
    # Add channel buttons (one per row for better visibility)
    for channel in channels:
        button_text = channel.get('button_text', 'JOIN CHANNEL')
        channel_link = channel.get('channel_link', '')
        
        keyboard.append([
            InlineKeyboardButton(button_text, url=channel_link)
        ])
    
    # Add try again button
    keyboard.append([
        InlineKeyboardButton("• TRY AGAIN •", url=try_again_link)
    ])
    
    return InlineKeyboardMarkup(keyboard)


def verification_keyboard(how_to_verify_link: str = None) -> InlineKeyboardMarkup:
    """
    Build verification keyboard with verify and help buttons.
    
    Args:
        how_to_verify_link: Optional link to verification tutorial
    
    Returns:
        InlineKeyboardMarkup with verification buttons
    """
    keyboard = [
        [InlineKeyboardButton("• VERIFY NOW •", callback_data="verify_now")]
    ]
    
    # Add "How to Verify" button if link is provided
    if how_to_verify_link:
        keyboard.append([
            InlineKeyboardButton("• HOW TO VERIFY •", url=how_to_verify_link)
        ])
    
    return InlineKeyboardMarkup(keyboard)


def file_deleted_keyboard(download_link: str) -> InlineKeyboardMarkup:
    """
    Build keyboard for deleted file message.
    
    Args:
        download_link: Deep link to re-download the file
    
    Returns:
        InlineKeyboardMarkup with click here and close buttons
    """
    keyboard = [
        [InlineKeyboardButton("♻️ CLICK HERE", url=download_link)],
        [InlineKeyboardButton("CLOSE ✖️", callback_data="close")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def close_keyboard() -> InlineKeyboardMarkup:
    """
    Build simple close button keyboard.
    
    Returns:
        InlineKeyboardMarkup with only close button
    """
    keyboard = [
        [InlineKeyboardButton("CLOSE ✖️", callback_data="close")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def try_again_keyboard(try_again_link: str) -> InlineKeyboardMarkup:
    """
    Build try again button keyboard.
    
    Args:
        try_again_link: Deep link for trying again
    
    Returns:
        InlineKeyboardMarkup with try again button
    """
    keyboard = [
        [InlineKeyboardButton("• TRY AGAIN •", url=try_again_link)]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def how_to_verify_button(link: str) -> InlineKeyboardMarkup:
    """
    Build how to verify button keyboard.
    
    Args:
        link: Link to verification tutorial
    
    Returns:
        InlineKeyboardMarkup with how to verify button
    """
    keyboard = [
        [InlineKeyboardButton("• HOW TO VERIFY •", url=link)]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def limit_reached_keyboard() -> InlineKeyboardMarkup:
    """
    Build keyboard for limit reached message.
    
    Returns:
        InlineKeyboardMarkup with verify again button
    """
    keyboard = [
        [InlineKeyboardButton("• VERIFY NOW •", callback_data="verify_now")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def already_verified_keyboard() -> InlineKeyboardMarkup:
    """
    Build keyboard for already verified message.
    
    Returns:
        InlineKeyboardMarkup with close button
    """
    keyboard = [
        [InlineKeyboardButton("CLOSE ✖️", callback_data="close")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def custom_keyboard(buttons: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
    """
    Build custom inline keyboard from button configuration.
    
    Args:
        buttons: List of rows, each row contains button dicts with 'text' and 'url' or 'callback_data'
        
    Example:
        buttons = [
            [{'text': 'Button 1', 'url': 'https://...'}, {'text': 'Button 2', 'callback_data': 'btn2'}],
            [{'text': 'Button 3', 'url': 'https://...'}]
        ]
    
    Returns:
        InlineKeyboardMarkup
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