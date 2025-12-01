"""
Files Database Operations
CRUD operations for file records and statistics.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId

from config.database import get_collection

logger = logging.getLogger(__name__)


async def add_file(
    post_no: int,
    context: str,
    extra_message: str,
    file_id: str,
    file_name: str,
    storage_message_id: int,
    public_message_id: int,
    password: str,
    created_by: int
) -> Optional[str]:
    """
    Add a new file record.
    
    Args:
        post_no: Unique post number
        context: Context/title of the file
        extra_message: Additional message
        file_id: Telegram file ID
        file_name: Original filename
        storage_message_id: Message ID in storage channel
        public_message_id: Message ID in public group
        password: File password
        created_by: Admin user ID who created
    
    Returns:
        File ID (MongoDB ObjectId as string) if successful, None otherwise
    """
    try:
        collection = get_collection('files')
        
        # Check if post_no already exists
        existing = collection.find_one({'post_no': post_no})
        if existing:
            logger.warning(f"Post number {post_no} already exists")
            return None
        
        # Create file document
        file_doc = {
            'post_no': post_no,
            'context': context,
            'extra_message': extra_message,
            'file_id': file_id,
            'file_name': file_name,
            'storage_message_id': storage_message_id,
            'public_message_id': public_message_id,
            'password': password,
            'download_count': 0,
            'created_by': created_by,
            'created_at': datetime.now()
        }
        
        result = collection.insert_one(file_doc)
        
        logger.info(f"Added file: Post #{post_no}")
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Error adding file: {e}", exc_info=True)
        return None


async def get_file_by_post_no(post_no: int) -> Optional[Dict[str, Any]]:
    """
    Get file by post number.
    
    Args:
        post_no: Post number
    
    Returns:
        File document or None
    """
    try:
        collection = get_collection('files')
        
        file = collection.find_one({'post_no': post_no})
        
        if file:
            file['_id'] = str(file['_id'])
        
        return file
    
    except Exception as e:
        logger.error(f"Error getting file by post_no: {e}", exc_info=True)
        return None


async def get_file_by_id(file_id: str) -> Optional[Dict[str, Any]]:
    """
    Get file by MongoDB ObjectId.
    
    Args:
        file_id: MongoDB ObjectId as string
    
    Returns:
        File document or None
    """
    try:
        collection = get_collection('files')
        
        file = collection.find_one({'_id': ObjectId(file_id)})
        
        if file:
            file['_id'] = str(file['_id'])
        
        return file
    
    except Exception as e:
        logger.error(f"Error getting file by ID: {e}", exc_info=True)
        return None


async def get_all_files(
    limit: Optional[int] = None,
    skip: int = 0,
    sort_by: str = 'created_at',
    descending: bool = True
) -> List[Dict[str, Any]]:
    """
    Get all files with pagination and sorting.
    
    Args:
        limit: Maximum number of files to return
        skip: Number of files to skip
        sort_by: Field to sort by
        descending: Sort in descending order
    
    Returns:
        List of file documents
    """
    try:
        collection = get_collection('files')
        
        sort_order = -1 if descending else 1
        cursor = collection.find().sort(sort_by, sort_order).skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        
        files = list(cursor)
        
        # Convert ObjectId to string
        for file in files:
            file['_id'] = str(file['_id'])
        
        return files
    
    except Exception as e:
        logger.error(f"Error getting all files: {e}", exc_info=True)
        return []


async def update_file(post_no: int, updates: Dict[str, Any]) -> bool:
    """
    Update file details.
    
    Args:
        post_no: Post number
        updates: Dictionary of fields to update
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('files')
        
        # Add update timestamp
        updates['updated_at'] = datetime.now()
        
        result = collection.update_one(
            {'post_no': post_no},
            {'$set': updates}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated file: Post #{post_no}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error updating file: {e}", exc_info=True)
        return False


async def delete_file(post_no: int) -> bool:
    """
    Delete a file record.
    
    Args:
        post_no: Post number
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('files')
        
        result = collection.delete_one({'post_no': post_no})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted file: Post #{post_no}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        return False


async def increment_download_count(post_no: int) -> bool:
    """
    Increment download count for a file.
    
    Args:
        post_no: Post number
    
    Returns:
        True if successful, False otherwise
    """
    try:
        collection = get_collection('files')
        
        result = collection.update_one(
            {'post_no': post_no},
            {
                '$inc': {'download_count': 1},
                '$set': {'last_downloaded_at': datetime.now()}
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Incremented download count for Post #{post_no}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error incrementing download count: {e}", exc_info=True)
        return False


async def get_total_files_count() -> int:
    """
    Get total number of files.
    
    Returns:
        Number of files
    """
    try:
        collection = get_collection('files')
        return collection.count_documents({})
    
    except Exception as e:
        logger.error(f"Error getting files count: {e}", exc_info=True)
        return 0


async def get_total_downloads_count() -> int:
    """
    Get total number of downloads across all files.
    
    Returns:
        Total download count
    """
    try:
        collection = get_collection('files')
        
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_downloads': {'$sum': '$download_count'}
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        
        if result:
            return result[0].get('total_downloads', 0)
        
        return 0
    
    except Exception as e:
        logger.error(f"Error getting total downloads: {e}", exc_info=True)
        return 0


async def get_most_downloaded_files(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get most downloaded files.
    
    Args:
        limit: Maximum number of files to return
    
    Returns:
        List of file documents sorted by download count
    """
    try:
        collection = get_collection('files')
        
        files = list(
            collection.find()
            .sort('download_count', -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for file in files:
            file['_id'] = str(file['_id'])
        
        return files
    
    except Exception as e:
        logger.error(f"Error getting most downloaded files: {e}", exc_info=True)
        return []


async def get_recent_files(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recently uploaded files.
    
    Args:
        days: Number of days to look back
        limit: Maximum number of files to return
    
    Returns:
        List of recent file documents
    """
    try:
        collection = get_collection('files')
        
        since_date = datetime.now() - timedelta(days=days)
        
        files = list(
            collection.find({'created_at': {'$gte': since_date}})
            .sort('created_at', -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for file in files:
            file['_id'] = str(file['_id'])
        
        return files
    
    except Exception as e:
        logger.error(f"Error getting recent files: {e}", exc_info=True)
        return []


async def get_files_by_admin(admin_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get files uploaded by specific admin.
    
    Args:
        admin_id: Admin user ID
        limit: Maximum number of files to return
    
    Returns:
        List of file documents
    """
    try:
        collection = get_collection('files')
        
        cursor = collection.find({'created_by': admin_id}).sort('created_at', -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        files = list(cursor)
        
        # Convert ObjectId to string
        for file in files:
            file['_id'] = str(file['_id'])
        
        return files
    
    except Exception as e:
        logger.error(f"Error getting files by admin: {e}", exc_info=True)
        return []


async def search_files(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search files by context or extra_message.
    
    Args:
        query: Search query
        limit: Maximum number of results
    
    Returns:
        List of matching file documents
    """
    try:
        collection = get_collection('files')
        
        # Case-insensitive search
        regex_query = {'$regex': query, '$options': 'i'}
        
        files = list(
            collection.find({
                '$or': [
                    {'context': regex_query},
                    {'extra_message': regex_query},
                    {'file_name': regex_query}
                ]
            })
            .sort('created_at', -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for file in files:
            file['_id'] = str(file['_id'])
        
        return files
    
    except Exception as e:
        logger.error(f"Error searching files: {e}", exc_info=True)
        return []


async def get_files_stats() -> Dict[str, Any]:
    """
    Get comprehensive file statistics.
    
    Returns:
        Dictionary with file statistics
    """
    try:
        collection = get_collection('files')
        
        total_files = collection.count_documents({})
        total_downloads = await get_total_downloads_count()
        
        # Get average downloads per file
        avg_downloads = total_downloads / total_files if total_files > 0 else 0
        
        # Get most popular file
        most_popular = list(collection.find().sort('download_count', -1).limit(1))
        
        # Get recent uploads
        last_24h = datetime.now() - timedelta(hours=24)
        recent_uploads = collection.count_documents({'created_at': {'$gte': last_24h}})
        
        stats = {
            'total_files': total_files,
            'total_downloads': total_downloads,
            'average_downloads_per_file': round(avg_downloads, 2),
            'recent_uploads_24h': recent_uploads,
            'most_popular_file': most_popular[0] if most_popular else None
        }
        
        if stats['most_popular_file']:
            stats['most_popular_file']['_id'] = str(stats['most_popular_file']['_id'])
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting file stats: {e}", exc_info=True)
        return {}


async def file_exists(post_no: int) -> bool:
    """
    Check if a file with given post number exists.
    
    Args:
        post_no: Post number
    
    Returns:
        True if exists, False otherwise
    """
    try:
        collection = get_collection('files')
        
        count = collection.count_documents({'post_no': post_no})
        return count > 0
    
    except Exception as e:
        logger.error(f"Error checking file existence: {e}", exc_info=True)
        return False


async def bulk_delete_files(post_numbers: List[int]) -> int:
    """
    Delete multiple files by post numbers.
    
    Args:
        post_numbers: List of post numbers
    
    Returns:
        Number of files deleted
    """
    try:
        collection = get_collection('files')
        
        result = collection.delete_many({'post_no': {'$in': post_numbers}})
        
        logger.info(f"Bulk deleted {result.deleted_count} files")
        return result.deleted_count
    
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}", exc_info=True)
        return 0