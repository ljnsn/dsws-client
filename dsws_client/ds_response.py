"""DSWS responses."""

import datetime as dt
from typing import Annotated, Any

import msgspec

from dsws_client import converters
from dsws_client.value_objects import (
    DSStringKVPair,
    Token,
    enums,
)

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
    currency: str | None
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

    def parse(self) -> list[bool]:
        """Parse the value."""
        return [BOOL_MAPPING[item] for item in self.value]


class DSIntArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.INT_ARRAY.value,
):
    """An integer array response value."""

    value: list[int]


class DSDateTimeArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.DATE_TIME_ARRAY.value,
):
    """A date/time array response value."""

    value: list[DSDateString]

    def parse(self) -> list[dt.datetime]:
        """Parse the value."""
        return [converters.convert_date(date_str) for date_str in self.value]


class DSDoubleArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.DOUBLE_ARRAY.value,
):
    """A double array response value."""

    value: list[float]


class DSStringArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.STRING_ARRAY.value,
):
    """A string array response value."""

    value: list[str]


class DSObjectArray(
    _DSSymbolResponseValue,
    tag=enums.DSSymbolResponseValueType.OBJECT_ARRAY.value,
):
    """An object array response value."""

    value: list[Any]


DSSymbolResponseValue = (
    DSError
    | DSEmpty
    | DSBool
    | DSInt
    | DSDateTime
    | DSDouble
    | DSString
    | DSBoolArray
    | DSIntArray
    | DSDateTimeArray
    | DSDoubleArray
    | DSStringArray
    | DSObjectArray
)


class DSDataTypeResponseValue(msgspec.Struct, rename="pascal"):
    """A data type response value."""

    data_type: str
    symbol_values: list[DSSymbolResponseValue]


class DSDataResponse(msgspec.Struct, rename="pascal"):
    """Object that contains a data response."""

    data_type_values: list[DSDataTypeResponseValue]
    dates: list[DSDateString] | None
    data_type_names: list[DSStringKVPair] | None
    symbol_names: list[DSStringKVPair] | None
    additional_responses: list[DSStringKVPair] | None
    tag: str | None

    def pydates(self) -> list[dt.datetime] | None:
        """Return response dates as python dates."""
        if self.dates is None:
            return None
        return [converters.convert_date(date_str) for date_str in self.dates]


class DSGetDataResponse(msgspec.Struct, rename="pascal"):
    """Object that containes a get data response."""

    data_response: DSDataResponse
    properties: list[DSStringKVPair] | None = None


class DSGetDataBundleResponse(msgspec.Struct, rename="pascal"):
    """Object that contains a get data bundle response."""

    data_responses: list[DSDataResponse]
    properties: list[DSStringKVPair] | None = None


class DSGetTokenResponse(msgspec.Struct, rename="pascal"):
    """Object that contains a token response."""

    token_value: str
    token_expiry: DSDateString
    properties: list[DSStringKVPair] | None

    def to_token(self) -> Token:
        """Convert to a token."""
        return Token(self.token_value, converters.convert_date(self.token_expiry))
