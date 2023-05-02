import datetime as dt
import functools
from typing import Any, List, Optional

import attrs

from dsws_client import converters, utils
from dsws_client.value_objects import DSStringKVPair, DSSymbolResponseValueType


@attrs.define(field_transformer=utils.ds_names)
class DSSymbolResponseValue:
    """A symbol response value."""

    symbol: str
    currency: Optional[str]
    type: DSSymbolResponseValueType = attrs.field(converter=DSSymbolResponseValueType)
    value: Any


@attrs.define(field_transformer=utils.ds_names)
class DSDataTypeResponseValue:
    """A data type response value."""

    data_type: str
    symbol_values: List[DSSymbolResponseValue] = attrs.field(
        converter=functools.partial(
            converters.convert_model_list,
            (DSSymbolResponseValue,),
        )
    )


@attrs.define(field_transformer=utils.ds_names)
class DSDataResponse:
    """Object that contains a data response."""

    data_type_values: List[DSDataTypeResponseValue] = attrs.field(
        converter=functools.partial(
            converters.convert_model_list,
            (DSDataTypeResponseValue,),
        )
    )
    dates: Optional[List[dt.datetime]] = attrs.field(
        converter=attrs.converters.optional(converters.convert_date_list)
    )
    data_type_names: Optional[List[DSStringKVPair]] = attrs.field(
        converter=attrs.converters.optional(converters.convert_key_value_pairs)
    )
    symbol_names: Optional[List[DSStringKVPair]] = attrs.field(
        converter=attrs.converters.optional(converters.convert_key_value_pairs)
    )
    additional_responses: Optional[List[DSStringKVPair]] = attrs.field(
        converter=attrs.converters.optional(converters.convert_key_value_pairs)
    )
    tag: Optional[str]


@attrs.define(field_transformer=utils.ds_names)
class DSGetDataResponse:
    """Object that containes a get data response."""

    data_response: DSDataResponse = attrs.field(
        converter=functools.partial(converters.convert_model, (DSDataResponse,))
    )
    properties: Optional[List[DSStringKVPair]] = attrs.field(
        converter=attrs.converters.optional(converters.convert_key_value_pairs)
    )


@attrs.define(field_transformer=utils.ds_names)
class DSGetDataBundleResponse:
    """Object that contains a get data bundle response."""

    data_responses: List[DSDataResponse] = attrs.field(
        converter=functools.partial(
            converters.convert_model_list,
            (DSDataResponse,),
        )
    )
    properties: Optional[List[DSStringKVPair]] = attrs.field(
        converter=attrs.converters.optional(converters.convert_key_value_pairs)
    )


@attrs.define(field_transformer=utils.ds_names)
class DSGetTokenResponse:
    """Object that contains a token response."""

    token_value: str
    token_expiry: dt.datetime = attrs.field(converter=converters.convert_date)
    properties: Optional[List[DSStringKVPair]] = attrs.field(
        converter=attrs.converters.optional(converters.convert_key_value_pairs)
    )

    @property
    def is_expired(self) -> bool:
        """Return True if the token is expired."""
        return (self.token_expiry + dt.timedelta(minutes=1)) < dt.datetime.now(
            tz=dt.timezone.utc
        )
