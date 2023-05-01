from enum import Enum


class MaintenanceStrategy(str, Enum):
    """Enumerate maintenance strategies."""

    MANUAL = "manual"
    """Active/Inactive Manually"""

    SINGLE = "single"
    """Single Maintenance Window"""

    RECURRING_INTERVAL = "recurring-interval"
    """Recurring - Interval"""

    RECURRING_WEEKDAY = "recurring-weekday"
    """Recurring - Day of Week"""

    RECURRING_DAY_OF_MONTH = "recurring-day-of-month"
    """Recurring - Day of Month"""

    CRON = "cron"
    """Cron Expression"""
