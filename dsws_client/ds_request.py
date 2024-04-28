"""DSWS requests."""

import datetime as dt
import sys
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)

import msgspec

from dsws_client.value_objects import DSStringKVPair, enums

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

# request limits
MAX_INSTRUMENTS_PER_REQUEST = 50
MAX_DATATYPES_PER_REQUEST = 50
MAX_ITEMS_PER_REQUEST = 100

# bundle limits
MAX_REQUESTS_PER_BUNDLE = 20
MAX_ITEMS_PER_BUNDLE = 500


class DSRequest(Protocol):
    """A DSWS request."""

    path: ClassVar[str]
    properties: List[DSStringKVPair]


_HINT_MAP = {
    "L": DSStringKVPair(enums.DSInstrumentPropertyName.INSTRUMENT_LIST, True),
    "E": DSStringKVPair(enums.DSInstrumentPropertyName.EXPRESSION, True),
}


class DSGetTokenRequest(msgspec.Struct, rename="pascal"):
    """Object that defines a token request."""

    path: ClassVar[str] = "GetToken"
    user_name: str
    password: str
    properties: List[DSStringKVPair] = msgspec.field(default_factory=list)

    def add_property(self, key: str, value: str) -> None:
        """Add a property to the request."""
        self.properties.append(DSStringKVPair(key, value))


class DSInstrument(msgspec.Struct, rename="pascal"):
    """Object that defines an instrument."""

    value: str
    properties: List[DSStringKVPair] = msgspec.field(default_factory=list)

    @property
    def identifiers(self) -> List[str]:
        """Return the identifiers."""
        # TODO: this breaks for expressions
        return self.value.split(",")

    @classmethod
    def from_list(cls, instrument_list: List[str]) -> "DSInstrument":
        """Return an instrument from a list of instrument names."""
        properties = [DSStringKVPair(enums.DSInstrumentPropertyName.SYMBOL_SET, True)]
        return cls(",".join(instrument_list), properties)

    @classmethod
    def construct(
        cls,
        identifiers: Union[str, List[str]],
        return_names: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ) -> "DSInstrument":
        """Return an instrument."""
        if isinstance(identifiers, list):
            instance = cls.from_list(identifiers)
        else:
            value = identifiers
            hint_properties = []
            if "|" in value:
                value, hint = identifiers.split("|")
                hint_properties.append(_HINT_MAP[hint])
            instance = cls(value, hint_properties)
        if return_names:
            instance.properties.append(
                DSStringKVPair(enums.DSInstrumentPropertyName.RETURN_NAME, True)
            )
        properties = properties or {}
        for key, value in properties.items():
            instance.properties.append(DSStringKVPair(key, value))
        return instance


class DSDataType(msgspec.Struct, rename="pascal"):
    """A data type (field)."""

    value: str
    properties: List[DSStringKVPair] = msgspec.field(default_factory=list)

    @classmethod
    def construct(
        cls,
        field: str,
        return_name: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ) -> "DSDataType":
        """Construct a data type."""
        instance = cls(field)
        if return_name:
            instance.properties.append(DSStringKVPair("ReturnName", True))
        properties = properties or {}
        for key, value in properties.items():
            instance.properties.append(DSStringKVPair(key, value))
        return instance


class DSDate(msgspec.Struct, rename="pascal"):
    """Date information."""

    start: str
    end: str
    frequency: Optional[enums.DSDateFrequencyName]
    kind: enums.DSDateKind

    @classmethod
    def construct(
        cls,
        start: Optional[Union[str, dt.date, enums.DSDateName]],
        end: Optional[Union[str, dt.date, enums.DSDateName]],
        frequency: Optional[str],
        kind: int,
    ) -> "DSDate":
        """Construct a date."""
        return cls(
            cls._convert_date(start),
            cls._convert_date(end),
            None if frequency is None else enums.DSDateFrequencyName(frequency),
            enums.DSDateKind(kind),
        )

    @classmethod
    def _convert_date(
        cls,
        date: Optional[Union[str, dt.date, enums.DSDateName]],
    ) -> str:
        """Convert a date to a string."""
        if date is None:
            return ""
        if isinstance(date, dt.date):
            return date.isoformat()
        if isinstance(date, str):
            date = enums.DSDateName(date)
        return date.value


