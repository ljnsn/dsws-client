import datetime as dt
import re
from typing import Union


def convert_date(date_str: Union[str, dt.datetime]) -> dt.datetime:
    """Convert a timestamp from Datastream to datetime."""
    if isinstance(date_str, dt.datetime):
        return date_str
    match = re.search(r"[0-9+]+", date_str)
    if match is None:
        msg = f"invalid date string: {date_str}"
        raise ValueError(msg)
    timestamp = match.group(0)
    tzinfo = dt.timezone.utc
    if "+" in timestamp:
        timestamp, offset = timestamp.split("+")
        timedelta = dt.timedelta(hours=int(offset[:2]), minutes=int(offset[2:]))
        tzinfo = dt.timezone(timedelta)
    timestamp_int = int(timestamp)
    return dt.datetime.fromtimestamp(timestamp_int / 1000, tz=tzinfo)
