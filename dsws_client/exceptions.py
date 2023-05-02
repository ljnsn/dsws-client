class DSWSError(Exception):
    """Base class for DSWS exceptions."""


class RequestFailedError(DSWSError):
    """Indicates that a request failed."""

    def __init__(self, message: str, status_code: int) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.status_code = status_code


class InvalidResponseError(DSWSError):
    """Indicates that the response is invalid."""


class InvalidRequestError(DSWSError):
    """Indicates that the request is invalid."""
