from enum import Enum


class MonitorType(str, Enum):
    """Enumerate monitor types."""

    HTTP = "http"
    """HTTP(s)"""

    PORT = "port"
    """TCP Port"""

    PING = "ping"
    """Ping"""

    KEYWORD = "keyword"
    """HTTP(s) - Keyword"""

    DNS = "dns"
    """DNS"""

    DOCKER = "docker"
    """Docker Container"""

    PUSH = "push"
    """Push"""

    STEAM = "steam"
    """Steam Game Server"""

    MQTT = "mqtt"
    """MQTT"""

    SQLSERVER = "sqlserver"
    """Microsoft SQL Server"""

    POSTGRES = "postgres"
    """PostgreSQL"""

    RADIUS = "radius"
    """Radius"""
