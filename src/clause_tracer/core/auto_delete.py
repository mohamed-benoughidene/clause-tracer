"""The auto-delete date rules (Spec 9).

Pure functions over datetimes. None reads a clock: the caller passes now
in, through the Clock port (T2). A review is deleted when now reaches its
due date; the warning window is the last three days before it. A setting
lowered recently holds a three-day grace, so old reviews do not fall due
at once. A clock behind the last change is never due, so a jump backwards
deletes nothing.
"""

from datetime import datetime, timedelta

WARNING_WINDOW = timedelta(days=3)
LOWERING_GRACE = timedelta(days=3)


def _check_datetime(value: datetime) -> None:
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")


def _check_days(days: int) -> None:
    if days < 1:
        raise ValueError("days must be 1 or more")


def due_at(last_change: datetime, days: int, protected_until: datetime | None = None) -> datetime:
    """When the review falls due: last_change + days, or the grace's end when later."""

    _check_datetime(last_change)
    _check_days(days)
    due = last_change + timedelta(days=days)
    if protected_until is not None:
        _check_datetime(protected_until)
        if protected_until > due:
            return protected_until
    return due


def is_due(
    last_change: datetime, days: int, now: datetime, protected_until: datetime | None = None
) -> bool:
    """True when now has reached the due date; a clock behind last_change is never due."""

    _check_datetime(now)
    return now >= due_at(last_change, days, protected_until)


def in_warning_window(
    last_change: datetime, days: int, now: datetime, protected_until: datetime | None = None
) -> bool:
    """True when now is in the last three days before the due date."""

    _check_datetime(now)
    due = due_at(last_change, days, protected_until)
    return due - WARNING_WINDOW <= now < due


def protected_until_after_lowering(lowered_at: datetime) -> datetime:
    """The end of the grace held after the auto-delete setting was lowered."""

    _check_datetime(lowered_at)
    return lowered_at + LOWERING_GRACE
