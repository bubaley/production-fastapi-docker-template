from typing import Annotated

from pydantic import AfterValidator


def normalize_email(value: str) -> str:
    return value.strip().lower()


NormalizedEmail = Annotated[str, AfterValidator(normalize_email)]
