import datetime as dt
from typing import Any, Union

import msgspec

DateType = Union[dt.date, str]


class DSStringKVPair(msgspec.Struct, rename="pascal", frozen=True):
    """A key-value pair."""

    key: str
    value: Any


class Token(msgspec.Struct, frozen=True):
    """A token."""

    token_value: str
    token_expiry: dt.datetime

    @property
    def is_expired(self) -> bool:
        """Return True if the token is expired."""
        return (self.token_expiry + dt.timedelta(minutes=1)) < dt.datetime.now(
            tz=dt.timezone.utc
        )
