class UptimeKumaException(Exception):
    """
    There was an exception that occurred while communicating with Uptime Kuma.
    """


class Timeout(UptimeKumaException):
    """
    A timeout has occurred while communicating with Uptime Kuma.
    """
