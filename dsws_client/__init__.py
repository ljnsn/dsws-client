"""The Datastream Web Service API client package."""

__all__ = (
    "__version__",
    "DSWSClient",
    "DSWSConfig",
)

from dsws_client.client import DSWSClient
from dsws_client.config import DSWSConfig
from dsws_client.version import __version__
