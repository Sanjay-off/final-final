"""
Logs Database Operations
Operations for admin action logging and audit trails.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId

from config.database import get_collection

logger = logging.getLogger(__name__)


async def log_admin_action(
    admin_id: int,
    action: str,
    details: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Log an admin action.
    
    Args:
        admin_id: Admin user ID
        action: Action performed (e.g., 'upload_file', 'verify_user')
        details: Additional details about the action
    
    Returns:
        Log ID (MongoDB ObjectId as string) if successful, None otherwise
    """
    try:
        collection = get_collection('admin_logs')
        
        log_doc = {
            'admin_id': admin_id,
            'action': action,
            'details': details or {},
            'timestamp': datetime.now()
        }
        
        result = collection.insert_one(log_doc)
        
        logger.debug(f"Logged action '{action}' by admin {admin_id}")
        return str(result.inserted_id)
    
    except Exception as e:
        logger.error(f"Error logging admin action: {e}", exc_info=True)
        return None


async def get_admin_logs(
    limit: Optional[int] = 100,
    skip: int = 0,
    sort_by: str = 'timestamp',
    descending: bool = True
) -> List[Dict[str, Any]]:
    """
    Get admin logs with pagination.
    
    Args:
        limit: Maximum number of logs to return
        skip: Number of logs to skip
        sort_by: Field to sort by
        descending: Sort in descending order
    
    Returns:
        List of log documents
    """
    try:
        collection = get_collection('admin_logs')
        
        sort_order = -1 if descending else 1
        cursor = collection.find().sort(sort_by, sort_order).skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        
        logs = list(cursor)
        
        # Convert ObjectId to string
        for log in logs:
            log['_id'] = str(log['_id'])
        
        return logs
    
    except Exception as e:
        logger.error(f"Error getting admin logs: {e}", exc_info=True)
        return []


