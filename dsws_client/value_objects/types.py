import datetime as dt
from typing import Union

import attrs

from dsws_client import utils

DateType = Union[dt.date, str]


@attrs.define(field_transformer=utils.ds_names, frozen=True)
class DSStringKVPair:
    """A key-value pair."""

    key: str
    value: str
