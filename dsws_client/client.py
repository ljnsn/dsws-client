"""The DSWS client."""

import concurrent.futures
import itertools
import logging
import sys
from typing import Any, Dict, Iterator, List, Optional, Type, TypeVar, Union

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
    """
    Client for the DSWS web service.

    It can be shared between threads.

    Args:
        username: The DSWS username.
        password: The DSWS password.
        host (default: "https://product.datastream.com"): The DSWS host URL.
        timeout (default: 180): The timeout configuration to use when sending
            requests.
        proxy (optional): A proxy URL where all the traffic should be routed.
        ssl_cert (optional): SSL certificates (a.k.a CA bundle) used to
            verify the identity of requested hosts.
        app_id (default: dsws-client-VERSION): The app ID to use in the
            request.
        data_source (optional): The data source to use in the request.
        max_concurrency (default: 1): The maximum number of concurrent
            requests to make.
        debug (default: False): If True, print the request and response
            data to stdout.
    """

    def __init__(self, username: str, password: str, **kwargs: Any) -> None:
        config = DSWSConfig(**kwargs)
        self._username = username
        self._password = password
        self._session = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            proxies=config.proxies,  # type: ignore[arg-type]
            verify=config.ssl_cert or True,
            headers={"Content-Type": "application/json"},
        )
        self._max_concurrency = config.max_concurrency
        self._app_id = config.app_id
        self._data_source = config.data_source
        self._debug = config.debug
        self._token: Optional[Token] = None

    @property
    def token(self) -> str:
        """Get a token."""
        if self._token is None or self._token.is_expired:
            self._token = self.fetch_token()
        return self._token.token_value

    def fetch_snapshot_data(
        self,
        identifiers: List[str],
        fields: List[str],
        start: Optional[DateType] = None,
        tag: Optional[str] = None,
    ) -> ParsedResponse:
        """Fetch snapshot data."""
        request_bundles = self.construct_request_bundles(
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
        responses = self.fetch_all(request_bundles)
        data_responses = itertools.chain.from_iterable(
            response.data_responses for response in responses
        )
        return responses_to_records(data_responses)

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
        request_bundles = self.construct_request_bundles(
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
        responses = self.fetch_all(request_bundles)
        data_responses = itertools.chain.from_iterable(
            response.data_responses for response in responses
        )
        return responses_to_records(data_responses)

    def fetch_one(
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
        logger.debug("fetching one")
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

    def fetch_bundle(
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
        logger.debug("fetching bundle")
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

    def fetch_all(
        self,
        request_bundles: List[List[DSDataRequest]],
    ) -> Iterator[DSGetDataBundleResponse]:
        """Fetch as many bundles as needed to get all items."""
        if self._max_concurrency > 1:
            yield from self._fetch_all_threaded(request_bundles)
        else:
            for bundle in request_bundles:
                yield self.fetch_bundle(bundle)

    def _fetch_all_threaded(
        self,
        request_bundles: List[List[DSDataRequest]],
    ) -> Iterator[DSGetDataBundleResponse]:
        """Fetch as many bundles as needed to get all items (concurrently)."""
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._max_concurrency
        ) as executor:
            logger.debug("fetching bundles in parallel")
            futures = [
                executor.submit(self.fetch_bundle, bundle) for bundle in request_bundles
            ]
            for future in concurrent.futures.as_completed(futures):
                yield future.result()

    def fetch_token(self, **kwargs: object) -> Token:
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

    def construct_request_bundles(  # noqa: PLR0913
        self,
        identifiers: List[str],
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
    ) -> List[List[DSDataRequest]]:
        """Construct a list of data request bundles."""
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
        request_bundles = []
        for identifier_bundle in identifier_bundles:
            data_requests = []
            for instrument in identifier_bundle:
                data_requests.append(
                    DSDataRequest(instrument, data_types, date, tag=tag)
                )
            request_bundles.append(data_requests)
        return request_bundles

    def _execute_request(
        self,
        request: DSRequest,
        response_cls: Type[ResponseCls],
    ) -> ResponseCls:
        """Execute a request."""
        logger.debug("executing request")
        self._prep_request(request)
        request_data = msgspec.json.encode(request)
        if self._debug:
            sys.stdout.write(f"sending request: {request_data!s}")
        response = self._session.post(
            request.path,
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

    def _prep_request(self, request: DSRequest) -> None:
        """Prepare a request."""
        if self._app_id is not None:
            request.properties.append(DSStringKVPair("__AppId", self._app_id))
        if self._data_source is not None:
            request.properties.append(DSStringKVPair("Source", self._data_source))
