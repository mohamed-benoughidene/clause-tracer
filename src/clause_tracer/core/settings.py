"""The settings shape (system design 3.4, Spec 14.3).

Loaded once at start-up, validated there, and passed in (I13).
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class Settings:
    """The app's settings, loaded once at start-up (I13, Spec 14.3)."""

    default_model: str
    step_models: tuple[tuple[str, str], ...]
    private_mode_default: bool
    send_why_notes: bool
    auto_delete_days: int
    data_dir: str
    log_level: str
