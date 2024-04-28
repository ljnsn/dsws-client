"""DSWS responses."""

import datetime as dt
import sys
from typing import Any, List, Optional, Union

import msgspec

from dsws_client import converters
from dsws_client.value_objects import (
    DSStringKVPair,
    Token,
    enums,
)

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

BOOL_MAPPING = {
    "Y": True,
    "true": True,
    "True": True,
    "N": False,
    "false": False,
    "False": False,
}

DSDateString = Annotated[
    str,
    msgspec.Meta(pattern=r"\/Date\((\d+)([+-]\d{4})?\)\/"),
]


class _DSSymbolResponseValue(msgspec.Struct, rename="pascal", tag_field="Type"):
    """A symbol response value."""

    symbol: str
    currency: Optional[str]
    value: Any

    def parse(self) -> Any:
        """Parse the value."""
        return self.value


class DSError(_DSSymbolResponseValue, tag=enums.DSSymbolResponseValueType.ERROR.value):
    """An error response value."""

    value: str

    def parse(self) -> None:
        """Parse the value."""
        return


class DSEmpty(_DSSymbolResponseValue, tag=enums.DSSymbolResponseValueType.EMPTY.value):
    """An empty response value."""

    value: Any

    def parse(self) -> None:
        """Parse the value."""
        return


class DSBool(_DSSymbolResponseValue, tag=enums.DSSymbolResponseValueType.BOOL.value):
    """A boolean response value."""

    value: str

    def parse(self) -> bool:
        """Parse the value."""
        return BOOL_MAPPING[self.value]


class DSInt(_DSSymbolResponseValue, tag=enums.DSSymbolResponseValueType.INT.value):
    """An integer response value."""

    value: int


class DSDateTime(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.DATE_TIME.value,
):
    """A date/time response value."""

    value: DSDateString

    def parse(self) -> dt.datetime:
        """Parse the value."""
        return converters.convert_date(self.value)


class DSDouble(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.DOUBLE.value,
):
    """A double response value."""

    value: float


class DSString(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.STRING.value,
):
    """A string response value."""

    value: str


class DSBoolArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.BOOL_ARRAY.value,
):
    """A boolean array response value."""

    value: str

    def parse(self) -> List[bool]:
        """Parse the value."""
        return [BOOL_MAPPING[item] for item in self.value]


class DSIntArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.INT_ARRAY.value,
):
    """An integer array response value."""

    value: List[int]


class DSDateTimeArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.DATE_TIME_ARRAY.value,
):
    """A date/time array response value."""

    value: List[DSDateString]

    def parse(self) -> List[dt.datetime]:
        """Parse the value."""
        return [converters.convert_date(date_str) for date_str in self.value]


class DSDoubleArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.DOUBLE_ARRAY.value,
):
    """A double array response value."""

    value: List[float]


class DSStringArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.STRING_ARRAY.value,
):
    """A string array response value."""

    value: List[str]


class DSObjectArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.OBJECT_ARRAY.value,
):
    """An object array response value."""

    value: List[Any]


DSSymbolResponseValue = Union[
    DSError,
    DSEmpty,
    DSBool,
    DSInt,
    DSDateTime,
    DSDouble,
    DSString,
    DSBoolArray,
    DSIntArray,
    DSDateTimeArray,
    DSDoubleArray,
    DSStringArray,
    DSObjectArray,
]


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

    def pydates(self) -> Optional[List[dt.datetime]]:
        """Return response dates as python dates."""
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

    def to_token(self) -> Token:
        """Convert to a token."""
        return Token(self.token_value, converters.convert_date(self.token_expiry))
