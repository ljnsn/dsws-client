import collections
import datetime as dt
import logging
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import msgspec

from dsws_client.ds_response import (
    DSDataResponse,
    DSError,
    DSString,
    DSSymbolResponseValue,
)
from dsws_client.exceptions import InvalidResponseError

logger = logging.getLogger(__name__)

RecordDict = Dict[Tuple[str, dt.datetime], Dict[str, Any]]


class Error(msgspec.Struct):
    """Error object."""

    field: str
    symbol: str
    message: str


class Meta(msgspec.Struct):
    """Meta object."""

    data_type_names: Dict[str, str] = msgspec.field(default_factory=dict)
    symbol_names: Dict[str, str] = msgspec.field(default_factory=dict)
    additional_responses: Dict[str, str] = msgspec.field(default_factory=dict)
    tags: List[str] = msgspec.field(default_factory=list)
    currencies: Dict[str, Dict[str, Optional[str]]] = msgspec.field(
        default_factory=lambda: collections.defaultdict(dict)
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
            tags=list({*self.tags, *other.tags}),
            currencies={**self.currencies, **other.currencies},
        )


class ParsedResponse(msgspec.Struct):
    """Parsed response object."""

    records: List[Dict[str, Any]] = msgspec.field(default_factory=list)
    errors: List[Error] = msgspec.field(default_factory=list)
    meta: Meta = msgspec.field(default_factory=Meta)


def responses_to_records(
    responses: Iterable[DSDataResponse],
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
    dates = response.pydates()
    if dates is None:
        raise InvalidResponseError(
            "Response does not contain dates. Probably the request was invalid."
        )
    meta = parse_meta(response)
    records: RecordDict = collections.defaultdict(dict)
    errors: List[Error] = []
    for data_type_value in response.data_type_values:
        field = data_type_value.data_type
        for symbol_value in data_type_value.symbol_values:
            meta.currencies[symbol_value.symbol][field] = symbol_value.currency
            process_symbol_value(
                records,
                errors,
                field,
                dates,
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
    is_error = isinstance(symbol_value, DSError)
    if is_error:
        errors.append(Error(field, symbol_value.symbol, symbol_value.value))  # type: ignore[arg-type]
    value = symbol_value.parse()
    if isinstance(symbol_value, DSString) and process_strings:
        value = process_string_value(value)  # type: ignore[arg-type]
    if isinstance(value, list):
        if len(value) != len(dates):
            raise InvalidResponseError(
                "Number of values does not match number of dates."
            )
        for date, xvalue in zip(dates, value):
            records[(symbol_value.symbol, date)][field] = xvalue
    else:
        if len(dates) > 1 and not is_error:
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
