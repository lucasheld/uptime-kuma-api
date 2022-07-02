from enum import Enum


class MonitorType(str, Enum):
    HTTP = "http"
    PORT = "port"
    PING = "ping"
    KEYWORD = "keyword"
    DNS = "dns"
    PUSH = "push"
    STEAM = "steam"
    MQTT = "mqtt"
    SQLSERVER = "sqlserver"
