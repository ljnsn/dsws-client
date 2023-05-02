from typing import Any, Dict

import pytest


@pytest.fixture()
def timeseries_response() -> Dict[str, Any]:
    """Return an example timeseries response."""
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


@pytest.fixture()
def snapshot_response() -> Dict[str, Any]:
    """Return an example snapshot response."""
    return {
        "AdditionalResponses": None,
        "DataTypeNames": [
            {"Key": "NAME", "Value": "NAME"},
            {"Key": "ISIN", "Value": "ISIN CODE"},
        ],
        "DataTypeValues": [
            {
                "DataType": "NAME",
                "SymbolValues": [
                    {
                        "Currency": "£ ",
                        "Symbol": "VOD",
                        "Type": 6,
                        "Value": "VODAFONE GROUP",
                    },
                    {
                        "Currency": "U$",
                        "Symbol": "U:JPM",
                        "Type": 6,
                        "Value": "JP MORGAN CHASE & CO.",
                    },
                ],
            },
            {
                "DataType": "ISIN",
                "SymbolValues": [
                    {
                        "Currency": "£",
                        "Symbol": "VOD",
                        "Type": 6,
                        "Value": "GB00BH4HKS39",
                    },
                    {
                        "Currency": "U$",
                        "Symbol": "U:JPM",
                        "Type": 6,
                        "Value": "US46625H1005",
                    },
                ],
            },
        ],
        "Dates": ["/Date(1577836800000+0000)/"],
        "SymbolNames": [
            {"Key": "VOD", "Value": "VOD"},
            {"Key": "U:JPM", "Value": "U:JPM"},
        ],
        "Tag": "test",
    }


@pytest.fixture()
def invalid_response(timeseries_response: Dict[str, Any]) -> Dict[str, Any]:
    """Return a response with missing dates."""
    response = timeseries_response.copy()
    response["Dates"] = []
    return response