async def get_logs_by_admin(
    admin_id: int,
    limit: Optional[int] = 50
) -> List[Dict[str, Any]]:
    """
    Get logs for a specific admin.
    
    Args:
        admin_id: Admin user ID
        limit: Maximum number of logs to return
    
    Returns:
        List of log documents
    """
    try:
        collection = get_collection('admin_logs')
        
        cursor = collection.find({'admin_id': admin_id}).sort('timestamp', -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        logs = list(cursor)
        
        # Convert ObjectId to string
        for log in logs:
            log['_id'] = str(log['_id'])
        
        return logs
    
    except Exception as e:
        logger.error(f"Error getting logs by admin: {e}", exc_info=True)
        return []


async def get_logs_by_action(
    action: str,
    limit: Optional[int] = 50
) -> List[Dict[str, Any]]:
    """
    Get logs for a specific action type.
    
    Args:
        action: Action type
        limit: Maximum number of logs to return
    
    Returns:
        List of log documents
    """
    try:
        collection = get_collection('admin_logs')
        
        cursor = collection.find({'action': action}).sort('timestamp', -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        logs = list(cursor)
        
        # Convert ObjectId to string
        for log in logs:
            log['_id'] = str(log['_id'])
        
        return logs
    
    except Exception as e:
        logger.error(f"Error getting logs by action: {e}", exc_info=True)
        return []


async def get_recent_logs(
    hours: int = 24,
    limit: Optional[int] = 100
) -> List[Dict[str, Any]]:
    """
    Get recent logs from the last N hours.
    
    Args:
        hours: Number of hours to look back
        limit: Maximum number of logs to return
    
    Returns:
        List of log documents
    """
    try:
        collection = get_collection('admin_logs')
        
        since_time = datetime.now() - timedelta(hours=hours)
        
        cursor = collection.find({
            'timestamp': {'$gte': since_time}
        }).sort('timestamp', -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        logs = list(cursor)
        
        # Convert ObjectId to string
        for log in logs:
            log['_id'] = str(log['_id'])
        
        return logs
    
    except Exception as e:
        logger.error(f"Error getting recent logs: {e}", exc_info=True)
        return []


async def get_logs_by_date_range(
    start_date: datetime,
    end_date: datetime,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get logs within a date range.
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        limit: Maximum number of logs to return
    
    Returns:
        List of log documents
    """
    try:
        collection = get_collection('admin_logs')
        
        cursor = collection.find({
            'timestamp': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('timestamp', -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        logs = list(cursor)
        
        # Convert ObjectId to string
        for log in logs:
            log['_id'] = str(log['_id'])
        
        return logs
    
    except Exception as e:
        logger.error(f"Error getting logs by date range: {e}", exc_info=True)
        return []


async def get_logs_count(
    admin_id: Optional[int] = None,
    action: Optional[str] = None,
    since: Optional[datetime] = None
) -> int:
    """
    Get count of logs with optional filters.
    
    Args:
        admin_id: Filter by admin ID
        action: Filter by action type
        since: Filter by timestamp (logs after this time)
    
    Returns:
        Number of logs
    """
    try:
        collection = get_collection('admin_logs')
        
        query = {}
        
        if admin_id:
            query['admin_id'] = admin_id
        
        if action:
            query['action'] = action
        
        if since:
            query['timestamp'] = {'$gte': since}
        
        return collection.count_documents(query)
    
    except Exception as e:
        logger.error(f"Error getting logs count: {e}", exc_info=True)
        return 0


async def get_admin_activity_stats(admin_id: int) -> Dict[str, Any]:
    """
    Get activity statistics for a specific admin.
    
    Args:
        admin_id: Admin user ID
    
    Returns:
        Dictionary with activity statistics
    """
    try:
        collection = get_collection('admin_logs')
        
        # Total actions
        total_actions = collection.count_documents({'admin_id': admin_id})
        
        # Actions by type
        pipeline = [
            {'$match': {'admin_id': admin_id}},
            {
                '$group': {
                    '_id': '$action',
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        actions_by_type = list(collection.aggregate(pipeline))
        
        # Recent activity (last 24 hours)
        last_24h = datetime.now() - timedelta(hours=24)
        recent_actions = collection.count_documents({
            'admin_id': admin_id,
            'timestamp': {'$gte': last_24h}
        })
        
        # First and last action
        first_action = collection.find_one(
            {'admin_id': admin_id},
            sort=[('timestamp', 1)]
        )
        
        last_action = collection.find_one(
            {'admin_id': admin_id},
            sort=[('timestamp', -1)]
        )
        
        stats = {
            'admin_id': admin_id,
            'total_actions': total_actions,
            'recent_actions_24h': recent_actions,
            'actions_by_type': [
                {'action': item['_id'], 'count': item['count']}
                for item in actions_by_type
            ],
            'first_action_at': first_action['timestamp'] if first_action else None,
            'last_action_at': last_action['timestamp'] if last_action else None
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting admin activity stats: {e}", exc_info=True)
        return {}


async def get_action_statistics() -> Dict[str, Any]:
    """
    Get overall action statistics.
    
    Returns:
        Dictionary with action statistics
    """
    try:
        collection = get_collection('admin_logs')
        
        # Total logs
        total_logs = collection.count_documents({})
        
        # Logs by action type
        pipeline = [
            {
                '$group': {
                    '_id': '$action',
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'count': -1}}
        ]
        
        actions = list(collection.aggregate(pipeline))
        
        # Active admins (unique admin IDs)
        active_admins = collection.distinct('admin_id')
        
        # Recent activity
        last_24h = datetime.now() - timedelta(hours=24)
        recent_logs = collection.count_documents({
            'timestamp': {'$gte': last_24h}
        })
        
        stats = {
            'total_logs': total_logs,
            'active_admins_count': len(active_admins),
            'recent_logs_24h': recent_logs,
            'actions_breakdown': [
                {'action': item['_id'], 'count': item['count']}
                for item in actions
            ]
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting action statistics: {e}", exc_info=True)
        return {}


async def cleanup_old_logs(days: int = 90) -> int:
    """
    Delete logs older than specified days.
    
    Args:
        days: Number of days to keep logs
    
    Returns:
        Number of logs deleted
    """
    try:
        collection = get_collection('admin_logs')
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = collection.delete_many({
            'timestamp': {'$lt': cutoff_date}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old logs (older than {days} days)")
        return result.deleted_count
    
    except Exception as e:
        logger.error(f"Error cleaning up old logs: {e}", exc_info=True)
        return 0


async def search_logs(
    query: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Search logs by action or details.
    
    Args:
        query: Search query
        limit: Maximum number of results
    
    Returns:
        List of matching log documents
    """
    try:
        collection = get_collection('admin_logs')
        
        # Case-insensitive search
        regex_query = {'$regex': query, '$options': 'i'}
        
        logs = list(
            collection.find({
                'action': regex_query
            })
            .sort('timestamp', -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for log in logs:
            log['_id'] = str(log['_id'])
        
        return logs
    
    except Exception as e:
        logger.error(f"Error searching logs: {e}", exc_info=True)
        return []


async def delete_logs_by_admin(admin_id: int) -> int:
    """
    Delete all logs for a specific admin.
    
    Args:
        admin_id: Admin user ID
    
    Returns:
        Number of logs deleted
    """
    try:
        collection = get_collection('admin_logs')
        
        result = collection.delete_many({'admin_id': admin_id})
        
        logger.info(f"Deleted {result.deleted_count} logs for admin {admin_id}")
        return result.deleted_count
    
    except Exception as e:
        logger.error(f"Error deleting logs by admin: {e}", exc_info=True)
        return 0


async def get_most_active_admins(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get most active admins by action count.
    
    Args:
        limit: Maximum number of admins to return
    
    Returns:
        List of admin activity summaries
    """
    try:
        collection = get_collection('admin_logs')
        
        pipeline = [
            {
                '$group': {
                    '_id': '$admin_id',
                    'action_count': {'$sum': 1},
                    'last_action': {'$max': '$timestamp'}
                }
            },
            {'$sort': {'action_count': -1}},
            {'$limit': limit}
        ]
        
        admins = list(collection.aggregate(pipeline))
        
        result = [
            {
                'admin_id': item['_id'],
                'action_count': item['action_count'],
                'last_action': item['last_action']
            }
            for item in admins
        ]
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting most active admins: {e}", exc_info=True)
        return []


async def get_log_by_id(log_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific log by ID.
    
    Args:
        log_id: MongoDB ObjectId as string
    
    Returns:
        Log document or None
    """
    try:
        collection = get_collection('admin_logs')
        
        log = collection.find_one({'_id': ObjectId(log_id)})
        
        if log:
            log['_id'] = str(log['_id'])
        
        return log
    
    except Exception as e:
        logger.error(f"Error getting log by ID: {e}", exc_info=True)
        return None