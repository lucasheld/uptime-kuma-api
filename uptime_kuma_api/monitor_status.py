from enum import Enum


class MonitorStatus(int, Enum):
    """Enumerate monitor statuses."""

    DOWN = 0
    """DOWN"""

    UP = 1
    """UP"""

    PENDING = 2
    """PENDING"""

    MAINTENANCE = 3
    """MAINTENANCE"""
