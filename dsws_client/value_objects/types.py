import datetime as dt
from typing import Any, Union

import msgspec

DateType = Union[dt.date, str]


class DSStringKVPair(msgspec.Struct, rename="pascal", frozen=True):
    """A key-value pair."""

    key: str
    value: Any
