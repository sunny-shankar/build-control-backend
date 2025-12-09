from datetime import datetime, timezone


def now_utc_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC
