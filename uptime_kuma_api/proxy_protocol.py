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
    """SOCKS v5"""

    SOCKS5H = "socks5h"
    """SOCKS v5 (+DNS)"""

    SOCKS4 = "socks4"
    """SOCKS v4"""
