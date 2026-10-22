from typing import Annotated

from pydantic import AfterValidator, Field

from app.core.settings import settings


def validate_password_policy(value: str) -> str:
    if len(value) < settings.password_min_length:
        raise ValueError(f'Password must be at least {settings.password_min_length} characters long')
    return value


# A new password: enforced on create and change, never on login.
NewPassword = Annotated[str, Field(max_length=128), AfterValidator(validate_password_policy)]
