"""
Channels Database Operations
CRUD operations for force subscribe channels.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from config.database import get_collection

logger = logging.getLogger(__name__)


async def add_channel(
    channel_username: str,
    channel_link: str,
    button_text: str,
    channel_id: Optional[int] = None,
    added_by: Optional[int] = None
) -> Optional[str]:
    """
    Add a new force subscribe channel.
    
    Args:
        channel_username: Channel username or ID
        channel_link: Channel invite link
        button_text: Button text for the channel
        channel_id: Telegram channel ID (optional)
        added_by: Admin user ID who added the channel
    
    Returns:
        Channel ID (MongoDB ObjectId as string) if successful, None otherwise
    """
    try:
        collection = get_collection('force_sub_channels')
        
        # Check if channel already exists
        existing = collection.find_one({'channel_username': channel_username})
        if existing:
            logger.warning(f"Channel {channel_username} already exists")
            return None
        
        # Get next order number
        max_order_doc = collection.find_one(
            {},
            sort=[('order', -1)]
        )
        next_order = (max_order_doc['order'] + 1) if max_order_doc and 'order' in max_order_doc else 1
        
        # Create channel document
        channel_doc = {
            'channel_username': channel_username,
            'channel_link': channel_link,
            'button_text': button_text,
            'order': next_order,
            'is_active': True,
            'added_at': datetime.now()
        }
        
        if channel_id:
            channel_doc['channel_id'] = channel_id
        
        if added_by:
            channel_doc['added_by'] = added_by
        
        result = collection.insert_one(channel_doc)
        
        logger.info(f"Added channel: {channel_username}")
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Error adding channel: {e}", exc_info=True)
        return None


async def get_channel_by_id(channel_id: str) -> Optional[Dict[str, Any]]:
    """
    Get channel by MongoDB ObjectId.
    
    Args:
        channel_id: MongoDB ObjectId as string
    
    Returns:
        Channel document or None
    """
    try:
        collection = get_collection('force_sub_channels')
        
        channel = collection.find_one({'_id': ObjectId(channel_id)})
        
        if channel:
            channel['_id'] = str(channel['_id'])
        
        return channel
    
    except Exception as e:
        logger.error(f"Error getting channel by ID: {e}", exc_info=True)
        return None


async def get_channel_by_username(channel_username: str) -> Optional[Dict[str, Any]]:
    """
    Get channel by username.
    
    Args:
        channel_username: Channel username or ID
    
    Returns:
        Channel document or None
    """
    try:
        collection = get_collection('force_sub_channels')
        
        channel = collection.find_one({'channel_username': channel_username})
        
        if channel:
            channel['_id'] = str(channel['_id'])
        
        return channel
    
    except Exception as e:
        logger.error(f"Error getting channel by username: {e}", exc_info=True)
        return None


async def get_all_channels() -> List[Dict[str, Any]]:
    """
    Get all force subscribe channels.
    
    Returns:
        List of channel documents
    """
    try:
        collection = get_collection('force_sub_channels')
        
        channels = list(collection.find().sort('order', 1))
        
        # Convert ObjectId to string
        for channel in channels:
            channel['_id'] = str(channel['_id'])
        
        return channels
    
    except Exception as e:
        logger.error(f"Error getting all channels: {e}", exc_info=True)
        return []


async def get_active_channels() -> List[Dict[str, Any]]:
    """
    Get only active force subscribe channels.
    
    Returns:
        List of active channel documents
    """
    try:
        collection = get_collection('force_sub_channels')
        
        channels = list(collection.find({'is_active': True}).sort('order', 1))
        
        # Convert ObjectId to string
        for channel in channels:
            channel['_id'] = str(channel['_id'])
        
        return channels
    
    except Exception as e:
        logger.error(f"Error getting active channels: {e}", exc_info=True)
        return []


async def update_channel(
    channel_id: str,
    updates: Dict[str, Any]
) -> bool:
    """
    Update channel details.
    
    Args:
        channel_id: MongoDB ObjectId as string
        updates: Dictionary of fields to update
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('force_sub_channels')
        
        # Add update timestamp
        updates['updated_at'] = datetime.now()
        
        result = collection.update_one(
            {'_id': ObjectId(channel_id)},
            {'$set': updates}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated channel: {channel_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error updating channel: {e}", exc_info=True)
        return False


async def remove_channel(channel_id: str) -> bool:
    """
    Remove a force subscribe channel.
    
    Args:
        channel_id: MongoDB ObjectId as string
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('force_sub_channels')
        
        result = collection.delete_one({'_id': ObjectId(channel_id)})
        
        if result.deleted_count > 0:
            logger.info(f"Removed channel: {channel_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error removing channel: {e}", exc_info=True)
        return False


async def toggle_channel_status(channel_id: str) -> bool:
    """
    Toggle channel active status.
    
    Args:
        channel_id: MongoDB ObjectId as string
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('force_sub_channels')
        
        # Get current status
        channel = collection.find_one({'_id': ObjectId(channel_id)})
        
        if not channel:
            return False
        
        new_status = not channel.get('is_active', True)
        
        result = collection.update_one(
            {'_id': ObjectId(channel_id)},
            {
                '$set': {
                    'is_active': new_status,
                    'updated_at': datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Toggled channel {channel_id} status to {new_status}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error toggling channel status: {e}", exc_info=True)
        return False


async def reorder_channels(channel_orders: Dict[str, int]) -> bool:
    """
    Reorder channels.
    
    Args:
        channel_orders: Dictionary mapping channel_id to new order number
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('force_sub_channels')
        
        for channel_id, order in channel_orders.items():
            collection.update_one(
                {'_id': ObjectId(channel_id)},
                {'$set': {'order': order, 'updated_at': datetime.now()}}
            )
        
        logger.info(f"Reordered {len(channel_orders)} channels")
        return True
    
    except Exception as e:
        logger.error(f"Error reordering channels: {e}", exc_info=True)
        return False


async def get_channels_count() -> int:
    """
    Get total number of channels.
    
    Returns:
        Number of channels
    """
    try:
        collection = get_collection('force_sub_channels')
        return collection.count_documents({})
    
    except Exception as e:
        logger.error(f"Error getting channels count: {e}", exc_info=True)
        return 0


async def get_active_channels_count() -> int:
    """
    Get number of active channels.
    
    Returns:
        Number of active channels
    """
    try:
        collection = get_collection('force_sub_channels')
        return collection.count_documents({'is_active': True})
    
    except Exception as e:
        logger.error(f"Error getting active channels count: {e}", exc_info=True)
        return 0


async def channel_exists(channel_username: str) -> bool:
    """
    Check if a channel already exists.
    
    Args:
        channel_username: Channel username or ID
    
    Returns:
        True if exists, False otherwise
    """
    try:
        collection = get_collection('force_sub_channels')
        
        count = collection.count_documents({'channel_username': channel_username})
        return count > 0
    
    except Exception as e:
        logger.error(f"Error checking channel existence: {e}", exc_info=True)
        return False


async def bulk_update_channel_status(channel_ids: List[str], is_active: bool) -> int:
    """
    Bulk update channel status.
    
    Args:
        channel_ids: List of channel IDs
        is_active: New active status
    
    Returns:
        Number of channels updated
    """
    try:
        collection = get_collection('force_sub_channels')
        
        object_ids = [ObjectId(cid) for cid in channel_ids]
        
        result = collection.update_many(
            {'_id': {'$in': object_ids}},
            {
                '$set': {
                    'is_active': is_active,
                    'updated_at': datetime.now()
                }
            }
        )
        
        logger.info(f"Bulk updated {result.modified_count} channels")
        return result.modified_count
    
    except Exception as e:
        logger.error(f"Error in bulk update: {e}", exc_info=True)
        return 0


async def delete_all_inactive_channels() -> int:
    """
    Delete all inactive channels.
    
    Returns:
        Number of channels deleted
    """
    try:
        collection = get_collection('force_sub_channels')
        
        result = collection.delete_many({'is_active': False})
        
        logger.info(f"Deleted {result.deleted_count} inactive channels")
        return result.deleted_count
    
    except Exception as e:
        logger.error(f"Error deleting inactive channels: {e}", exc_info=True)
        return 0