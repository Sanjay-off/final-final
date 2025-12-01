"""
Encryption and Security Utilities
Provides encryption, decryption, hashing, and token generation functions.
"""

import hashlib
import secrets
import base64
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

from config.settings import ENCRYPTION_KEY


def _get_fernet_key(password: Optional[str] = None) -> bytes:
    """
    Generate Fernet key from password.
    
    Args:
        password: Password to derive key from (uses ENCRYPTION_KEY if not provided)
    
    Returns:
        Fernet-compatible key
    """
    if password is None:
        password = ENCRYPTION_KEY
    
    # Use PBKDF2 to derive a key from password
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'telegram_file_system_salt',  # Static salt for consistency
        iterations=100000,
        backend=default_backend()
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_data(data: str, password: Optional[str] = None) -> str:
    """
    Encrypt data using Fernet symmetric encryption.
    
    Args:
        data: Data to encrypt
        password: Encryption password (uses ENCRYPTION_KEY if not provided)
    
    Returns:
        Encrypted data as base64 string
    """
    try:
        key = _get_fernet_key(password)
        f = Fernet(key)
        
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()
    
    except Exception as e:
        raise ValueError(f"Encryption failed: {e}")


def decrypt_data(encrypted_data: str, password: Optional[str] = None) -> str:
    """
    Decrypt data encrypted with encrypt_data.
    
    Args:
        encrypted_data: Encrypted data as base64 string
        password: Decryption password (uses ENCRYPTION_KEY if not provided)
    
    Returns:
        Decrypted data as string
    """
    try:
        key = _get_fernet_key(password)
        f = Fernet(key)
        
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")


def generate_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Length of token in bytes
    
    Returns:
        URL-safe token string
    """
    return secrets.token_urlsafe(length)


def generate_verification_token() -> str:
    """
    Generate a verification token.
    
    Returns:
        Secure verification token
    """
    return generate_token(32)


def generate_short_token(length: int = 16) -> str:
    """
    Generate a shorter token (for display purposes).
    
    Args:
        length: Length of token in characters
    
    Returns:
        Hexadecimal token string
    """
    return secrets.token_hex(length // 2)


def hash_string(data: str, algorithm: str = 'sha256') -> str:
    """
    Hash a string using specified algorithm.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
    
    Returns:
        Hexadecimal hash string
    """
    try:
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    except Exception as e:
        raise ValueError(f"Hashing failed: {e}")


def verify_hash(data: str, hash_value: str, algorithm: str = 'sha256') -> bool:
    """
    Verify if data matches hash.
    
    Args:
        data: Original data
        hash_value: Hash to verify against
        algorithm: Hash algorithm used
    
    Returns:
        True if hash matches, False otherwise
    """
    try:
        computed_hash = hash_string(data, algorithm)
        return secrets.compare_digest(computed_hash, hash_value)
    
    except Exception:
        return False


def encode_base64(data: Union[str, bytes]) -> str:
    """
    Encode data to base64.
    
    Args:
        data: Data to encode
    
    Returns:
        Base64 encoded string
    """
    if isinstance(data, str):
        data = data.encode()
    
    return base64.b64encode(data).decode()


def decode_base64(encoded_data: str) -> str:
    """
    Decode base64 data.
    
    Args:
        encoded_data: Base64 encoded string
    
    Returns:
        Decoded string
    """
    try:
        return base64.b64decode(encoded_data.encode()).decode()
    except Exception as e:
        raise ValueError(f"Base64 decoding failed: {e}")


def encode_url_safe(data: str) -> str:
    """
    Encode data to URL-safe base64 (for deep links).
    
    Args:
        data: Data to encode
    
    Returns:
        URL-safe base64 encoded string
    """
    encoded = base64.urlsafe_b64encode(data.encode()).decode()
    # Remove padding for cleaner URLs
    return encoded.rstrip('=')


def decode_url_safe(encoded_data: str) -> str:
    """
    Decode URL-safe base64 data.
    
    Args:
        encoded_data: URL-safe base64 encoded string
    
    Returns:
        Decoded string
    """
    try:
        # Add padding back if needed
        padding = 4 - (len(encoded_data) % 4)
        if padding != 4:
            encoded_data += '=' * padding
        
        return base64.urlsafe_b64decode(encoded_data.encode()).decode()
    except Exception as e:
        raise ValueError(f"URL-safe decoding failed: {e}")


def generate_secure_id(prefix: str = "", length: int = 16) -> str:
    """
    Generate a secure unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of random part
    
    Returns:
        Secure unique ID
    """
    random_part = secrets.token_hex(length // 2)
    
    if prefix:
        return f"{prefix}_{random_part}"
    
    return random_part


def obfuscate_string(data: str, show_chars: int = 4) -> str:
    """
    Obfuscate a string (for displaying sensitive data).
    
    Args:
        data: String to obfuscate
        show_chars: Number of characters to show at start and end
    
    Returns:
        Obfuscated string
    """
    if not data or len(data) <= show_chars * 2:
        return '*' * len(data)
    
    visible_start = data[:show_chars]
    visible_end = data[-show_chars:]
    masked_middle = '*' * (len(data) - show_chars * 2)
    
    return f"{visible_start}{masked_middle}{visible_end}"


def generate_random_hex(length: int = 16) -> str:
    """
    Generate random hexadecimal string.
    
    Args:
        length: Length of output string
    
    Returns:
        Random hex string
    """
    return secrets.token_hex(length // 2)


def generate_api_key(length: int = 32) -> str:
    """
    Generate an API key.
    
    Args:
        length: Length of the API key
    
    Returns:
        Secure API key
    """
    return generate_token(length)


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time (timing-attack safe).
    
    Args:
        a: First string
        b: Second string
    
    Returns:
        True if strings match, False otherwise
    """
    return secrets.compare_digest(a.encode(), b.encode())


