from enum import Enum


class IncidentStyle(str, Enum):
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    PRIMARY = "primary"
    LIGHT = "light"
    DARK = "dark"
