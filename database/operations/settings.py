"""
Settings Database Operations
CRUD operations for admin settings and configuration.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from config.database import get_collection

logger = logging.getLogger(__name__)


async def get_setting(setting_key: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific setting by key.
    
    Args:
        setting_key: Setting key name
    
    Returns:
        Setting document or None
    """
    try:
        collection = get_collection('admin_settings')
        
        setting = collection.find_one({'setting_key': setting_key})
        
        if setting:
            setting['_id'] = str(setting['_id'])
        
        return setting
    
    except Exception as e:
        logger.error(f"Error getting setting '{setting_key}': {e}", exc_info=True)
        return None


async def get_setting_value(setting_key: str, default: Any = None) -> Any:
    """
    Get only the value of a setting.
    
    Args:
        setting_key: Setting key name
        default: Default value if setting not found
    
    Returns:
        Setting value or default
    """
    try:
        setting = await get_setting(setting_key)
        
        if setting:
            return setting.get('setting_value', default)
        
        return default
    
    except Exception as e:
        logger.error(f"Error getting setting value '{setting_key}': {e}", exc_info=True)
        return default


async def set_setting(
    setting_key: str,
    setting_value: str,
    updated_by: Optional[int] = None
) -> bool:
    """
    Set or update a setting.
    
    Args:
        setting_key: Setting key name
        setting_value: Setting value
        updated_by: Admin user ID who updated
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('admin_settings')
        
        # Check if setting exists
        existing = collection.find_one({'setting_key': setting_key})
        
        setting_doc = {
            'setting_key': setting_key,
            'setting_value': setting_value,
            'updated_at': datetime.now()
        }
        
        if updated_by:
            setting_doc['updated_by'] = updated_by
        
        if existing:
            # Update existing setting
            result = collection.update_one(
                {'setting_key': setting_key},
                {'$set': setting_doc}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated setting: {setting_key}")
                return True
        else:
            # Insert new setting
            result = collection.insert_one(setting_doc)
            
            if result.inserted_id:
                logger.info(f"Created setting: {setting_key}")
                return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error setting '{setting_key}': {e}", exc_info=True)
        return False


async def update_setting(
    setting_key: str,
    setting_value: str,
    updated_by: Optional[int] = None
) -> bool:
    """
    Update an existing setting (alias for set_setting).
    
    Args:
        setting_key: Setting key name
        setting_value: New setting value
        updated_by: Admin user ID who updated
    
    Returns:
        True if successful, False otherwise
    """
    return await set_setting(setting_key, setting_value, updated_by)


async def get_all_settings() -> List[Dict[str, Any]]:
    """
    Get all settings.
    
    Returns:
        List of setting documents
    """
    try:
        collection = get_collection('admin_settings')
        
        settings = list(collection.find().sort('setting_key', 1))
        
        # Convert ObjectId to string
        for setting in settings:
            setting['_id'] = str(setting['_id'])
        
        return settings
    
    except Exception as e:
        logger.error(f"Error getting all settings: {e}", exc_info=True)
        return []


async def get_all_settings_dict() -> Dict[str, str]:
    """
    Get all settings as a key-value dictionary.
    
    Returns:
        Dictionary mapping setting_key to setting_value
    """
    try:
        collection = get_collection('admin_settings')
        
        settings = collection.find()
        
        settings_dict = {
            setting['setting_key']: setting['setting_value']
            for setting in settings
        }
        
        return settings_dict
    
    except Exception as e:
        logger.error(f"Error getting settings dictionary: {e}", exc_info=True)
        return {}


async def delete_setting(setting_key: str) -> bool:
    """
    Delete a setting.
    
    Args:
        setting_key: Setting key name
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('admin_settings')
        
        result = collection.delete_one({'setting_key': setting_key})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted setting: {setting_key}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error deleting setting '{setting_key}': {e}", exc_info=True)
        return False


async def setting_exists(setting_key: str) -> bool:
    """
    Check if a setting exists.
    
    Args:
        setting_key: Setting key name
    
    Returns:
        True if exists, False otherwise
    """
    try:
        collection = get_collection('admin_settings')
        
        count = collection.count_documents({'setting_key': setting_key})
        return count > 0
    
    except Exception as e:
        logger.error(f"Error checking setting existence: {e}", exc_info=True)
        return False


async def get_settings_count() -> int:
    """
    Get total number of settings.
    
    Returns:
        Number of settings
    """
    try:
        collection = get_collection('admin_settings')
        return collection.count_documents({})
    
    except Exception as e:
        logger.error(f"Error getting settings count: {e}", exc_info=True)
        return 0


async def bulk_set_settings(
    settings: Dict[str, str],
    updated_by: Optional[int] = None
) -> int:
    """
    Set multiple settings at once.
    
    Args:
        settings: Dictionary of setting_key: setting_value pairs
        updated_by: Admin user ID who updated
    
    Returns:
        Number of settings updated/created
    """
    try:
        count = 0
        
        for key, value in settings.items():
            success = await set_setting(key, value, updated_by)
            if success:
                count += 1
        
        logger.info(f"Bulk set {count} settings")
        return count
    
    except Exception as e:
        logger.error(f"Error in bulk set settings: {e}", exc_info=True)
        return 0


