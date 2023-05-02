import datetime as dt
import re
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union

from dsws_client.value_objects import DateType, DSDateName, DSStringKVPair


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


def convert_date_list(date_list: List[Union[str, dt.datetime]]) -> List[dt.datetime]:
    """Convert a list of date strings to a list of datetime."""
    return [convert_date(date) for date in date_list]


def convert_request_date(date: DateType) -> Union[str, DSDateName]:
    """Convert a date to a string."""
    if isinstance(date, dt.date):
        return date.isoformat()
    try:
        return DSDateName(date)
    except ValueError:
        pass
    return date


ModelT = TypeVar("ModelT")


def convert_model(
    model_types: Tuple[Type[ModelT], ...],
    data: Dict[str, Any],
) -> ModelT:
    """Convert a dict to a model."""
    for model_type in model_types:
        try:
            return model_type(**data)
        except TypeError:
            continue
    msg = f"could not convert {data} to a model"
    raise TypeError(msg)


def convert_model_list(
    model_types: Tuple[Type[ModelT], ...],
    items: List[Union[Dict[str, Any], ModelT]],
) -> List[ModelT]:
    """Convert a list of dicts to a list of models."""
    models = []
    for item in items:
        if any(isinstance(item, model_type) for model_type in model_types):
            models.append(item)
            continue
        models.append(convert_model(model_types, item))  # type: ignore[arg-type]
    return models  # type: ignore[return-value]


def convert_key_value_pairs(
    items: Union[List[DSStringKVPair], Dict[str, str]]
) -> DSStringKVPair:
    """Convert a dictionary to a list of key-value pairs."""
    if isinstance(items, list):
        return convert_model_list((DSStringKVPair,), items)
    return [DSStringKVPair(key, value) for key, value in items.items()]
