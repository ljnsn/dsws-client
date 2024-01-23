import collections
import datetime as dt
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import attrs

from dsws_client import converters
from dsws_client.ds_response import DSDataResponse, DSSymbolResponseValue
from dsws_client.exceptions import InvalidResponseError
from dsws_client.value_objects import DSSymbolResponseValueType

logger = logging.getLogger(__name__)

RecordDict = Dict[Tuple[str, dt.datetime], Dict[str, Any]]


@attrs.define()
class Error:
    """Error object."""

    field: str
    symbol: str
    message: str


@attrs.define()
class Meta:
    """Meta object."""

    data_type_names: Dict[str, str] = attrs.field(factory=dict)
    symbol_names: Dict[str, str] = attrs.field(factory=dict)
    additional_responses: Dict[str, str] = attrs.field(factory=dict)
    tags: List[str] = attrs.field(factory=list)
    currencies: Dict[str, Dict[str, Optional[str]]] = attrs.field(
        factory=lambda: collections.defaultdict(dict)
    )

    def merge(self, other: "Meta") -> "Meta":
        """Merge this meta object with another one."""
        return Meta(
            data_type_names={**self.data_type_names, **other.data_type_names},
            symbol_names={**self.symbol_names, **other.symbol_names},
            additional_responses={
                **self.additional_responses,
                **other.additional_responses,
            },
            tags=[*self.tags, *other.tags],
            currencies={**self.currencies, **other.currencies},
        )


@attrs.define()
class ParsedResponse:
    """Parsed response object."""

    records: List[Dict[str, Any]] = attrs.field(factory=list)
    errors: List[Error] = attrs.field(factory=list)
    meta: Meta = attrs.field(factory=Meta)


def responses_to_records(
    responses: List[DSDataResponse],
    *,
    process_strings: bool = True,
) -> ParsedResponse:
    """Parse a list of DSDataResponse objects into a list of records."""
    parsed_response = ParsedResponse()
    for response in responses:
        try:
            _parsed_response = parse_response(response, process_strings=process_strings)
        except InvalidResponseError as exc:
            logger.warning("Invalid response, skipping")
            logger.debug(exc)
            continue
        parsed_response.records.extend(_parsed_response.records)
        parsed_response.errors.extend(_parsed_response.errors)
        parsed_response.meta = parsed_response.meta.merge(_parsed_response.meta)
    return parsed_response


def parse_response(
    response: DSDataResponse,
    *,
    process_strings: bool = True,
) -> ParsedResponse:
    """Parse a DSDataResponse object into a list of records."""
    if response.dates is None:
        raise InvalidResponseError(
            "Response does not contain dates. Probably the request was invalid."
        )
    meta = parse_meta(response)
    records = collections.defaultdict(dict)
    errors = []
    for data_type_value in response.data_type_values:
        field = data_type_value.data_type
        for symbol_value in data_type_value.symbol_values:
            meta.currencies[symbol_value.symbol][field] = symbol_value.currency
            process_symbol_value(
                records,
                errors,
                field,
                response.dates,
                symbol_value,
                process_strings=process_strings,
            )
    record_list = []
    for (symbol, date), record in records.items():
        record["symbol"] = symbol
        record["date"] = date
        record_list.append(record)
    return ParsedResponse(record_list, errors, meta)


def process_symbol_value(  # noqa: PLR0913
    records: RecordDict,
    errors: List[Error],
    field: str,
    dates: List[dt.datetime],
    symbol_value: DSSymbolResponseValue,
    *,
    process_strings: bool,
) -> None:
    """Parse a symbol value into a dictionary."""
    is_error = symbol_value.type == DSSymbolResponseValueType.ERROR
    if is_error:
        errors.append(Error(field, symbol_value.symbol, symbol_value.value))
    func = _CONVERSION_MAP[symbol_value.type]
    value = func(symbol_value.value)
    if symbol_value.type == DSSymbolResponseValueType.STRING and process_strings:
        value = process_string_value(value)
    if is_error:
        for date in dates:
            records[(symbol_value.symbol, date)][field] = value
    elif isinstance(value, list):
        if len(value) != len(dates):
            raise InvalidResponseError(
                "Number of values does not match number of dates."
            )
        for date, xvalue in zip(dates, value):
            records[(symbol_value.symbol, date)][field] = xvalue
    else:
        if len(dates) > 1:
            raise InvalidResponseError("More than one date found for single value.")
        records[(symbol_value.symbol, dates[0])][field] = value


