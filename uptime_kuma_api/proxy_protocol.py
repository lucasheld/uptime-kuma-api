from enum import Enum


class ProxyProtocol(str, Enum):
    """Enumerate proxy protocols."""

    HTTPS = "https"
    """HTTPS"""

    HTTP = "http"
    """HTTP"""

    SOCKS = "socks"
    """SOCKS"""

    SOCKS5 = "socks5"
    """SOCKS5"""

    SOCKS4 = "socks4"
    """SOCKS4"""
