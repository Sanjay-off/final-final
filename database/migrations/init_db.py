"""
Database Initialization Migration
Creates initial collections and indexes for the Telegram file distribution system.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from config.database import get_database, create_indexes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_files_collection() -> None:
    """Create files collection with validation schema."""
    db = get_database()
    
    try:
        # Check if collection exists
        if 'files' in db.list_collection_names():
            logger.info("Collection 'files' already exists")
            return
        
        # Create collection with validation
        db.create_collection(
            'files',
            validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['post_no', 'context', 'extra_message', 'file_id', 'created_at'],
                    'properties': {
                        'post_no': {
                            'bsonType': 'int',
                            'description': 'Unique post number'
                        },
                        'context': {
                            'bsonType': 'string',
                            'description': 'Context/title of the file'
                        },
                        'extra_message': {
                            'bsonType': 'string',
                            'description': 'Additional message for the post'
                        },
                        'file_id': {
                            'bsonType': 'string',
                            'description': 'Telegram file ID'
                        },
                        'file_name': {
                            'bsonType': 'string',
                            'description': 'Original filename'
                        },
                        'storage_message_id': {
                            'bsonType': 'int',
                            'description': 'Message ID in storage channel'
                        },
                        'public_message_id': {
                            'bsonType': 'int',
                            'description': 'Message ID in public group'
                        },
                        'password': {
                            'bsonType': 'string',
                            'description': 'File password'
                        },
                        'download_count': {
                            'bsonType': 'int',
                            'description': 'Number of downloads'
                        },
                        'created_by': {
                            'bsonType': 'int',
                            'description': 'Admin user ID who created'
                        },
                        'created_at': {
                            'bsonType': 'date',
                            'description': 'Creation timestamp'
                        }
                    }
                }
            }
        )
        
        logger.info("Collection 'files' created successfully")
    
    except Exception as e:
        logger.error(f"Error creating 'files' collection: {e}")


def create_users_verification_collection() -> None:
    """Create users verification collection."""
    db = get_database()
    
    try:
        if 'users_verification' in db.list_collection_names():
            logger.info("Collection 'users_verification' already exists")
            return
        
        db.create_collection(
            'users_verification',
            validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['user_id', 'is_verified'],
                    'properties': {
                        'user_id': {
                            'bsonType': 'int',
                            'description': 'Telegram user ID'
                        },
                        'username': {
                            'bsonType': 'string',
                            'description': 'Telegram username'
                        },
                        'is_verified': {
                            'bsonType': 'bool',
                            'description': 'Verification status'
                        },
                        'verified_at': {
                            'bsonType': 'date',
                            'description': 'Verification timestamp'
                        },
                        'expires_at': {
                            'bsonType': 'date',
                            'description': 'Verification expiry timestamp'
                        },
                        'files_accessed_count': {
                            'bsonType': 'int',
                            'description': 'Number of files accessed'
                        },
                        'files_accessed': {
                            'bsonType': 'array',
                            'description': 'List of accessed post numbers'
                        },
                        'last_access': {
                            'bsonType': 'date',
                            'description': 'Last access timestamp'
                        }
                    }
                }
            }
        )
        
        logger.info("Collection 'users_verification' created successfully")
    
    except Exception as e:
        logger.error(f"Error creating 'users_verification' collection: {e}")


def create_verification_tokens_collection() -> None:
    """Create verification tokens collection."""
    db = get_database()
    
    try:
        if 'verification_tokens' in db.list_collection_names():
            logger.info("Collection 'verification_tokens' already exists")
            return
        
        db.create_collection(
            'verification_tokens',
            validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['token_id', 'user_id', 'status', 'created_at'],
                    'properties': {
                        'token_id': {
                            'bsonType': 'string',
                            'description': 'Unique token ID'
                        },
                        'user_id': {
                            'bsonType': 'int',
                            'description': 'User ID'
                        },
                        'status': {
                            'enum': ['pending', 'in_progress', 'completed', 'expired'],
                            'description': 'Token status'
                        },
                        'created_at': {
                            'bsonType': 'date',
                            'description': 'Token creation timestamp'
                        },
                        'expires_at': {
                            'bsonType': 'date',
                            'description': 'Token expiry timestamp'
                        },
                        'completed_at': {
                            'bsonType': 'date',
                            'description': 'Completion timestamp'
                        }
                    }
                }
            }
        )
        
        logger.info("Collection 'verification_tokens' created successfully")
    
    except Exception as e:
        logger.error(f"Error creating 'verification_tokens' collection: {e}")


def create_force_sub_channels_collection() -> None:
    """Create force subscribe channels collection."""
    db = get_database()
    
    try:
        if 'force_sub_channels' in db.list_collection_names():
            logger.info("Collection 'force_sub_channels' already exists")
            return
        
        db.create_collection(
            'force_sub_channels',
            validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['channel_username', 'channel_link', 'button_text'],
                    'properties': {
                        'channel_id': {
                            'bsonType': 'int',
                            'description': 'Telegram channel ID'
                        },
                        'channel_username': {
                            'bsonType': 'string',
                            'description': 'Channel username or ID'
                        },
                        'channel_link': {
                            'bsonType': 'string',
                            'description': 'Channel invite link'
                        },
                        'button_text': {
                            'bsonType': 'string',
                            'description': 'Button text for channel'
                        },
                        'order': {
                            'bsonType': 'int',
                            'description': 'Display order'
                        },
                        'is_active': {
                            'bsonType': 'bool',
                            'description': 'Active status'
                        },
                        'added_by': {
                            'bsonType': 'int',
                            'description': 'Admin who added the channel'
                        },
                        'added_at': {
                            'bsonType': 'date',
                            'description': 'Addition timestamp'
                        }
                    }
                }
            }
        )
        
        logger.info("Collection 'force_sub_channels' created successfully")
    
    except Exception as e:
        logger.error(f"Error creating 'force_sub_channels' collection: {e}")


def create_admin_settings_collection() -> None:
    """Create admin settings collection."""
    db = get_database()
    
    try:
        if 'admin_settings' in db.list_collection_names():
            logger.info("Collection 'admin_settings' already exists")
            return
        
        db.create_collection(
            'admin_settings',
            validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['setting_key', 'setting_value'],
                    'properties': {
                        'setting_key': {
                            'bsonType': 'string',
                            'description': 'Setting key name'
                        },
                        'setting_value': {
                            'bsonType': 'string',
                            'description': 'Setting value'
                        },
                        'updated_at': {
                            'bsonType': 'date',
                            'description': 'Last update timestamp'
                        },
                        'updated_by': {
                            'bsonType': 'int',
                            'description': 'Admin who updated'
                        }
                    }
                }
            }
        )
        
        logger.info("Collection 'admin_settings' created successfully")
    
    except Exception as e:
        logger.error(f"Error creating 'admin_settings' collection: {e}")


def create_admin_logs_collection() -> None:
    """Create admin logs collection."""
    db = get_database()
    
    try:
        if 'admin_logs' in db.list_collection_names():
            logger.info("Collection 'admin_logs' already exists")
            return
        
        db.create_collection(
            'admin_logs',
            validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['admin_id', 'action', 'timestamp'],
                    'properties': {
                        'admin_id': {
                            'bsonType': 'int',
                            'description': 'Admin user ID'
                        },
                        'action': {
                            'bsonType': 'string',
                            'description': 'Action performed'
                        },
                        'details': {
                            'bsonType': 'object',
                            'description': 'Additional details'
                        },
                        'timestamp': {
                            'bsonType': 'date',
                            'description': 'Action timestamp'
                        }
                    }
                }
            }
        )
        
        logger.info("Collection 'admin_logs' created successfully")
    
    except Exception as e:
        logger.error(f"Error creating 'admin_logs' collection: {e}")


def insert_default_settings() -> None:
    """Insert default settings if not exist."""
    db = get_database()
    settings_collection = db['admin_settings']
    
    default_settings = [
        {
            'setting_key': 'file_password',
            'setting_value': 'default123',
            'updated_at': datetime.now(),
            'updated_by': 0
        },
        {
            'setting_key': 'verification_period_hours',
            'setting_value': '24',
            'updated_at': datetime.now(),
            'updated_by': 0
        },
        {
            'setting_key': 'file_access_limit',
            'setting_value': '3',
            'updated_at': datetime.now(),
            'updated_by': 0
        }
    ]
    
    for setting in default_settings:
        try:
            # Check if setting exists
            existing = settings_collection.find_one({'setting_key': setting['setting_key']})
            
            if not existing:
                settings_collection.insert_one(setting)
                logger.info(f"Inserted default setting: {setting['setting_key']}")
            else:
                logger.info(f"Setting already exists: {setting['setting_key']}")
        
        except Exception as e:
            logger.error(f"Error inserting setting {setting['setting_key']}: {e}")


def initialize_database() -> bool:
    """
    Initialize database with all collections and indexes.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("=" * 60)
        logger.info("DATABASE INITIALIZATION STARTED")
        logger.info("=" * 60)
        
        # Create collections
        logger.info("\n--- Creating Collections ---")
        create_files_collection()
        create_users_verification_collection()
        create_verification_tokens_collection()
        create_force_sub_channels_collection()
        create_admin_settings_collection()
        create_admin_logs_collection()
        
        # Create indexes
        logger.info("\n--- Creating Indexes ---")
        create_indexes()
        
        # Insert default settings
        logger.info("\n--- Inserting Default Settings ---")
        insert_default_settings()
        
        logger.info("\n" + "=" * 60)
        logger.info("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return True
    
    except Exception as e:
        logger.error(f"\n❌ Database initialization failed: {e}", exc_info=True)
        return False


def get_database_status() -> Dict[str, Any]:
    """
    Get current database status.
    
    Returns:
        Dictionary with database status information
    """
    try:
        db = get_database()
        
        collections = db.list_collection_names()
        
        status = {
            'initialized': True,
            'collections': {},
            'total_collections': len(collections)
        }
        
        # Get document counts
        for collection_name in collections:
            try:
                count = db[collection_name].count_documents({})
                status['collections'][collection_name] = count
            except:
                status['collections'][collection_name] = 'Error'
        
        return status
    
    except Exception as e:
        return {
            'initialized': False,
            'error': str(e)
        }


def print_database_status() -> None:
    """Print current database status."""
    status = get_database_status()
    
    print("\n" + "=" * 60)
    print("DATABASE STATUS")
    print("=" * 60)
    
    if status.get('initialized'):
        print(f"Status: ✅ Initialized")
        print(f"Total Collections: {status['total_collections']}")
        print("\nDocument Counts:")
        
        for collection, count in status.get('collections', {}).items():
            print(f"  • {collection}: {count}")
    else:
        print(f"Status: ❌ Not Initialized")
        print(f"Error: {status.get('error', 'Unknown')}")
    
    print("=" * 60 + "\n")


# Run initialization if executed directly
if __name__ == "__main__":
    print("\n🚀 Starting Database Initialization...\n")
    
    success = initialize_database()
    
    if success:
        print("\n✅ Database is ready to use!\n")
        print_database_status()
    else:
        print("\n❌ Database initialization failed. Check logs for details.\n")
        exit(1)