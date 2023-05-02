import enum
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union

import attrs

from dsws_client import converters, utils
from dsws_client.exceptions import InvalidRequestError
from dsws_client.value_objects import (
    DSDateFrequencyName,
    DSDateKind,
    DSDateName,
    DSInstrumentPropertyName,
    DSStringKVPair,
)

# request limits
MAX_INSTRUMENTS_PER_REQUEST = 50
MAX_DATATYPES_PER_REQUEST = 50
MAX_ITEMS_PER_REQUEST = 100

# bundle limits
MAX_REQUESTS_PER_BUNDLE = 20
MAX_ITEMS_PER_BUNDLE = 500


class DSRequest(attrs.AttrsInstance):
    """Protocol for DS requests."""

    path: ClassVar[str]


_HINT_MAP = {
    "L": DSStringKVPair(DSInstrumentPropertyName.INSTRUMENT_LIST, True),
    "E": DSStringKVPair(DSInstrumentPropertyName.EXPRESSION, True),
}

kv_validator = attrs.validators.deep_iterable(
    attrs.validators.instance_of(DSStringKVPair),
    attrs.validators.instance_of(list),
)


@attrs.define()
class DSInstrument:
    """An instrument."""

    value: str = attrs.field(validator=attrs.validators.instance_of(str))
    properties: List[DSStringKVPair] = attrs.field(
        factory=list,
        converter=converters.convert_key_value_pairs,
        validator=kv_validator,
    )

    @property
    def identifiers(self) -> List[str]:
        """Return the identifiers."""
        # TODO: this breaks for expressions
        return self.value.split(",")

    @classmethod
    def from_list(cls, instrument_list: List[str]) -> "DSInstrument":
        """Return an instrument from a list of instrument names."""
        properties = [DSStringKVPair(DSInstrumentPropertyName.SYMBOL_SET, True)]
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
                DSStringKVPair(DSInstrumentPropertyName.RETURN_NAME, True)
            )
        properties = properties or {}
        for key, value in properties.items():
            instance.properties.append(DSStringKVPair(key, value))
        return instance


@attrs.define()
class DSDataType:
    """A data type (field)."""

    value: str
    properties: List[DSStringKVPair] = attrs.field(
        factory=list,
        converter=converters.convert_key_value_pairs,
        validator=kv_validator,
    )

    @classmethod
    def construct(
        cls,
        field: str,
        return_names: bool = False,
        properties: Optional[Dict[str, str]] = None,
    ) -> "DSDataType":
        """Construct a data type."""
        instance = cls(field)
        if return_names:
            instance.properties.append(DSStringKVPair("ReturnName", True))
        properties = properties or {}
        for key, value in properties.items():
            instance.properties.append(DSStringKVPair(key, value))
        return instance


@attrs.define()
class DSDate:
    """Date information."""

    start: Union[str, DSDateName] = attrs.field(
        converter=converters.convert_request_date,
        validator=attrs.validators.instance_of((str, DSDateName)),
    )
    end: Union[str, DSDateName] = attrs.field(
        converter=converters.convert_request_date,
        validator=attrs.validators.instance_of((str, DSDateName)),
    )
    frequency: Optional[DSDateFrequencyName] = attrs.field(
        converter=attrs.converters.optional(
            lambda value: value
            if isinstance(value, DSDateFrequencyName)
            else DSDateFrequencyName(value)
        ),
        validator=attrs.validators.optional(
            attrs.validators.instance_of(DSDateFrequencyName)
        ),
    )
    kind: DSDateKind = attrs.field(
        converter=lambda value: value
        if isinstance(value, DSDateKind)
        else DSDateKind(value),
        validator=attrs.validators.instance_of(DSDateKind),
    )


@attrs.define()
class DSDataRequest:
    """Object that defines a data request."""

    instrument: DSInstrument = attrs.field(
        validator=attrs.validators.instance_of(DSInstrument)
    )
    data_types: List[DSDataType] = attrs.field(
        validator=attrs.validators.deep_iterable(
            attrs.validators.instance_of(DSDataType),
            attrs.validators.and_(
                attrs.validators.instance_of(list),
                attrs.validators.min_len(1),
            ),
        )
    )
    date: DSDate = attrs.field(validator=attrs.validators.instance_of(DSDate))
    tag: Optional[str] = attrs.field(
        default=None,
        validator=attrs.validators.optional(attrs.validators.instance_of(str)),
    )

    def __attrs_post_init__(self) -> None:
        """Validate that a request complies with DSWS request limits."""
        if len(self.instrument.identifiers) > MAX_INSTRUMENTS_PER_REQUEST:
            msg = (
                f"Request contains more than {MAX_INSTRUMENTS_PER_REQUEST} instruments."
            )
            raise InvalidRequestError(msg)
        if len(self.data_types) > MAX_DATATYPES_PER_REQUEST:
            msg = f"Request contains more than {MAX_DATATYPES_PER_REQUEST} data types."
            raise InvalidRequestError(msg)
        if (
            len(self.instrument.identifiers) * len(self.data_types)
            > MAX_ITEMS_PER_REQUEST
        ):
            msg = f"Request contains more than {MAX_ITEMS_PER_REQUEST} items."
            raise InvalidRequestError(msg)


