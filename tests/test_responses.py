from typing import Any, Dict

import msgspec
import pytest
from dsws_client.ds_response import (
    DSDataResponse,
    DSGetDataBundleResponse,
    DSGetDataResponse,
    DSGetTokenResponse,
)


@pytest.fixture(name="token_response_dict")
def token_response_fix() -> Dict[str, Any]:
    """Return an example token response."""
    return {
        "Properties": None,
        "TokenExpiry": "/Date(928149600000+0000)/",
        "TokenValue": "n9IcXCXIq+ApBEe0zLBeTrU11D65F6BB2ED74E3467EA0EBE0C",
    }


def test_token_response(token_response_dict: Dict[str, Any]) -> None:
    """Verify responses can be initialized with field aliases."""
    token_response = msgspec.convert(
        token_response_dict,
        type=DSGetTokenResponse,
    )

    assert token_response.token_value == token_response_dict["TokenValue"]
    assert token_response.token_expiry == token_response_dict["TokenExpiry"]
    assert token_response.properties == token_response_dict["Properties"]


def test_init_get_data_response(timeseries_response: Dict[str, Any]) -> None:
    """Verify responses can be initialized with field aliases."""
    response = msgspec.convert(
        {"DataResponse": timeseries_response},
        type=DSGetDataResponse,
    )

    assert response.data_response == msgspec.convert(
        timeseries_response,
        type=DSDataResponse,
    )


def test_init_get_data_bundle_response(timeseries_response: Dict[str, Any]) -> None:
    """Verify responses can be initialized with field aliases."""
    response = msgspec.convert(
        {"DataResponses": [timeseries_response]},
        type=DSGetDataBundleResponse,
    )

    assert response.data_responses == [
        msgspec.convert(
            timeseries_response,
            type=DSDataResponse,
        )
    ]
