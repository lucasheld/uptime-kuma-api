from enum import Enum


class MonitorType(str, Enum):
    """Enumerate monitor types."""
    
    GROUP = "group"
    """Group"""

    HTTP = "http"
    """HTTP(s)"""

    PORT = "port"
    """TCP Port"""

    PING = "ping"
    """Ping"""

    KEYWORD = "keyword"
    """HTTP(s) - Keyword"""

    JSON_QUERY = "json-query"
    """HTTP(s) - Json Query"""

    GRPC_KEYWORD = "grpc-keyword"
    """gRPC(s) - Keyword"""

    DNS = "dns"
    """DNS"""

    DOCKER = "docker"
    """Docker Container"""

    REAL_BROWSER = "real-browser"
    """HTTP(s) - Browser Engine (Chrome/Chromium)"""

    PUSH = "push"
    """Push"""

    STEAM = "steam"
    """Steam Game Server"""

    GAMEDIG = "gamedig"
    """GameDig"""

    MQTT = "mqtt"
    """MQTT"""

    KAFKA_PRODUCER = "kafka-producer"
    """Kafka Producer"""

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

    TAILSCALE_PING = "tailscale-ping"
    """Tailscale Ping"""