async def get_settings_by_prefix(prefix: str) -> List[Dict[str, Any]]:
    """
    Get settings with keys starting with a prefix.
    
    Args:
        prefix: Key prefix to search for
    
    Returns:
        List of matching setting documents
    """
    try:
        collection = get_collection('admin_settings')
        
        settings = list(
            collection.find({
                'setting_key': {'$regex': f'^{prefix}', '$options': 'i'}
            }).sort('setting_key', 1)
        )
        
        # Convert ObjectId to string
        for setting in settings:
            setting['_id'] = str(setting['_id'])
        
        return settings
    
    except Exception as e:
        logger.error(f"Error getting settings by prefix: {e}", exc_info=True)
        return []


async def search_settings(query: str) -> List[Dict[str, Any]]:
    """
    Search settings by key or value.
    
    Args:
        query: Search query
    
    Returns:
        List of matching setting documents
    """
    try:
        collection = get_collection('admin_settings')
        
        regex_query = {'$regex': query, '$options': 'i'}
        
        settings = list(
            collection.find({
                '$or': [
                    {'setting_key': regex_query},
                    {'setting_value': regex_query}
                ]
            }).sort('setting_key', 1)
        )
        
        # Convert ObjectId to string
        for setting in settings:
            setting['_id'] = str(setting['_id'])
        
        return settings
    
    except Exception as e:
        logger.error(f"Error searching settings: {e}", exc_info=True)
        return []


async def get_settings_updated_since(since: datetime) -> List[Dict[str, Any]]:
    """
    Get settings updated since a specific datetime.
    
    Args:
        since: Datetime to check from
    
    Returns:
        List of recently updated settings
    """
    try:
        collection = get_collection('admin_settings')
        
        settings = list(
            collection.find({
                'updated_at': {'$gte': since}
            }).sort('updated_at', -1)
        )
        
        # Convert ObjectId to string
        for setting in settings:
            setting['_id'] = str(setting['_id'])
        
        return settings
    
    except Exception as e:
        logger.error(f"Error getting settings updated since: {e}", exc_info=True)
        return []


async def get_settings_updated_by_admin(admin_id: int) -> List[Dict[str, Any]]:
    """
    Get settings updated by a specific admin.
    
    Args:
        admin_id: Admin user ID
    
    Returns:
        List of settings updated by admin
    """
    try:
        collection = get_collection('admin_settings')
        
        settings = list(
            collection.find({
                'updated_by': admin_id
            }).sort('updated_at', -1)
        )
        
        # Convert ObjectId to string
        for setting in settings:
            setting['_id'] = str(setting['_id'])
        
        return settings
    
    except Exception as e:
        logger.error(f"Error getting settings by admin: {e}", exc_info=True)
        return []


async def reset_setting_to_default(setting_key: str, default_value: str) -> bool:
    """
    Reset a setting to its default value.
    
    Args:
        setting_key: Setting key name
        default_value: Default value to set
    
    Returns:
        True if successful, False otherwise
    """
    try:
        return await set_setting(setting_key, default_value, updated_by=0)
    
    except Exception as e:
        logger.error(f"Error resetting setting to default: {e}", exc_info=True)
        return False


async def export_settings() -> Dict[str, str]:
    """
    Export all settings as a dictionary (for backup).
    
    Returns:
        Dictionary of all settings
    """
    try:
        return await get_all_settings_dict()
    
    except Exception as e:
        logger.error(f"Error exporting settings: {e}", exc_info=True)
        return {}


async def import_settings(
    settings: Dict[str, str],
    updated_by: Optional[int] = None,
    overwrite: bool = False
) -> Dict[str, int]:
    """
    Import settings from a dictionary (for restore).
    
    Args:
        settings: Dictionary of settings to import
        updated_by: Admin user ID who imported
        overwrite: Whether to overwrite existing settings
    
    Returns:
        Dictionary with 'created' and 'updated' counts
    """
    try:
        created = 0
        updated = 0
        skipped = 0
        
        for key, value in settings.items():
            exists = await setting_exists(key)
            
            if exists and not overwrite:
                skipped += 1
                continue
            
            success = await set_setting(key, value, updated_by)
            
            if success:
                if exists:
                    updated += 1
                else:
                    created += 1
        
        logger.info(f"Imported settings - Created: {created}, Updated: {updated}, Skipped: {skipped}")
        
        return {
            'created': created,
            'updated': updated,
            'skipped': skipped
        }
    
    except Exception as e:
        logger.error(f"Error importing settings: {e}", exc_info=True)
        return {'created': 0, 'updated': 0, 'skipped': 0}


async def get_setting_history(setting_key: str) -> List[Dict[str, Any]]:
    """
    Get history of a setting (requires logging to be implemented).
    This is a placeholder for future enhancement.
    
    Args:
        setting_key: Setting key name
    
    Returns:
        List of historical values (currently just current value)
    """
    try:
        current = await get_setting(setting_key)
        
        if current:
            return [current]
        
        return []
    
    except Exception as e:
        logger.error(f"Error getting setting history: {e}", exc_info=True)
        return []