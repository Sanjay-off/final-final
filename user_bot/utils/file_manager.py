"""
File Manager for User Bot
Handles file sending, auto-deletion, and file delivery management.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from telegram import Bot, Message, InlineKeyboardMarkup
from telegram.error import TelegramError

from database.operations.files import increment_download_count
from database.operations.users import increment_user_file_access
from user_bot.keyboards.inline import file_deleted_keyboard
from shared.constants import AUTO_DELETE_MINUTES, FILE_DELETED_TEMPLATE
from shared.utils import build_deep_link
from shared.encryption import encode_url_safe
from config.settings import USER_BOT_USERNAME

logger = logging.getLogger(__name__)


async def send_file_with_autodelete(
    bot: Bot,
    user_id: int,
    file_id: str,
    caption: str,
    post_no: int,
    auto_delete_minutes: int = AUTO_DELETE_MINUTES
) -> bool:
    """
    Send file to user with auto-delete functionality.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        file_id: Telegram file ID to send
        caption: File caption (password)
        post_no: Post number for re-download link
        auto_delete_minutes: Minutes until auto-delete (default: 10)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Send the file
        file_message = await bot.send_document(
            chat_id=user_id,
            document=file_id,
            caption=caption
        )
        
        # Send auto-delete warning
        warning_message = await send_autodelete_warning(
            bot=bot,
            user_id=user_id,
            minutes=auto_delete_minutes
        )
        
        # Update database
        await increment_download_count(post_no)
        await increment_user_file_access(user_id, post_no)
        
        # Schedule deletion
        await schedule_file_deletion(
            bot=bot,
            user_id=user_id,
            message_ids=[file_message.message_id, warning_message.message_id],
            post_no=post_no,
            delay_seconds=auto_delete_minutes * 60
        )
        
        logger.info(f"File sent to user {user_id}, post {post_no}, auto-delete in {auto_delete_minutes} min")
        return True
    
    except Exception as e:
        logger.error(f"Error sending file with auto-delete: {e}", exc_info=True)
        return False


async def send_autodelete_warning(
    bot: Bot,
    user_id: int,
    minutes: int
) -> Optional[Message]:
    """
    Send auto-delete warning message.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        minutes: Minutes until deletion
    
    Returns:
        Message object if successful, None otherwise
    """
    try:
        warning_text = (
            f"⚠️ TELEGRAM MF DONT LIKE IT SO....\n\n"
            f"YOUR FILES WILL BE DELETED WITHIN **{minutes} MINUTES**. "
            f"SO PLEASE FORWARD THEM TO ANY OTHER PLACE FOR FUTURE AVAILABILITY."
        )
        
        message = await bot.send_message(
            chat_id=user_id,
            text=warning_text
        )
        
        return message
    
    except Exception as e:
        logger.error(f"Error sending auto-delete warning: {e}")
        return None


async def schedule_file_deletion(
    bot: Bot,
    user_id: int,
    message_ids: List[int],
    post_no: int,
    delay_seconds: int
) -> None:
    """
    Schedule messages for deletion and send replacement message.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        message_ids: List of message IDs to delete
        post_no: Post number for re-download link
        delay_seconds: Delay in seconds before deletion
    """
    try:
        # Wait for specified delay
        await asyncio.sleep(delay_seconds)
        
        # Delete messages
        deleted = await delete_messages(bot, user_id, message_ids)
        
        if deleted:
            # Send replacement message with re-download option
            await send_file_deleted_notification(
                bot=bot,
                user_id=user_id,
                post_no=post_no
            )
            
            logger.info(f"Deleted {len(message_ids)} messages for user {user_id}, post {post_no}")
    
    except Exception as e:
        logger.error(f"Error in scheduled deletion: {e}", exc_info=True)


async def delete_messages(
    bot: Bot,
    chat_id: int,
    message_ids: List[int]
) -> bool:
    """
    Delete multiple messages.
    
    Args:
        bot: Telegram bot instance
        chat_id: Chat ID
        message_ids: List of message IDs to delete
    
    Returns:
        True if all deleted successfully, False otherwise
    """
    try:
        success_count = 0
        
        for message_id in message_ids:
            try:
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=message_id
                )
                success_count += 1
            except TelegramError as e:
                logger.warning(f"Could not delete message {message_id}: {e}")
        
        return success_count == len(message_ids)
    
    except Exception as e:
        logger.error(f"Error deleting messages: {e}")
        return False


