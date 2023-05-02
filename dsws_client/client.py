import json
import logging
import sys
import urllib.parse
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import requests

from dsws_client.config import DSWSConfig
from dsws_client.ds_request import (
    DSDataRequest,
    DSDataType,
    DSDate,
    DSGetDataBundleRequest,
    DSGetDataRequest,
    DSGetTokenRequest,
    DSInstrument,
    DSRequest,
    bundle_identifiers,
    to_ds_dict,
)
from dsws_client.ds_response import (
    DSGetDataBundleResponse,
    DSGetDataResponse,
    DSGetTokenResponse,
)
from dsws_client.exceptions import (
    InvalidResponseError,
    RequestFailedError,
)
from dsws_client.parse import ParsedResponse, responses_to_records
from dsws_client.value_objects import DateType, DSStringKVPair

logger = logging.getLogger(__name__)

ResponseCls = TypeVar("ResponseCls")


class DSWSClient:
    """Client for the DSWS web service."""

    def __init__(self, username: str, password: str, **kwargs: Any) -> None:
        """
        Initialize the client.

        Args:
            username: DSWS username.
            password: DSWS password.
            **kwargs: Additional keyword arguments passed to the config object.
        """
        config = DSWSConfig(**kwargs)
        self._username = username
        self._password = password
        self._url = urllib.parse.urljoin(config.base_url, config.path)
        self._session = requests.Session()
        self._proxies = (
            None
            if config.proxy is None
            else {"http": config.proxy, "https": config.proxy}
        )
        self._timeout = config.timeout
        self._ssl_cert = config.ssl_cert
        self._token_response: Optional[DSGetTokenResponse] = None
        self._app_id = config.app_id
        self._data_source = config.data_source
        self._debug = config.debug

    @property
    def token(self) -> str:
        """Get a token."""
        if self._token_response is None or self._token_response.is_expired:
            self._token_response = self.get_token()
        return self._token_response.token_value

    def fetch_snapshot_data(
        self,
        identifiers: List[str],
        fields: List[str],
        start: DateType = "",
        tag: Optional[str] = None,
    ) -> ParsedResponse:
        """Fetch snapshot data."""
        responses = self.fetch_all(
            identifiers=identifiers,
            fields=fields,
            start=start,
            end="",
            frequency=None,
            kind=0,
            tag=tag,
            return_symbol_names=True,
            return_field_names=True,
        )
        data_responses = []
        for response in responses:
            data_responses.extend(response.data_responses)
        return responses_to_records(data_responses)

    def fetch_timeseries_data(  # noqa: PLR0913
        self,
        identifiers: List[str],
        fields: List[str],
        start: DateType = "",
        end: DateType = "",
        frequency: str = "D",
        tag: Optional[str] = None,
    ) -> ParsedResponse:
        """Fetch timeseries data."""
        responses = self.fetch_all(
            identifiers=identifiers,
            fields=fields,
            start=start,
            end=end,
            frequency=frequency,
            kind=1,
            tag=tag,
            return_symbol_names=True,
            return_field_names=True,
        )
        data_responses = []
        for response in responses:
            data_responses.extend(response.data_responses)
        return responses_to_records(data_responses)

    def fetch_one(  # noqa: PLR0913
        self,
        identifiers: Union[str, List[str]],
        fields: List[str],
        start: DateType,
        end: DateType = "",
        frequency: str = "D",
        kind: int = 1,
        tag: Optional[str] = None,
        *,
        return_symbol_names: bool = False,
        return_field_names: bool = False,
        instrument_props: Optional[Dict[str, str]] = None,
        field_props: Optional[Dict[str, str]] = None,
    ) -> DSGetDataResponse:
        """Fetch data from the DSWS web service."""
        request = self.construct_request(
            identifiers=identifiers,
            fields=fields,
            start=start,
            end=end,
            frequency=frequency,
            kind=kind,
            tag=tag,
            return_symbol_names=return_symbol_names,
            return_field_names=return_field_names,
            instrument_props=instrument_props,
            field_props=field_props,
        )
        return self.get_data(request)

    def fetch_all(  # noqa: PLR0913
        self,
        identifiers: List[str],
        fields: List[str],
        start: DateType,
        end: DateType = "",
        frequency: Optional[str] = "D",
        kind: int = 1,
        tag: Optional[str] = None,
        *,
        return_symbol_names: bool = False,
        return_field_names: bool = False,
        instrument_props: Optional[Dict[str, str]] = None,
        field_props: Optional[Dict[str, str]] = None,
    ) -> List[DSGetDataBundleResponse]:
        """Fetch as many bundles as needed to get all items."""
        instrument = DSInstrument.construct(
            identifiers,
            return_names=return_symbol_names,
            properties=instrument_props,
        )
        data_types = [
            DSDataType.construct(
                field,
                return_names=return_field_names,
                properties=field_props,
            )
            for field in fields
        ]
        date = DSDate(start, end, frequency, kind)
        identifier_bundles = bundle_identifiers(instrument, len(data_types))
        responses = []
        for identifier_bundle in identifier_bundles:
            data_requests = []
            for instrument in identifier_bundle:
                data_requests.append(
                    DSDataRequest(instrument, data_types, date, tag=tag)
                )
            responses.append(self.get_data_bundle(data_requests))
        return responses

    def get_token(self, **kwargs: Any) -> DSGetTokenResponse:
        """
        Fetch a new token.

        Args:
            **kwargs: Additional properties to set on the request.

        Returns:
            A token response.
        """
        return self._execute_request(
            DSGetTokenRequest(self._username, self._password, properties=kwargs),
            DSGetTokenResponse,
        )

    def get_data(self, data_request: DSDataRequest, **kwargs: Any) -> DSGetDataResponse:
        """
        Post a data request.

        Args:
            data_request: A data request.
            **kwargs: Additional properties to set on the request.

        Returns:
            A data response.
        """
        return self._execute_request(
            DSGetDataRequest(
                token_value=self.token,
                data_request=data_request,
                properties=kwargs,
            ),
            DSGetDataResponse,
        )

    def get_data_bundle(
        self,
        data_requests: List[DSDataRequest],
        **kwargs: Any,
    ) -> DSGetDataBundleResponse:
        """
        Post multiple data requests.

        Args:
            data_requests: A list of data requests.
            **kwargs: Additional properties to set on the request.

        Returns:
            A data bundle response.
        """
        return self._execute_request(
            DSGetDataBundleRequest(
                token_value=self.token,
                data_requests=data_requests,
                properties=kwargs,
            ),
            DSGetDataBundleResponse,
        )

    def construct_request(  # noqa: PLR0913
        self,
        identifiers: Union[str, List[str]],
        fields: List[str],
        start: DateType,
        end: DateType,
        frequency: Optional[str],
        kind: int,
        tag: Optional[str] = None,
        *,
        return_symbol_names: bool = False,
        return_field_names: bool = False,
        instrument_props: Optional[Dict[str, str]] = None,
        field_props: Optional[Dict[str, str]] = None,
    ) -> DSDataRequest:
        """Construct a data request."""
        instrument = DSInstrument.construct(
            identifiers,
            return_names=return_symbol_names,
            properties=instrument_props,
        )
        data_types = [
            DSDataType.construct(
                field,
                return_names=return_field_names,
                properties=field_props,
            )
            for field in fields
        ]
        date = DSDate(start, end, frequency, kind)
        return DSDataRequest(instrument, data_types, date, tag)

    def _execute_request(
        self,
        request: DSRequest,
        response_cls: Type[ResponseCls],
    ) -> ResponseCls:
        """Execute a request."""
        if self._app_id is not None:
            request.properties.append(DSStringKVPair("__AppId", self._app_id))
        if self._data_source is not None:
            request.properties.append(DSStringKVPair("Source", self._data_source))
        request_url = urllib.parse.urljoin(self._url, request.path)
        request_dict = to_ds_dict(request)
        if self._debug:
            sys.stdout.write(f"sending request: {request_dict!s}")
        response = self._session.post(
            request_url,
            json=request_dict,
            proxies=self._proxies,
            verify=self._ssl_cert,
            timeout=self._timeout,
        )
        if not response.ok:
            msg = f"request failed: {response.text}"
            raise RequestFailedError(msg, response.status_code)
        try:
            json_response = response.json()
        except json.JSONDecodeError as exc:
            msg = f"invalid response: {response.text}"
            raise InvalidResponseError(msg) from exc
        if self._debug:
            sys.stdout.write(f"received response: {json_response!s}")
        return response_cls(**json_response)
