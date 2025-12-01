"""
Database Models
Defines the structure and schema for all database collections.
These are reference models - MongoDB itself doesn't enforce schema,
but these classes provide documentation and validation helpers.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class FileModel:
    """
    Model for files collection.
    Stores uploaded ZIP files and their metadata.
    """
    post_no: int
    context: str
    extra_message: str
    file_id: str
    file_name: str
    storage_message_id: int
    public_message_id: int
    password: str
    download_count: int = 0
    created_by: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_downloaded_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB insertion."""
        return {
            'post_no': self.post_no,
            'context': self.context,
            'extra_message': self.extra_message,
            'file_id': self.file_id,
            'file_name': self.file_name,
            'storage_message_id': self.storage_message_id,
            'public_message_id': self.public_message_id,
            'password': self.password,
            'download_count': self.download_count,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_downloaded_at': self.last_downloaded_at
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FileModel':
        """Create model instance from MongoDB document."""
        return FileModel(
            post_no=data['post_no'],
            context=data['context'],
            extra_message=data['extra_message'],
            file_id=data['file_id'],
            file_name=data['file_name'],
            storage_message_id=data['storage_message_id'],
            public_message_id=data['public_message_id'],
            password=data['password'],
            download_count=data.get('download_count', 0),
            created_by=data.get('created_by', 0),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at'),
            last_downloaded_at=data.get('last_downloaded_at')
        )


@dataclass
class UserVerificationModel:
    """
    Model for users_verification collection.
    Stores user verification status and file access tracking.
    """
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    files_accessed_count: int = 0
    files_accessed: List[int] = field(default_factory=list)
    last_access: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    verified_by: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB insertion."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at,
            'expires_at': self.expires_at,
            'files_accessed_count': self.files_accessed_count,
            'files_accessed': self.files_accessed,
            'last_access': self.last_access,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'verified_by': self.verified_by
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UserVerificationModel':
        """Create model instance from MongoDB document."""
        return UserVerificationModel(
            user_id=data['user_id'],
            username=data.get('username'),
            first_name=data.get('first_name'),
            is_verified=data.get('is_verified', False),
            verified_at=data.get('verified_at'),
            expires_at=data.get('expires_at'),
            files_accessed_count=data.get('files_accessed_count', 0),
            files_accessed=data.get('files_accessed', []),
            last_access=data.get('last_access', datetime.now()),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at'),
            verified_by=data.get('verified_by')
        )
    
    def is_expired(self) -> bool:
        """Check if verification is expired."""
        if not self.is_verified or not self.expires_at:
            return True
        return datetime.now() > self.expires_at
    
    def can_access_file(self, file_limit: int = 3) -> bool:
        """Check if user can access more files."""
        return not self.is_expired() and self.files_accessed_count < file_limit


@dataclass
class VerificationTokenModel:
    """
    Model for verification_tokens collection.
    Stores verification tokens for bypass detection.
    """
    token_id: str
    user_id: int
    status: str  # pending, in_progress, completed, expired
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB insertion."""
        return {
            'token_id': self.token_id,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'completed_at': self.completed_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'VerificationTokenModel':
        """Create model instance from MongoDB document."""
        return VerificationTokenModel(
            token_id=data['token_id'],
            user_id=data['user_id'],
            status=data['status'],
            created_at=data.get('created_at', datetime.now()),
            expires_at=data.get('expires_at'),
            completed_at=data.get('completed_at'),
            updated_at=data.get('updated_at')
        )
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return True
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if token is valid for use."""
        return (
            not self.is_expired() and
            self.status in ['pending', 'in_progress']
        )


@dataclass
class ForceSubChannelModel:
    """
    Model for force_sub_channels collection.
    Stores force subscribe channel information.
    """
    channel_username: str
    channel_link: str
    button_text: str
    channel_id: Optional[int] = None
    order: int = 1
    is_active: bool = True
    added_by: Optional[int] = None
    added_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB insertion."""
        data = {
            'channel_username': self.channel_username,
            'channel_link': self.channel_link,
            'button_text': self.button_text,
            'order': self.order,
            'is_active': self.is_active,
            'added_at': self.added_at,
            'updated_at': self.updated_at
        }
        
        if self.channel_id:
            data['channel_id'] = self.channel_id
        
        if self.added_by:
            data['added_by'] = self.added_by
        
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ForceSubChannelModel':
        """Create model instance from MongoDB document."""
        return ForceSubChannelModel(
            channel_username=data['channel_username'],
            channel_link=data['channel_link'],
            button_text=data['button_text'],
            channel_id=data.get('channel_id'),
            order=data.get('order', 1),
            is_active=data.get('is_active', True),
            added_by=data.get('added_by'),
            added_at=data.get('added_at', datetime.now()),
            updated_at=data.get('updated_at')
        )


@dataclass
class AdminSettingModel:
    """
    Model for admin_settings collection.
    Stores configuration settings.
    """
    setting_key: str
    setting_value: str
    updated_at: datetime = field(default_factory=datetime.now)
    updated_by: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB insertion."""
        data = {
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'updated_at': self.updated_at
        }
        
        if self.updated_by:
            data['updated_by'] = self.updated_by
        
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AdminSettingModel':
        """Create model instance from MongoDB document."""
        return AdminSettingModel(
            setting_key=data['setting_key'],
            setting_value=data['setting_value'],
            updated_at=data.get('updated_at', datetime.now()),
            updated_by=data.get('updated_by')
        )


@dataclass
class AdminLogModel:
    """
    Model for admin_logs collection.
    Stores admin action logs for audit trail.
    """
    admin_id: int
    action: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB insertion."""
        return {
            'admin_id': self.admin_id,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AdminLogModel':
        """Create model instance from MongoDB document."""
        return AdminLogModel(
            admin_id=data['admin_id'],
            action=data['action'],
            details=data.get('details', {}),
            timestamp=data.get('timestamp', datetime.now())
        )


# Collection name constants
COLLECTION_FILES = 'files'
COLLECTION_USERS_VERIFICATION = 'users_verification'
COLLECTION_VERIFICATION_TOKENS = 'verification_tokens'
COLLECTION_FORCE_SUB_CHANNELS = 'force_sub_channels'
COLLECTION_ADMIN_SETTINGS = 'admin_settings'
COLLECTION_ADMIN_LOGS = 'admin_logs'

# Model to collection mapping
MODEL_COLLECTION_MAP = {
    FileModel: COLLECTION_FILES,
    UserVerificationModel: COLLECTION_USERS_VERIFICATION,
    VerificationTokenModel: COLLECTION_VERIFICATION_TOKENS,
    ForceSubChannelModel: COLLECTION_FORCE_SUB_CHANNELS,
    AdminSettingModel: COLLECTION_ADMIN_SETTINGS,
    AdminLogModel: COLLECTION_ADMIN_LOGS,
}


def get_collection_name(model_class) -> str:
    """
    Get collection name for a model class.
    
    Args:
        model_class: Model class
    
    Returns:
        Collection name
    """
    return MODEL_COLLECTION_MAP.get(model_class, '')


__all__ = [
    'FileModel',
    'UserVerificationModel',
    'VerificationTokenModel',
    'ForceSubChannelModel',
    'AdminSettingModel',
    'AdminLogModel',
    'COLLECTION_FILES',
    'COLLECTION_USERS_VERIFICATION',
    'COLLECTION_VERIFICATION_TOKENS',
    'COLLECTION_FORCE_SUB_CHANNELS',
    'COLLECTION_ADMIN_SETTINGS',
    'COLLECTION_ADMIN_LOGS',
    'MODEL_COLLECTION_MAP',
    'get_collection_name',
]