from enum import Enum


class IncidentStyle(str, Enum):
    """Enumerate incident styles."""

    INFO = "info"
    """Info"""

    WARNING = "warning"
    """Warning"""

    DANGER = "danger"
    """Danger"""

    PRIMARY = "primary"
    """Primary"""

    LIGHT = "light"
    """Light"""

    DARK = "dark"
    """Dark"""
