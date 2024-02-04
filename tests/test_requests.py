import datetime as dt
import random
from typing import List, Optional, Type, Union

import pytest
from dsws_client.ds_request import (
    MAX_DATATYPES_PER_REQUEST,
    MAX_INSTRUMENTS_PER_REQUEST,
    MAX_ITEMS_PER_BUNDLE,
    DSDataRequest,
    DSDataType,
    DSDate,
    DSGetDataBundleRequest,
    DSInstrument,
)
from dsws_client.value_objects import (
    DSDateName,
    DSInstrumentPropertyName,
    DSStringKVPair,
)


@pytest.fixture(name="token")
def token_fix() -> str:
    """Return a fixed token."""
    return "test-token"


def make_snapshot_date(
    date: Union[str, dt.date, DSDateName] = dt.date(2018, 1, 1),
) -> DSDate:
    """Return a snapshot date."""
    return DSDate.construct(
        start=date,
        end=None,
        frequency=None,
        kind=0,
    )


def make_timeseries_date(
    start: Union[str, dt.date, DSDateName] = dt.date(2018, 1, 1),
    end: Union[str, dt.date, DSDateName] = dt.date(2018, 1, 1),
    frequency: str = "D",
) -> DSDate:
    """Return a fixed timeseries date."""
    return DSDate.construct(
        start=start,
        end=end,
        frequency=frequency,
        kind=1,
    )


def random_date() -> DSDate:
    """Return either a snapshot or timeseries date."""
    return make_snapshot_date() if random.random() > 0.5 else make_timeseries_date()


@pytest.fixture(name="snapshot_request")
def data_request_fix(snapshot_date: DSDate) -> DSDataRequest:
    """Return a fixed data request."""
    return DSDataRequest(
        instrument=DSInstrument(value="IBM,MSFT"),
        data_types=[DSDataType(value="P")],
        date=snapshot_date,
    )


def make_data_request(
    date: DSDate,
    instrument: Optional[DSInstrument] = None,
    data_types: Optional[List[DSDataType]] = None,
    tag: Optional[str] = None,
) -> DSDataRequest:
    """Generate a data request."""
    if instrument is None:
        instrument = DSInstrument(value="IBM,MSFT")
    if data_types is None:
        data_types = [DSDataType(value="P")]
    return DSDataRequest(
        instrument=instrument,
        data_types=data_types,
        date=date,
        tag=tag,
    )


@pytest.mark.parametrize("date", [make_snapshot_date(), make_timeseries_date()])
def test_request_instantiation(date: DSDate) -> None:
    """Verify that a request is instantiated properly."""
    data_request = make_data_request(date)

    assert data_request.instrument.identifiers == ["IBM", "MSFT"]


@pytest.mark.parametrize(
    ("instrument", "data_types", "expected"),
    [
        (
            DSInstrument(",".join(["DUMMY"] * (MAX_INSTRUMENTS_PER_REQUEST + 1))),
            [DSDataType("P")],
            ValueError,
        ),
        (
            DSInstrument("DUMMY"),
            [DSDataType("P")] * (MAX_DATATYPES_PER_REQUEST + 1),
            ValueError,
        ),
        (
            DSInstrument(",".join(["DUMMY"] * 40)),
            [DSDataType("P")] * 3,
            ValueError,
        ),
    ],
)
def test_request_validation(
    instrument: DSInstrument,
    data_types: List[DSDataType],
    expected: Type[Exception],
) -> None:
    """Verify that requests are validated properly."""
    with pytest.raises(expected):
        DSDataRequest(
            instrument=instrument,
            data_types=data_types,
            date=random_date(),
        )


def test_bundle_validation(token: str) -> None:
    """Verify that bundles are validated properly."""
    requests = [
        make_data_request(random_date()) for _ in range(MAX_ITEMS_PER_BUNDLE + 1)
    ]

    with pytest.raises(ValueError):  # noqa: PT011
        DSGetDataBundleRequest(data_requests=requests, token_value=token)


# ruff: noqa: ERA001
@pytest.mark.parametrize(
    ("identifiers", "expected", "expected_properties"),
    [
        ("IBM,MSFT", ["IBM", "MSFT"], []),
        (
            ["IBM", "MSFT"],
            ["IBM", "MSFT"],
            [DSStringKVPair(DSInstrumentPropertyName.SYMBOL_SET, True)],
        ),
        # TODO: fix expression splitting
        # (
        #     "PCH#(VOD(P),3M)|E",
        #     ["PCH#(VOD(P),3M)"],
        #     [DSStringKVPair(DSInstrumentPropertyName.EXPRESSION, True)],
        # ),
        (
            "LS&PCOMP|L",
            ["LS&PCOMP"],
            [DSStringKVPair(DSInstrumentPropertyName.INSTRUMENT_LIST, True)],
        ),
    ],
)
def test_construct_instrument(
    identifiers: Union[str, List[str]],
    expected: List[str],
    expected_properties: List[DSStringKVPair],
) -> None:
    """Verify instrument is constructed properly."""
    instrument = DSInstrument.construct(identifiers)

    assert instrument.identifiers == expected
    assert instrument.properties == expected_properties

    # test with return_names
    instrument = DSInstrument.construct(identifiers, return_names=True)

    assert instrument.properties == [
        *expected_properties,
        DSStringKVPair(DSInstrumentPropertyName.RETURN_NAME, True),
    ]
