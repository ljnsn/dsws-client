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


@pytest.fixture(name="data_response_dict")
def data_response_fix() -> Dict[str, Any]:
    """Return an example data response."""
    return {
        "AdditionalResponses": [{"Key": "Frequency", "Value": "D"}],
        "DataTypeNames": [{"Key": "P", "Value": None}],
        "DataTypeValues": [
            {
                "DataType": "P",
                "SymbolValues": [
                    {
                        "Currency": "£",
                        "Symbol": "VOD",
                        "Type": 10,
                        "Value": [92.71, 92.01, 90.79, 89.81, 90.66, 89.68],
                    }
                ],
            }
        ],
        "Dates": [
            "/Date(1681689600000+0000)/",
            "/Date(1681776000000+0000)/",
            "/Date(1681862400000+0000)/",
            "/Date(1681948800000+0000)/",
            "/Date(1682035200000+0000)/",
            "/Date(1682294400000+0000)/",
        ],
        "SymbolNames": [{"Key": "VOD", "Value": "VODAFONE GROUP"}],
        "Tag": None,
    }


def test_init_get_data_response(data_response_dict: Dict[str, Any]) -> None:
    """Verify responses can be initialized with field aliases."""
    response = DSGetDataResponse(data_response_dict, None)

    assert response.data_response == converters.convert_model(
        (DSDataResponse,),
        data_response_dict,
    )


def test_init_get_data_bundle_response(data_response_dict: Dict[str, Any]) -> None:
    """Verify responses can be initialized with field aliases."""
    response = DSGetDataBundleResponse([data_response_dict], None)

    assert response.data_responses == [
        converters.convert_model(
            (DSDataResponse,),
            data_response_dict,
        )
    ]
