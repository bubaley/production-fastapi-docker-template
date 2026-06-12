import base64
import hashlib

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.settings import settings


class _CryptoService:
    """Manages encryption and decryption of bot tokens"""

    def __init__(self):
        self._fernet = self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize encryption key"""
        try:
            # Use the encryption key from settings
            key = settings.encryption_key.encode()

            # Ensure key is 32 bytes for Fernet
            if len(key) != 32:
                # Derive key from password
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'telegram_auth_salt',
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(key))
            else:
                key = base64.urlsafe_b64encode(key)

            return Fernet(key)
        except Exception:
            raise

    def encrypt(self, value: str) -> str:
        """Encrypt bot token"""
        try:
            encrypted = self._fernet.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception:
            raise

    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt bot token"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return ''

    @staticmethod
    def hash_value(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()


# Global crypto manager instance
CryptoService = _CryptoService()
