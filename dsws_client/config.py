import os
import urllib.parse
from typing import Any, ClassVar, Dict, Optional

import attrs
import httpx
from dotenv import load_dotenv

from dsws_client.version import __version__


@attrs.define()
class DSWSConfig:
    """Configuration for the DSWS client."""

    path: ClassVar[str] = "/DSWSClient/V1/DSService.svc/rest/"
    host: str = "https://product.datastream.com"
    timeout: int = attrs.field(default=180, converter=int)
    proxy: Optional[str] = None
    ssl_cert: Optional[str] = None
    app_id: str = f"dsws-client-{__version__}"
    data_source: Optional[str] = None
    max_concurrency: int = 1
    debug: bool = attrs.field(default=False, converter=attrs.converters.to_bool)

    def __init__(self, **kwargs: Any) -> None:
        """Load configuration from environment variables."""
        load_dotenv()
        init_dict = {}
        for field in attrs.fields(DSWSConfig):
            # try to get the value from kwargs, then from environment variables
            value = kwargs.get(field.name, os.getenv(field.name.upper()))
            if value is not None:
                init_dict[field.name] = value
        self.__attrs_init__(**init_dict)  # type: ignore[attr-defined]

    @property
    def base_url(self) -> str:
        """Return the base URL."""
        return urllib.parse.urljoin(self.host, self.path)

    @property
    def proxies(self) -> Optional[Dict[str, httpx.HTTPTransport]]:
        """Return the proxies."""
        proxy = httpx.HTTPTransport(proxy=self.proxy)
        return {"https://": proxy, "http://": proxy} if self.proxy else None
