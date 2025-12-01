"""
Force Subscribe Utilities for User Bot
Handles force subscribe channel checking and messaging.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from telegram import Bot, InlineKeyboardMarkup
from telegram.error import TelegramError

from database.operations.channels import get_active_channels
from user_bot.keyboards.inline import force_subscribe_keyboard
from shared.constants import FORCE_SUB_TEMPLATE
from shared.utils import build_deep_link
from shared.encryption import encode_url_safe
from config.settings import USER_BOT_USERNAME

logger = logging.getLogger(__name__)


async def check_user_subscribed(
    bot: Bot,
    user_id: int,
    channel_id: Optional[int] = None,
    channel_username: Optional[str] = None
) -> bool:
    """
    Check if user is subscribed to a specific channel.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        channel_id: Channel ID (optional)
        channel_username: Channel username (optional)
    
    Returns:
        True if subscribed, False otherwise
    """
    try:
        # Try with channel_id first, then username
        chat_identifier = channel_id if channel_id else channel_username
        
        if not chat_identifier:
            logger.warning("No channel identifier provided")
            return False
        
        # Get chat member
        member = await bot.get_chat_member(
            chat_id=chat_identifier,
            user_id=user_id
        )
        
        # Check if user is a member (not left or kicked)
        is_member = member.status not in ['left', 'kicked']
        
        return is_member
    
    except TelegramError as e:
        logger.warning(f"Error checking subscription for user {user_id}: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error checking subscription: {e}", exc_info=True)
        return False


async def get_unsubscribed_channels(
    bot: Bot,
    user_id: int
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Get list of channels user is not subscribed to.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
    
    Returns:
        Tuple of (is_subscribed_all: bool, unsubscribed_channels: list)
    """
    try:
        # Get all active force subscribe channels
        channels = await get_active_channels()
        
        if not channels:
            # No force sub channels configured
            logger.info("No force subscribe channels configured")
            return True, []
        
        unsubscribed = []
        
        for channel in channels:
            channel_id = channel.get('channel_id')
            channel_username = channel.get('channel_username')
            
            # Check subscription
            is_subscribed = await check_user_subscribed(
                bot=bot,
                user_id=user_id,
                channel_id=channel_id,
                channel_username=channel_username
            )
            
            if not is_subscribed:
                unsubscribed.append(channel)
                logger.info(f"User {user_id} not subscribed to {channel_username}")
        
        is_subscribed_all = len(unsubscribed) == 0
        
        return is_subscribed_all, unsubscribed
    
    except Exception as e:
        logger.error(f"Error getting unsubscribed channels: {e}", exc_info=True)
        return False, []


