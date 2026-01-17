"""
Encryption Service for secure message handling
Uses Fernet symmetric encryption from the cryptography library
"""
from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib
import os


class EncryptionService:
    """
    Handles message encryption and decryption using Fernet symmetric encryption.
    
    Features:
    - Generate secure encryption keys
    - Encrypt messages before transmission
    - Decrypt messages on receipt
    - Room-specific encryption keys
    """
    
    def __init__(self, master_key: str = None):
        """
        Initialize the encryption service.
        
        Args:
            master_key: Optional master key for encryption. If not provided,
                       a new key will be generated.
        """
        if master_key:
            # Derive a Fernet-compatible key from the master key
            self._key = self._derive_key(master_key)
        else:
            self._key = Fernet.generate_key()
        
        self._cipher = Fernet(self._key)
        self._room_ciphers = {}  # Room-specific encryption
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new Fernet encryption key."""
        return Fernet.generate_key()
    
    @staticmethod
    def _derive_key(password: str) -> bytes:
        """
        Derive a Fernet-compatible key from a password string.
        
        Args:
            password: The password to derive the key from
            
        Returns:
            A base64-encoded 32-byte key suitable for Fernet
        """
        # Use SHA-256 to get a 32-byte key, then base64 encode it
        key = hashlib.sha256(password.encode()).digest()
        return base64.urlsafe_b64encode(key)
    
    def encrypt(self, message: str) -> str:
        """
        Encrypt a message.
        
        Args:
            message: The plaintext message to encrypt
            
        Returns:
            The encrypted message as a base64 string
        """
        try:
            encrypted = self._cipher.encrypt(message.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt message: {str(e)}")
    
    def decrypt(self, encrypted_message: str) -> str:
        """
        Decrypt an encrypted message.
        
        Args:
            encrypted_message: The encrypted message as a base64 string
            
        Returns:
            The decrypted plaintext message
        """
        try:
            decrypted = self._cipher.decrypt(encrypted_message.encode('utf-8'))
            return decrypted.decode('utf-8')
        except InvalidToken:
            raise EncryptionError("Invalid token - message may be corrupted or tampered with")
        except Exception as e:
            raise EncryptionError(f"Failed to decrypt message: {str(e)}")
    
    def create_room_key(self, room_id: str) -> str:
        """
        Create a unique encryption key for a chat room.
        
        Args:
            room_id: The unique identifier of the room
            
        Returns:
            The room's encryption key as a string
        """
        room_key = Fernet.generate_key()
        self._room_ciphers[room_id] = Fernet(room_key)
        return room_key.decode('utf-8')
    
    def set_room_key(self, room_id: str, key: str) -> None:
        """
        Set the encryption key for a specific room.
        
        Args:
            room_id: The unique identifier of the room
            key: The encryption key as a string
        """
        self._room_ciphers[room_id] = Fernet(key.encode('utf-8'))