def create_signature(data: str, secret: str) -> str:
    """
    Create HMAC signature for data.
    
    Args:
        data: Data to sign
        secret: Secret key
    
    Returns:
        Hexadecimal signature
    """
    import hmac
    
    signature = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_signature(data: str, signature: str, secret: str) -> bool:
    """
    Verify HMAC signature.
    
    Args:
        data: Original data
        signature: Signature to verify
        secret: Secret key
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        expected_signature = create_signature(data, secret)
        return constant_time_compare(expected_signature, signature)
    except Exception:
        return False


def encrypt_token(token_data: dict, password: Optional[str] = None) -> str:
    """
    Encrypt token data (dict to encrypted string).
    
    Args:
        token_data: Dictionary containing token data
        password: Encryption password
    
    Returns:
        Encrypted token string
    """
    import json
    
    json_str = json.dumps(token_data)
    return encrypt_data(json_str, password)


def decrypt_token(encrypted_token: str, password: Optional[str] = None) -> dict:
    """
    Decrypt token string to dictionary.
    
    Args:
        encrypted_token: Encrypted token string
        password: Decryption password
    
    Returns:
        Token data as dictionary
    """
    import json
    
    json_str = decrypt_data(encrypted_token, password)
    return json.loads(json_str)


__all__ = [
    # Encryption/Decryption
    'encrypt_data',
    'decrypt_data',
    
    # Token Generation
    'generate_token',
    'generate_verification_token',
    'generate_short_token',
    'generate_secure_id',
    'generate_api_key',
    
    # Hashing
    'hash_string',
    'verify_hash',
    
    # Base64 Encoding
    'encode_base64',
    'decode_base64',
    'encode_url_safe',
    'decode_url_safe',
    
    # Utility
    'obfuscate_string',
    'generate_random_hex',
    'constant_time_compare',
    
    # Signatures
    'create_signature',
    'verify_signature',
    
    # Token Encryption
    'encrypt_token',
    'decrypt_token',
]