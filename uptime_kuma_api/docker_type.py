from enum import Enum


class DockerType(str, Enum):
    """Enumerate docker connection types."""

    SOCKET = "socket"
    """Socket"""

    TCP = "tcp"
    """TCP"""
