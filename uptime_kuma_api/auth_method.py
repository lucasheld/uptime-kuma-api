from enum import Enum


class AuthMethod(str, Enum):
    NONE = ""
    HTTP_BASIC = "basic"
    NTLM = "ntlm"
