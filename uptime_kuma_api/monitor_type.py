from enum import Enum


class MonitorType(str, Enum):
    HTTP = "http"
    PORT = "port"
    PING = "ping"
    KEYWORD = "keyword"
    DNS = "dns"
    DOCKER = "docker"
    PUSH = "push"
    STEAM = "steam"
    MQTT = "mqtt"
    SQLSERVER = "sqlserver"
    POSTGRES = "postgres"
    RADIUS = "radius"
