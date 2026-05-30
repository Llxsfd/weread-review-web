from datetime import datetime, timedelta, timezone

SHANGHAI_TZ = timezone(timedelta(hours=8))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def local_now() -> datetime:
    return datetime.now(SHANGHAI_TZ).replace(tzinfo=None)


def from_unix_timestamp(value: int | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=SHANGHAI_TZ).replace(tzinfo=None)


def to_local_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.isoformat(sep=" ")
    return value.astimezone(SHANGHAI_TZ).replace(tzinfo=None).isoformat(sep=" ")
