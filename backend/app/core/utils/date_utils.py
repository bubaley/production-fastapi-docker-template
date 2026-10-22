from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


def as_utc(value: datetime) -> datetime:
    """Treat naive datetimes (Tortoise with use_tz=False) as UTC so they compare with `utcnow()`."""
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
