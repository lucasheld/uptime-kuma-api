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

    GRPC_KEYWORD = "grpc-keyword"
    """gRPC(s) - Keyword"""

    DNS = "dns"
    """DNS"""

    DOCKER = "docker"
    """Docker Container"""

    PUSH = "push"
    """Push"""

    STEAM = "steam"
    """Steam Game Server"""

    GAMEDIG = "gamedig"
    """GameDig"""

    MQTT = "mqtt"
    """MQTT"""

    SQLSERVER = "sqlserver"
    """Microsoft SQL Server"""

    POSTGRES = "postgres"
    """PostgreSQL"""

    MYSQL = "mysql"
    """MySQL/MariaDB"""

    MONGODB = "mongodb"
    """MongoDB"""

    RADIUS = "radius"
    """Radius"""

    REDIS = "redis"
    """Redis"""

    GROUP = "group"
    """Group"""
