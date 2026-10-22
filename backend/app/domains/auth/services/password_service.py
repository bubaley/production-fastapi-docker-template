import asyncio
import hashlib
import hmac
import secrets
from collections.abc import Sequence
from functools import cache

import bcrypt

from app.core.settings import settings


class PasswordService:
    """Password hashing. bcrypt is CPU-bound: inside the event loop use the *_async variants."""

    @staticmethod
    def _password_digest(password: str, pepper: str) -> bytes:
        # HMAC pre-hash keeps the bcrypt input at 64 bytes (bcrypt rejects inputs over 72 bytes).
        digest = hmac.new(pepper.encode('utf-8'), password.encode('utf-8'), hashlib.sha256).hexdigest()
        return digest.encode('utf-8')

    @staticmethod
    def hash_password(password: str, pepper: str) -> str:
        salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
        hashed = bcrypt.hashpw(PasswordService._password_digest(password, pepper), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str, pepper: str) -> bool:
        try:
            return bcrypt.checkpw(
                PasswordService._password_digest(plain_password, pepper),
                hashed_password.encode('utf-8'),
            )
        except ValueError:
            return False

    @staticmethod
    def match_pepper(plain_password: str, hashed_password: str, peppers: Sequence[str]) -> int | None:
        """Return the index of the first pepper that verifies the password, or None."""
        for index, pepper in enumerate(peppers):
            if PasswordService.verify_password(plain_password, hashed_password, pepper):
                return index
        return None

    @staticmethod
    async def hash_password_async(password: str, pepper: str) -> str:
        return await asyncio.to_thread(PasswordService.hash_password, password, pepper)

    @staticmethod
    async def match_pepper_async(plain_password: str, hashed_password: str, peppers: Sequence[str]) -> int | None:
        return await asyncio.to_thread(PasswordService.match_pepper, plain_password, hashed_password, peppers)

    @staticmethod
    @cache
    def _dummy_password_hash(rounds: int) -> str:
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(secrets.token_urlsafe(32).encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def _dummy_password_check(plain_password: str, peppers: Sequence[str]) -> None:
        dummy_hash = PasswordService._dummy_password_hash(settings.bcrypt_rounds)
        PasswordService.match_pepper(plain_password, dummy_hash, peppers)

    @staticmethod
    async def verify_dummy_password(plain_password: str, peppers: Sequence[str]) -> None:
        """Spend the same bcrypt work as a failed real check, so unknown accounts are not revealed by timing."""
        await asyncio.to_thread(PasswordService._dummy_password_check, plain_password, peppers)