@attrs.define()
class DSGetDataRequest:
    """Object that contains a data request."""

    path: ClassVar[str] = "GetData"
    token_value: str = attrs.field(validator=attrs.validators.instance_of(str))
    data_request: DSDataRequest = attrs.field(
        validator=attrs.validators.instance_of(DSDataRequest)
    )
    properties: List[DSStringKVPair] = attrs.field(
        factory=list,
        converter=converters.convert_key_value_pairs,
        validator=kv_validator,
    )

    def add_property(self, key: str, value: Any) -> None:
        """Add a property to the request."""
        self.properties.append(DSStringKVPair(key, value))


@attrs.define()
class DSGetDataBundleRequest:
    """Object that contains multiple data requests."""

    path: ClassVar[str] = "GetDataBundle"
    token_value: str = attrs.field(validator=attrs.validators.instance_of(str))
    data_requests: List[DSDataRequest] = attrs.field(
        validator=attrs.validators.deep_iterable(
            attrs.validators.instance_of(DSDataRequest),
            attrs.validators.and_(
                attrs.validators.instance_of(list),
                attrs.validators.min_len(1),
            ),
        )
    )
    properties: List[DSStringKVPair] = attrs.field(
        factory=list,
        converter=converters.convert_key_value_pairs,
        validator=kv_validator,
    )

    @data_requests.validator
    def validate_requests(
        self,
        attribute: attrs.Attribute,  # noqa: ARG002
        value: List[DSDataRequest],
    ) -> None:
        """Validate that a bundle complies with DSWS bundle limits."""
        if len(value) > MAX_REQUESTS_PER_BUNDLE:
            msg = f"Bundle contains more than {MAX_REQUESTS_PER_BUNDLE} requests."
            raise InvalidRequestError(msg)
        total_items = sum(
            len(request.instrument.identifiers) * len(request.data_types)
            for request in value
        )
        if total_items > MAX_ITEMS_PER_BUNDLE:
            msg = f"Bundle contains more than {MAX_ITEMS_PER_BUNDLE} items."
            raise InvalidRequestError(msg)

    def add_property(self, key: str, value: Any) -> None:
        """Add a property to the request."""
        self.properties.append(DSStringKVPair(key, value))


@attrs.define()
class DSGetTokenRequest:
    """Object that defines a token request."""

    path: ClassVar[str] = "GetToken"
    user_name: str = attrs.field(validator=attrs.validators.instance_of(str))
    password: str = attrs.field(validator=attrs.validators.instance_of(str))
    properties: List[DSStringKVPair] = attrs.field(
        factory=list,
        converter=converters.convert_key_value_pairs,
        validator=kv_validator,
    )

    def add_property(self, key: str, value: Any) -> None:
        """Add a property to the request."""
        self.properties.append(DSStringKVPair(key, value))


def to_ds_dict(obj: attrs.AttrsInstance) -> Dict[str, Any]:
    """Convert an attrs class to a dictionary."""
    obj_dict: Dict[str, Any] = {}
    for field in attrs.fields(type(obj)):
        value = getattr(obj, field.name)
        if attrs.has(type(value)):
            obj_dict[utils.snake_to_pascal_case(field.name)] = to_ds_dict(value)
        elif isinstance(value, list):
            if value:
                value_list = [
                    to_ds_dict(item) if attrs.has(type(item)) else item
                    for item in value
                ]
            else:
                value_list = None
            obj_dict[utils.snake_to_pascal_case(field.name)] = value_list
        else:
            if isinstance(value, enum.Enum):
                value = value.value
            obj_dict[utils.snake_to_pascal_case(field.name)] = value
    return obj_dict


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
                attrs.evolve(instrument, value=",".join(batch_identifiers)),
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
            attrs.evolve(bundle_instrument, value=",".join(bundle_request_identifiers))
        )
    return tuple(request_bundles)
