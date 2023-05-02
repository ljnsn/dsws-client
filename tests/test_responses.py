from typing import Any, Dict

import pytest
from dsws_client import converters
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
        "TokenExpiry": "\\/Date(928149600000+0000)\\/",
        "TokenValue": "n9IcXCXIq+ApBEe0zLBeTrU11D65F6BB2ED74E3467EA0EBE0C",
    }


def test_token_response(token_response_dict: Dict[str, Any]) -> None:
    """Verify responses can be initialized with field aliases."""
    token_response = DSGetTokenResponse(**token_response_dict)

    assert token_response.token_value == token_response_dict["TokenValue"]
    assert token_response.token_expiry == converters.convert_date(
        token_response_dict["TokenExpiry"]
    )
    assert token_response.properties == token_response_dict["Properties"]


def test_init_get_data_response(timeseries_response: Dict[str, Any]) -> None:
    """Verify responses can be initialized with field aliases."""
    response = DSGetDataResponse(timeseries_response, None)

    assert response.data_response == converters.convert_model(
        (DSDataResponse,),
        timeseries_response,
    )


def test_init_get_data_bundle_response(timeseries_response: Dict[str, Any]) -> None:
    """Verify responses can be initialized with field aliases."""
    response = DSGetDataBundleResponse([timeseries_response], None)

    assert response.data_responses == [
        converters.convert_model(
            (DSDataResponse,),
            timeseries_response,
        )
    ]
