import base64
import hashlib

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.settings import settings


class _CryptoService:
    """Symmetric encryption (Fernet) for secrets stored at rest, keyed by ENCRYPTION_KEY."""

    def __init__(self):
        self._fernet = self._initialize_encryption()

    def _initialize_encryption(self):
        """Build the Fernet instance from ENCRYPTION_KEY."""
        try:
            key = settings.encryption_key.encode()

            # Fernet needs exactly 32 bytes; derive them when the configured key is not 32 bytes long.
            # The salt is part of the derived key: changing it makes existing ciphertexts unreadable.
            if len(key) != 32:
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
        except Exception as e:
            raise RuntimeError(f'Failed to initialize encryption, error: {e}')

    def encrypt(self, value: str) -> str:
        """Encrypt a string and return URL-safe text."""
        try:
            encrypted = self._fernet.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise RuntimeError(f'Failed to encrypt value, error: {e}')

    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt a value produced by `encrypt`; returns an empty string when it cannot be decrypted."""
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
