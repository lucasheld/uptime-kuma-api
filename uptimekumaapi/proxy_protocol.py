from enum import Enum


class ProxyProtocol(str, Enum):
    HTTPS = "https"
    HTTP = "http"
    SOCKS = "socks"
    SOCKS5 = "socks5"
    SOCKS4 = "socks4"
