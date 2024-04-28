import datetime as dt
import os

import pytest
from dotenv import load_dotenv
from dsws_client import DSWSClient

load_dotenv()


def has_credentials() -> bool:
    """Return True if credentials are available."""
    return (
        os.environ.get("DSWS_USERNAME") is not None
        and os.environ.get("DSWS_PASSWORD") is not None
    )


@pytest.fixture(name="client")
def client_fix() -> DSWSClient:
    """Provide a DSWSClient instance."""
    username = os.getenv("DSWS_USERNAME", "")
    password = os.getenv("DSWS_PASSWORD", "")
    return DSWSClient(username, password)


@pytest.fixture(name="tag")
def tag_fix() -> str:
    """Provide a test tag."""
    return "test"


@pytest.mark.skipif(not has_credentials(), reason="no credentials available")
def test_get_token(client: DSWSClient) -> None:
    """Test get_token method."""
    token_response = client.fetch_token()

    assert token_response.token_value is not None
    assert token_response.token_expiry is not None
    assert not token_response.is_expired


@pytest.mark.skipif(not has_credentials(), reason="no credentials available")
def test_fetch_snapshot_data(client: DSWSClient, tag: str) -> None:
    """Test fetch_snapshot_data method."""
    identifiers = ["VOD", "U:JPM"]
    fields = ["NAME", "ISIN"]
    start = dt.date(2020, 1, 1)
    response = client.fetch_snapshot_data(
        identifiers=identifiers,
        fields=fields,
        start=start,
        tag=tag,
    )

    assert len(response.records) == 2
    assert len(response.errors) == 0
    assert len(response.meta.data_type_names) == 2
    assert len(response.meta.symbol_names) == 2
    assert len(response.meta.additional_responses) == 0
    assert len(response.meta.tags) == 1
    assert all(isinstance(record["date"], dt.datetime) for record in response.records)


@pytest.mark.skipif(not has_credentials(), reason="no credentials available")
def test_fetch_timeseries_data(client: DSWSClient, tag: str) -> None:
    """Test fetch_timeseries_data method."""
    identifiers = ["VOD", "U:JPM"]
    fields = ["P", "MV"]
    start = dt.date(2020, 1, 1)
    end = dt.date(2020, 1, 10)
    response = client.fetch_timeseries_data(
        identifiers=identifiers,
        fields=fields,
        start=start,
        end=end,
        tag=tag,
    )

    assert len(response.records) == 16
    assert len(response.errors) == 0
    assert len(response.meta.data_type_names) == 2
    assert len(response.meta.symbol_names) == 2
    assert len(response.meta.additional_responses) == 1
    assert len(response.meta.tags) == 1
