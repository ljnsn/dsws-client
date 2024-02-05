from typing import Any, Dict, Optional, Union

import msgspec
import pytest
from dsws_client.ds_response import DSDataResponse, DSDoubleArray
from dsws_client.exceptions import InvalidResponseError
from dsws_client.parse import parse_response, process_string_value, process_symbol_value


def test_invalid_response(invalid_response: Dict[str, Any]) -> None:
    """Verify parsing an invalid response raises an error."""
    response = msgspec.convert(invalid_response, type=DSDataResponse)

    with pytest.raises(InvalidResponseError):
        parse_response(response)


def test_process_response_invalid_value() -> None:
    """Verify processing a value raises an exception if invalid."""
    symbol_value = DSDoubleArray(
        symbol="AAPL",
        currency="E",
        value=[1, 2, 3],
    )

    with pytest.raises(InvalidResponseError):
        process_symbol_value({}, [], "field", [], symbol_value, process_strings=False)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("NA", None), ("N", False), ("Y", True), ("TEST", "TEST")],
)
def test_process_string_value(value: str, expected: Optional[Union[str, bool]]) -> None:
    """Verify strings are cast to correct type."""
    assert process_string_value(value) == expected