async def send_file_deleted_notification(
    bot: Bot,
    user_id: int,
    post_no: int
) -> Optional[Message]:
    """
    Send notification after files are deleted with re-download option.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        post_no: Post number for re-download
    
    Returns:
        Message object if successful, None otherwise
    """
    try:
        # Generate deep link for re-download
        deep_link_data = f"get-{post_no}"
        encoded_data = encode_url_safe(deep_link_data)
        download_link = build_deep_link(USER_BOT_USERNAME, encoded_data)
        
        # Build keyboard
        keyboard = file_deleted_keyboard(download_link)
        
        # Send notification
        message = await bot.send_message(
            chat_id=user_id,
            text=FILE_DELETED_TEMPLATE,
            reply_markup=keyboard
        )
        
        return message
    
    except Exception as e:
        logger.error(f"Error sending file deleted notification: {e}")
        return None


async def send_file_to_user(
    bot: Bot,
    user_id: int,
    file_id: str,
    password: str,
    post_no: int
) -> bool:
    """
    Send file to user with password caption and auto-delete.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        file_id: Telegram file ID
        password: File password
        post_no: Post number
    
    Returns:
        True if successful, False otherwise
    """
    try:
        caption = f"password - {password}"
        
        return await send_file_with_autodelete(
            bot=bot,
            user_id=user_id,
            file_id=file_id,
            caption=caption,
            post_no=post_no
        )
    
    except Exception as e:
        logger.error(f"Error sending file to user: {e}")
        return False


async def can_resend_file(user_id: int, post_no: int) -> bool:
    """
    Check if user can re-download a file (doesn't count against limit if already accessed).
    
    Args:
        user_id: User's Telegram ID
        post_no: Post number
    
    Returns:
        True if can resend, False otherwise
    """
    try:
        from database.operations.users import get_user_by_id
        
        user = await get_user_by_id(user_id)
        
        if not user:
            return False
        
        # Check if file was already accessed (shouldn't count against limit again)
        files_accessed = user.get('files_accessed', [])
        
        return post_no in files_accessed
    
    except Exception as e:
        logger.error(f"Error checking file resend eligibility: {e}")
        return False


async def get_file_from_storage(
    bot: Bot,
    storage_channel_id: int,
    storage_message_id: int
) -> Optional[str]:
    """
    Retrieve file ID from storage channel.
    
    Args:
        bot: Telegram bot instance
        storage_channel_id: Storage channel ID
        storage_message_id: Message ID in storage channel
    
    Returns:
        File ID if found, None otherwise
    """
    try:
        message = await bot.forward_message(
            chat_id=storage_channel_id,
            from_chat_id=storage_channel_id,
            message_id=storage_message_id
        )
        
        # Extract file ID
        if message.document:
            file_id = message.document.file_id
            
            # Delete the forwarded message
            try:
                await bot.delete_message(
                    chat_id=storage_channel_id,
                    message_id=message.message_id
                )
            except:
                pass
            
            return file_id
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting file from storage: {e}")
        return None


async def copy_file_from_storage(
    bot: Bot,
    user_id: int,
    storage_channel_id: int,
    storage_message_id: int,
    caption: str
) -> Optional[Message]:
    """
    Copy file from storage channel to user.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        storage_channel_id: Storage channel ID
        storage_message_id: Message ID in storage channel
        caption: Caption for the file
    
    Returns:
        Sent message object if successful, None otherwise
    """
    try:
        message = await bot.copy_message(
            chat_id=user_id,
            from_chat_id=storage_channel_id,
            message_id=storage_message_id,
            caption=caption
        )
        
        return message
    
    except Exception as e:
        logger.error(f"Error copying file from storage: {e}")
        return None


async def schedule_multiple_deletions(
    bot: Bot,
    deletions: List[dict]
) -> None:
    """
    Schedule multiple file deletions.
    
    Args:
        bot: Telegram bot instance
        deletions: List of deletion configs with keys:
            - user_id: int
            - message_ids: List[int]
            - post_no: int
            - delay_seconds: int
    """
    try:
        tasks = []
        
        for deletion in deletions:
            task = schedule_file_deletion(
                bot=bot,
                user_id=deletion['user_id'],
                message_ids=deletion['message_ids'],
                post_no=deletion['post_no'],
                delay_seconds=deletion['delay_seconds']
            )
            tasks.append(task)
        
        # Run all deletions concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
    
    except Exception as e:
        logger.error(f"Error scheduling multiple deletions: {e}")


async def cleanup_old_messages(
    bot: Bot,
    user_id: int,
    older_than_minutes: int = 60
) -> int:
    """
    Cleanup old messages for a user (placeholder for future implementation).
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        older_than_minutes: Delete messages older than this
    
    Returns:
        Number of messages deleted
    """
    # This would require storing message IDs in database
    # Placeholder for future implementation
    logger.info(f"Cleanup requested for user {user_id}, older than {older_than_minutes} min")
    return 0