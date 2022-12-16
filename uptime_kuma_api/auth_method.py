from enum import Enum


class AuthMethod(str, Enum):
    """Enumerate authentication methods for monitors."""

    NONE = ""
    """Authentication is disabled."""

    HTTP_BASIC = "basic"
    """HTTP Basic Authentication."""

    NTLM = "ntlm"
    """NTLM Authentication."""
