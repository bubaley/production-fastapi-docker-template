from typing import Annotated

from pydantic import AfterValidator, EmailStr, Field


def normalize_email(value: str) -> str:
    return value.strip().lower()


# Validated address, stored lowercase. Use for fields that create or change an email.
NormalizedEmail = Annotated[EmailStr, AfterValidator(normalize_email)]

# Lowercased but not validated: login must still find accounts stored before validation existed.
LoginEmail = Annotated[str, Field(max_length=320), AfterValidator(normalize_email)]