def parse_meta(response: DSDataResponse) -> Meta:
    """Parse meta information from a response."""
    meta = Meta()
    if response.data_type_names:
        meta.data_type_names = {
            kv_pair.key: kv_pair.value for kv_pair in response.data_type_names
        }
    if response.symbol_names:
        meta.symbol_names = {
            kv_pair.key: kv_pair.value for kv_pair in response.symbol_names
        }
    if response.additional_responses:
        meta.additional_responses = {
            kv_pair.key: kv_pair.value for kv_pair in response.additional_responses
        }
    if response.tag:
        meta.tags.append(response.tag)
    return meta


def process_string_value(value: str) -> Optional[Union[str, bool]]:
    """Process a string value further."""
    return {
        "NA": None,
        "N": False,
        "Y": True,
    }.get(value, value)


def parse_empty_value(value: Any) -> None:  # noqa: ARG001
    """Parse an empty value."""
    return


def parse_boolean_value(value: Any) -> bool:
    """Parse a boolean value."""
    return {
        "Y": True,
        "true": True,
        "True": True,
        "N": False,
        "false": False,
        "False": False,
    }[value]


def parse_int_value(value: Any) -> int:
    """Parse an integer value."""
    return int(value)


def parse_date_time_value(value: Any) -> dt.datetime:
    """Parse a date/time value."""
    return converters.convert_date(value)


def parse_double_value(value: Any) -> float:
    """Parse a double value."""
    return float(value)


def parse_string_value(value: Any) -> str:
    """Parse a string value."""
    return str(value)


def parse_bool_array(values: List[Any]) -> List[bool]:
    """Parse a boolean array."""
    return [parse_boolean_value(value) for value in values]


def prase_int_array(values: List[Any]) -> List[int]:
    """Parse an integer array."""
    return [parse_int_value(value) for value in values]


def parse_date_time_array(values: List[Any]) -> List[dt.datetime]:
    """Parse a date/time array."""
    return [parse_date_time_value(value) for value in values]


def parse_double_array(values: List[Any]) -> List[float]:
    """Parse a double array."""
    return [parse_double_value(value) for value in values]


def parse_string_array(values: List[Any]) -> List[str]:
    """Parse a string array."""
    return [parse_string_value(value) for value in values]


def parse_object_array(values: List[Any]) -> List[Any]:
    """Parse an object array."""
    return values


_CONVERSION_MAP = {
    DSSymbolResponseValueType.ERROR: parse_empty_value,
    DSSymbolResponseValueType.EMPTY: parse_empty_value,
    DSSymbolResponseValueType.BOOL: parse_boolean_value,
    DSSymbolResponseValueType.INT: parse_int_value,
    DSSymbolResponseValueType.DATE_TIME: parse_date_time_value,
    DSSymbolResponseValueType.DOUBLE: parse_double_value,
    DSSymbolResponseValueType.STRING: parse_string_value,
    DSSymbolResponseValueType.BOOL_ARRAY: parse_bool_array,
    DSSymbolResponseValueType.INT_ARRAY: prase_int_array,
    DSSymbolResponseValueType.DATE_TIME_ARRAY: parse_date_time_array,
    DSSymbolResponseValueType.DOUBLE_ARRAY: parse_double_array,
    DSSymbolResponseValueType.STRING_ARRAY: parse_string_array,
    DSSymbolResponseValueType.OBJECT_ARRAY: parse_object_array,
}
