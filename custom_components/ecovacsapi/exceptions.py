"""Library exceptions."""
import sys
import traceback

class EcovacsException(Exception):
    """Base exception."""

    def __init__(self, message: str = "") -> None:
        """Initialize."""
        self.message = message
        super().__init__(self.message)

    def to_string(self) -> str:
        """Return the exception as a string."""
        return f"{self.__class__.__name__}: {self.message}\n" + self.traceback()

    def traceback(self) -> str:
        """Return the traceback as a string."""
        etype, value, trace = sys.exc_info()
        return "".join(traceback.format_exception(etype, value, trace, None))

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "generic_error"


class NotConnected(EcovacsException):
    """Action requested but not yet connected to the API."""

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "not_connected"


class ConnectionFailed(EcovacsException):
    """Failed to connect to the API."""

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "connection_failed"


class InvalidConfiguration(EcovacsException):
    """Invalid API Key provided."""

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "invalid_configuration"


class NotAuthorized(EcovacsException):
    """Not authorized to operate on the device or invalid device id."""

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "not_authorized"


class APIError(EcovacsException):
    """Remote API error."""

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "api_error"

class CommandError(EcovacsException):
    """Command error."""

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "command_error"


class InvalidResponse(EcovacsException):
    """Malformed or unexpected API response."""

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "invalid_reponse"


class DeviceOffline(EcovacsException):
    """Device is offline."""

    def get_title(self) -> str:
        """Return the title of the exception which will be then translated."""
        return "device_offline"