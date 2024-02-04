"""DSWS responses."""

import datetime as dt
import sys
from typing import Any, List, Optional

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

import msgspec

from dsws_client import converters
from dsws_client.value_objects import DSStringKVPair, DSSymbolResponseValueType

DSDateString = Annotated[
    str,
    msgspec.Meta(pattern=r"\/Date\((\d+)([+-]\d{4})?\)\/"),
]


class DSSymbolResponseValue(msgspec.Struct, rename="pascal"):
    """A symbol response value."""

    symbol: str
    currency: Optional[str]
    type: DSSymbolResponseValueType
    value: Any


class DSDataTypeResponseValue(msgspec.Struct, rename="pascal"):
    """A data type response value."""

    data_type: str
    symbol_values: List[DSSymbolResponseValue]


class DSDataResponse(msgspec.Struct, rename="pascal"):
    """Object that contains a data response."""

    data_type_values: List[DSDataTypeResponseValue]
    dates: Optional[List[DSDateString]]
    data_type_names: Optional[List[DSStringKVPair]]
    symbol_names: Optional[List[DSStringKVPair]]
    additional_responses: Optional[List[DSStringKVPair]]
    tag: Optional[str]

    @property
    def pydates(self) -> Optional[List[dt.datetime]]:
        """The foo property."""
        if self.dates is None:
            return None
        return [converters.convert_date(date_str) for date_str in self.dates]


class DSGetDataResponse(msgspec.Struct, rename="pascal"):
    """Object that containes a get data response."""

    data_response: DSDataResponse
    properties: Optional[List[DSStringKVPair]] = None


class DSGetDataBundleResponse(msgspec.Struct, rename="pascal"):
    """Object that contains a get data bundle response."""

    data_responses: List[DSDataResponse]
    properties: Optional[List[DSStringKVPair]] = None


class DSGetTokenResponse(msgspec.Struct, rename="pascal"):
    """Object that contains a token response."""

    token_value: str
    token_expiry: DSDateString
    properties: Optional[List[DSStringKVPair]]

    @property
    def expiry_pydate(self) -> dt.datetime:
        """The foo property."""
        return converters.convert_date(self.token_expiry)

    @property
    def is_expired(self) -> bool:
        """Return True if the token is expired."""
        return (self.expiry_pydate + dt.timedelta(minutes=1)) < dt.datetime.now(
            tz=dt.timezone.utc
        )
