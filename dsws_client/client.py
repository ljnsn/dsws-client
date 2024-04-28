"""The DSWS client."""

import itertools
import logging
import sys
import urllib.parse
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import httpx
import msgspec

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
from dsws_client.value_objects import DateType, DSStringKVPair, Token

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
        self._proxies = (
            None
            if config.proxy is None
            else {"http": config.proxy, "https": config.proxy}
        )
        self._timeout = config.timeout
        self._ssl_cert = config.ssl_cert
        self._token: Optional[Token] = None
        self._app_id = config.app_id
        self._data_source = config.data_source
        self._debug = config.debug
        self._session = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            proxies=self._proxies,
            verify=self._ssl_cert or True,
            headers={"Content-Type": "application/json"},
        )

    @property
    def token(self) -> str:
        """Get a token."""
        if self._token is None or self._token.is_expired:
            self._token = self.get_token()
        return self._token.token_value

    def fetch_snapshot_data(
        self,
        identifiers: List[str],
        fields: List[str],
        start: Optional[DateType] = None,
        tag: Optional[str] = None,
    ) -> ParsedResponse:
        """Fetch snapshot data."""
        responses = self.fetch_all(
            identifiers=identifiers,
            fields=fields,
            start=start,
            end=None,
            frequency=None,
            kind=0,
            tag=tag,
            return_symbol_names=True,
            return_field_names=True,
        )
        data_responses = itertools.chain.from_iterable(
            response.data_responses for response in responses
        )
        return responses_to_records(list(data_responses))

    def fetch_timeseries_data(  # noqa: PLR0913
        self,
        identifiers: List[str],
        fields: List[str],
        start: Optional[DateType] = None,
        end: Optional[DateType] = None,
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
        data_responses = itertools.chain.from_iterable(
            response.data_responses for response in responses
        )
        return responses_to_records(list(data_responses))

    def fetch_one(  # noqa: PLR0913
        self,
        identifiers: Union[str, List[str]],
        fields: List[str],
        start: Optional[DateType],
        end: Optional[DateType] = None,
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
        start: Optional[DateType],
        end: Optional[DateType] = None,
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
                return_name=return_field_names,
                properties=field_props,
            )
            for field in fields
        ]
        date = DSDate.construct(start, end, frequency, kind)
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

    def get_token(self, **kwargs: object) -> Token:
        """
        Fetch a new token.

        Args:
            **kwargs: Additional properties to set on the request.

        Returns:
            A token.
        """
        token_response = self._execute_request(
            DSGetTokenRequest(
                self._username,
                self._password,
                properties=[
                    DSStringKVPair(key, value) for key, value in kwargs.items()
                ],
            ),
            DSGetTokenResponse,
        )
        return token_response.to_token()

    def get_data(
        self,
        data_request: DSDataRequest,
        **kwargs: object,
    ) -> DSGetDataResponse:
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
                properties=[
                    DSStringKVPair(key, value) for key, value in kwargs.items()
                ],
            ),
            DSGetDataResponse,
        )

    def get_data_bundle(
        self,
        data_requests: List[DSDataRequest],
        **kwargs: object,
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
                properties=[
                    DSStringKVPair(key, value) for key, value in kwargs.items()
                ],
            ),
            DSGetDataBundleResponse,
        )

    def construct_request(  # noqa: PLR0913
        self,
        identifiers: Union[str, List[str]],
        fields: List[str],
        start: Optional[DateType],
        end: Optional[DateType],
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
                return_name=return_field_names,
                properties=field_props,
            )
            for field in fields
        ]
        date = DSDate.construct(start, end, frequency, kind)
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
        request_data = msgspec.json.encode(request)
        if self._debug:
            sys.stdout.write(f"sending request: {request_data!s}")
        response = self._session.post(
            request_url,
            content=request_data,
        )
        if not response.is_success:
            msg = f"request failed: {response.text}"
            raise RequestFailedError(msg, response.status_code)
        try:
            response_decoded = msgspec.json.decode(response.content, type=response_cls)
        except (msgspec.ValidationError, ValueError, TypeError) as exc:
            msg = f"invalid response: {response.text}"
            raise InvalidResponseError(msg) from exc
        if self._debug:
            sys.stdout.write(f"received response: {response_decoded!s}")
        return response_decoded