async def build_force_sub_message(
    username: str,
    unsubscribed_channels: List[Dict[str, Any]],
    try_again_link: str
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Build force subscribe message with channels keyboard.
    
    Args:
        username: User's first name or username
        unsubscribed_channels: List of channels user needs to subscribe to
        try_again_link: Deep link for try again button
    
    Returns:
        Tuple of (message_text: str, keyboard: InlineKeyboardMarkup)
    """
    try:
        # Format message
        message = FORCE_SUB_TEMPLATE.format(username=username)
        
        # Build keyboard
        keyboard = force_subscribe_keyboard(
            channels=unsubscribed_channels,
            try_again_link=try_again_link
        )
        
        return message, keyboard
    
    except Exception as e:
        logger.error(f"Error building force sub message: {e}")
        
        # Return basic message and keyboard on error
        message = (
            f"❝ » HEY, {username} ×~ ❞\n\n"
            "YOUR FILE IS READY ‼️ LOOKS LIKE YOU HAVEN'T SUBSCRIBED TO OUR CHANNELS YET,\n"
            "SUBSCRIBE NOW TO GET YOUR FILES."
        )
        
        keyboard = force_subscribe_keyboard(
            channels=unsubscribed_channels,
            try_again_link=try_again_link
        )
        
        return message, keyboard


async def check_force_subscribe(
    bot: Bot,
    user_id: int,
    username: str,
    post_no: int
) -> Tuple[bool, Optional[str], Optional[InlineKeyboardMarkup]]:
    """
    Check force subscribe and return appropriate message if not subscribed.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        username: User's first name or username
        post_no: Post number for try again link
    
    Returns:
        Tuple of (is_subscribed: bool, message: str or None, keyboard: InlineKeyboardMarkup or None)
    """
    try:
        # Check subscriptions
        is_subscribed_all, unsubscribed_channels = await get_unsubscribed_channels(
            bot=bot,
            user_id=user_id
        )
        
        if is_subscribed_all:
            # User is subscribed to all channels
            return True, None, None
        
        # User not subscribed - build force sub message
        deep_link_data = f"get-{post_no}"
        encoded_data = encode_url_safe(deep_link_data)
        try_again_link = build_deep_link(USER_BOT_USERNAME, encoded_data)
        
        message, keyboard = await build_force_sub_message(
            username=username,
            unsubscribed_channels=unsubscribed_channels,
            try_again_link=try_again_link
        )
        
        return False, message, keyboard
    
    except Exception as e:
        logger.error(f"Error in force subscribe check: {e}", exc_info=True)
        return False, "Error checking subscriptions. Please try again.", None


async def verify_bot_admin_status(
    bot: Bot,
    channel_id: Optional[int] = None,
    channel_username: Optional[str] = None
) -> bool:
    """
    Verify that the bot is an admin in the channel.
    
    Args:
        bot: Telegram bot instance
        channel_id: Channel ID (optional)
        channel_username: Channel username (optional)
    
    Returns:
        True if bot is admin, False otherwise
    """
    try:
        chat_identifier = channel_id if channel_id else channel_username
        
        if not chat_identifier:
            return False
        
        # Get bot's member status
        bot_user = await bot.get_me()
        member = await bot.get_chat_member(
            chat_id=chat_identifier,
            user_id=bot_user.id
        )
        
        # Check if bot is admin or creator
        is_admin = member.status in ['administrator', 'creator']
        
        return is_admin
    
    except Exception as e:
        logger.error(f"Error verifying bot admin status: {e}")
        return False


async def validate_all_channels(bot: Bot) -> Dict[str, Any]:
    """
    Validate all configured channels (check if bot is admin).
    
    Args:
        bot: Telegram bot instance
    
    Returns:
        Dictionary with validation results
    """
    try:
        channels = await get_active_channels()
        
        if not channels:
            return {
                'total': 0,
                'valid': 0,
                'invalid': 0,
                'invalid_channels': []
            }
        
        valid_count = 0
        invalid_channels = []
        
        for channel in channels:
            channel_id = channel.get('channel_id')
            channel_username = channel.get('channel_username')
            
            is_admin = await verify_bot_admin_status(
                bot=bot,
                channel_id=channel_id,
                channel_username=channel_username
            )
            
            if is_admin:
                valid_count += 1
            else:
                invalid_channels.append({
                    'channel_username': channel_username,
                    'button_text': channel.get('button_text')
                })
        
        return {
            'total': len(channels),
            'valid': valid_count,
            'invalid': len(invalid_channels),
            'invalid_channels': invalid_channels
        }
    
    except Exception as e:
        logger.error(f"Error validating channels: {e}")
        return {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'invalid_channels': [],
            'error': str(e)
        }


async def get_channel_info(
    bot: Bot,
    channel_id: Optional[int] = None,
    channel_username: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get information about a channel.
    
    Args:
        bot: Telegram bot instance
        channel_id: Channel ID (optional)
        channel_username: Channel username (optional)
    
    Returns:
        Dictionary with channel info or None
    """
    try:
        chat_identifier = channel_id if channel_id else channel_username
        
        if not chat_identifier:
            return None
        
        chat = await bot.get_chat(chat_id=chat_identifier)
        
        return {
            'id': chat.id,
            'title': chat.title,
            'username': chat.username,
            'type': chat.type,
            'member_count': await get_channel_member_count(bot, chat.id)
        }
    
    except Exception as e:
        logger.error(f"Error getting channel info: {e}")
        return None


async def get_channel_member_count(
    bot: Bot,
    channel_id: int
) -> Optional[int]:
    """
    Get member count of a channel.
    
    Args:
        bot: Telegram bot instance
        channel_id: Channel ID
    
    Returns:
        Member count or None
    """
    try:
        count = await bot.get_chat_member_count(chat_id=channel_id)
        return count
    
    except Exception as e:
        logger.warning(f"Error getting member count: {e}")
        return None


async def is_user_banned(
    bot: Bot,
    user_id: int,
    channel_id: Optional[int] = None,
    channel_username: Optional[str] = None
) -> bool:
    """
    Check if user is banned/kicked from a channel.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        channel_id: Channel ID (optional)
        channel_username: Channel username (optional)
    
    Returns:
        True if banned, False otherwise
    """
    try:
        chat_identifier = channel_id if channel_id else channel_username
        
        if not chat_identifier:
            return False
        
        member = await bot.get_chat_member(
            chat_id=chat_identifier,
            user_id=user_id
        )
        
        return member.status == 'kicked'
    
    except Exception as e:
        logger.warning(f"Error checking ban status: {e}")
        return False


async def get_subscription_status_details(
    bot: Bot,
    user_id: int
) -> Dict[str, Any]:
    """
    Get detailed subscription status for all channels.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
    
    Returns:
        Dictionary with detailed subscription status
    """
    try:
        channels = await get_active_channels()
        
        if not channels:
            return {
                'total_channels': 0,
                'subscribed': 0,
                'not_subscribed': 0,
                'all_subscribed': True,
                'channels': []
            }
        
        channel_details = []
        subscribed_count = 0
        
        for channel in channels:
            channel_id = channel.get('channel_id')
            channel_username = channel.get('channel_username')
            button_text = channel.get('button_text')
            
            is_subscribed = await check_user_subscribed(
                bot=bot,
                user_id=user_id,
                channel_id=channel_id,
                channel_username=channel_username
            )
            
            if is_subscribed:
                subscribed_count += 1
            
            channel_details.append({
                'channel_username': channel_username,
                'button_text': button_text,
                'is_subscribed': is_subscribed,
                'channel_link': channel.get('channel_link')
            })
        
        return {
            'total_channels': len(channels),
            'subscribed': subscribed_count,
            'not_subscribed': len(channels) - subscribed_count,
            'all_subscribed': subscribed_count == len(channels),
            'channels': channel_details
        }
    
    except Exception as e:
        logger.error(f"Error getting subscription status details: {e}")
        return {
            'total_channels': 0,
            'subscribed': 0,
            'not_subscribed': 0,
            'all_subscribed': False,
            'channels': [],
            'error': str(e)
        }