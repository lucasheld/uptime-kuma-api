from enum import Enum


class Event(str, Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MONITOR_LIST = "monitorList"
    NOTIFICATION_LIST = "notificationList"
    PROXY_LIST = "proxyList"
    STATUS_PAGE_LIST = "statusPageList"
    HEARTBEAT_LIST = "heartbeatList"
    IMPORTANT_HEARTBEAT_LIST = "importantHeartbeatList"
    AVG_PING = "avgPing"
    UPTIME = "uptime"
    HEARTBEAT = "heartbeat"
    INFO = "info"
    CERT_INFO = "certInfo"
    DOCKER_HOST_LIST = "dockerHostList"
    AUTO_LOGIN = "autoLogin"
