import datetime as dt
from typing import Optional, Union

import msgspec

DateType = Union[dt.date, str]


class DSStringKVPair(msgspec.Struct, rename="pascal", frozen=True):
    """A key-value pair."""

    key: str
    value: Optional[str]