class DSDataRequest(msgspec.Struct, rename="pascal"):
    """Object that defines a data request."""

    instrument: DSInstrument
    data_types: Annotated[List[DSDataType], msgspec.Meta(min_length=1)]
    date: DSDate
    tag: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate that a request complies with DSWS request limits."""
        if len(self.instrument.identifiers) > MAX_INSTRUMENTS_PER_REQUEST:
            msg = (
                f"Request contains more than {MAX_INSTRUMENTS_PER_REQUEST} instruments."
            )
            raise ValueError(msg)
        if len(self.data_types) > MAX_DATATYPES_PER_REQUEST:
            msg = f"Request contains more than {MAX_DATATYPES_PER_REQUEST} data types."
            raise ValueError(msg)
        if (
            len(self.instrument.identifiers) * len(self.data_types)
            > MAX_ITEMS_PER_REQUEST
        ):
            msg = f"Request contains more than {MAX_ITEMS_PER_REQUEST} items."
            raise ValueError(msg)


class DSGetDataRequest(msgspec.Struct, rename="pascal"):
    """Object that contains a data request."""

    path: ClassVar[str] = "GetData"
    token_value: str
    data_request: DSDataRequest
    properties: List[DSStringKVPair] = msgspec.field(default_factory=list)

    def add_property(self, key: str, value: str) -> None:
        """Add a property to the request."""
        self.properties.append(DSStringKVPair(key, value))


class DSGetDataBundleRequest(msgspec.Struct, rename="pascal"):
    """Object that contains multiple data requests."""

    path: ClassVar[str] = "GetDataBundle"
    token_value: str
    data_requests: Annotated[List[DSDataRequest], msgspec.Meta(min_length=1)]
    properties: List[DSStringKVPair] = msgspec.field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate that a bundle complies with DSWS bundle limits."""
        if len(self.data_requests) > MAX_REQUESTS_PER_BUNDLE:
            msg = f"Bundle contains more than {MAX_REQUESTS_PER_BUNDLE} requests."
            raise ValueError(msg)
        total_items = sum(
            len(request.instrument.identifiers) * len(request.data_types)
            for request in self.data_requests
        )
        if total_items > MAX_ITEMS_PER_BUNDLE:
            msg = f"Bundle contains more than {MAX_ITEMS_PER_BUNDLE} items."
            raise ValueError(msg)

    def add_property(self, key: str, value: str) -> None:
        """Add a property to the request."""
        self.properties.append(DSStringKVPair(key, value))


T = TypeVar("T", bound=msgspec.Struct)


def evolve(instance: T, **changes: object) -> T:
    """Evolve an instance."""

    def get_field(name: str) -> Any:
        """Return the field."""
        return changes.get(name, getattr(instance, name))

    return instance.__class__(
        **{field: get_field(field) for field in instance.__struct_fields__}
    )


def bundle_identifiers(
    instrument: DSInstrument,
    n_fields: int,
) -> List[Tuple[DSInstrument, ...]]:
    """
    Make a list of bundles of identifiers.

    Args:
        instrument: A DSInstrument to bundle identifiers for.
        n_fields: Number of fields in the request.

    Returns:
        List of bundles of identifiers.

    Raises:
        ValueError: If the number of fields exceeds the maximum allowed.
    """
    if n_fields > MAX_DATATYPES_PER_REQUEST:
        raise ValueError("Number of fields exceeds maximum allowed.")
    identifiers = instrument.identifiers
    bundles = []
    n_identifiers_per_batch = MAX_ITEMS_PER_BUNDLE // n_fields
    for batch_idx in range(0, len(identifiers), n_identifiers_per_batch):
        batch_identifiers = identifiers[batch_idx : batch_idx + n_identifiers_per_batch]
        bundles.append(
            split_bundle_identifiers(
                evolve(instrument, value=",".join(batch_identifiers)),
                n_fields,
            )
        )
    return bundles


def split_bundle_identifiers(
    bundle_instrument: DSInstrument,
    n_fields: int,
) -> Tuple[DSInstrument, ...]:
    """
    Split identifiers per bundle identifiers per bundle request.

    Args:
        bundle_instrument: A DSInstrument to split.
        n_fields: Number of fields in the request.

    Returns:
        Tuple of DSInstruments.
    """
    identifiers = bundle_instrument.identifiers
    request_bundles = []
    n_identifiers_per_request = min(
        MAX_INSTRUMENTS_PER_REQUEST,
        MAX_ITEMS_PER_REQUEST // n_fields,
    )
    for request_idx in range(0, len(identifiers), n_identifiers_per_request):
        bundle_request_identifiers = identifiers[
            request_idx : request_idx + n_identifiers_per_request
        ]
        request_bundles.append(
            evolve(bundle_instrument, value=",".join(bundle_request_identifiers))
        )
    return tuple(request_bundles)
