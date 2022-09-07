from enum import Enum


class DockerType(str, Enum):
    SOCKET = "socket"
    TCP = "tcp"
