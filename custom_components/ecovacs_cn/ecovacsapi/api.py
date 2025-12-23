"""Low-level API for interacting with Ecovacs devices."""

import logging

import json
import re

from aiohttp import ClientSession

from .const import (
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    ENDPOINT_DEVICE_LIST,
    ENDPOINT_CONTROL,
    CMD_CLEAN,
    CMD_CHARGE,
    CMD_GETCLEANSTATE,
    CMD_GETCHARGESTATE,
    CLEAN_ACTIONS,
    CHARGE_ACTIONS,
    CLEAN_STATES
)
from .exceptions import (
    APIError,
    ConnectionFailed,
    EcovacsException,
    InvalidResponse,
    NotConnected,
    CommandError
)

_LOGGER = logging.getLogger(__package__)


class EcovacsAPIClient:
    """Interact with Ecovacs API."""

    def __init__(self, base_url: str, api_key: str, session: ClientSession) -> None:
        """
        Initialize the instance.

        Parameters:
            api_key: api key from https://open.ecovacs.cn
            session: aiohttp client session
        """
        self._api_key = api_key
        self._session = session

        self._base_url = base_url
        self._timeout = DEFAULT_TIMEOUT
        self._log_http_requests_enabled = False
        self._redact_log_message_enabled = True

        self._connected = False
        self._retries = 1
        _LOGGER.debug("Initialized. Endpoint URL: %s", self._base_url)

    def _redact_log_message(self, data: str) -> str:
        """Redact log messages to remove sensitive information."""
        if not self._redact_log_message_enabled:
            return data
        for keyword in (
            "ak",
            "nickName",
            "cmd",
            "act",
        ):
            for tick in ('"', "'"):
                data = re.sub(
                    f"{tick}{keyword}{tick}:\\s*{tick}[^{tick}]+{tick}",
                    f"{tick}{keyword}{tick}: {tick}XXXXXXXXX{tick}",
                    data,
                )
        return data

    def get_base_url(self) -> str:
        """Get base url for the API."""
        return self._base_url

    def set_base_url(self, value: str) -> None:
        """Set a custom base url for the API."""
        self._base_url = value
        _LOGGER.debug("Set endpoint URL to %s", self._base_url)

    def get_timeout(self) -> int:
        """Get timeout for the API."""
        return self._timeout

    def set_timeout(self, value: int) -> None:
        """Set a custom timeout."""
        self._timeout = value
        _LOGGER.debug("Set timeout to %s", self._base_url)

    def set_session(self, value: ClientSession) -> None:
        """Set an aiohttp client session."""
        self._session = value

    def get_session(self) -> ClientSession:
        """Return the aiohttp client session."""
        return self._session

    def set_log_http_requests(self, value: bool) -> None:
        """Set to true if you want in debug logs also HTTP requests and responses."""
        self._log_http_requests_enabled = value

    async def async_connect(self) -> bool:
        """Authenticate against the API and retrieve an access token."""
        # check if we already have an access token and if so assume already authenticated
        if self.is_connected():
            return True

        # Ecovacs server doesn't require an access token

        self._connected = True
        return True

    async def async_disconnect(self) -> bool:
        """Disconnect from the API."""
        self._access_token = None
        self._access_token_expire_time = None
        self._connected = False
        _LOGGER.debug("Disconnected")
        return True

    async def async_reconnect(self) -> bool:
        """Reconnect to the API."""
        await self.async_disconnect()
        return await self.async_connect()

    def is_connected(self) -> bool:
        """Return true if already connected."""
        return self._connected

    async def _async_call_api(self, api: str, payload: dict, method: str = "post") -> dict:  # noqa: C901
        """Submit request to the HTTP API endpoint."""

        # connect if not connected
        while not self.is_connected():
            _LOGGER.debug("Connection attempt %d/%d", self._retries, MAX_RETRIES)
            # if noo many attempts, give up
            if self._retries >= MAX_RETRIES:
                _LOGGER.error("Too many unsuccesful connection attempts")
                break
            try:
                await self.async_connect()
            except EcovacsException as exception:
                _LOGGER.error(exception.to_string())
            self._retries = self._retries + 1
        if not self.is_connected():
            raise NotConnected()

        # prepare the API request
        url = f"{self._base_url}/{api}"

        params = {k: str(v) for k, v in payload.items()}
        params.update({"ak": self._api_key})

        if self._log_http_requests_enabled:
            _LOGGER.debug("[HTTP_REQUEST] %s: %s", url, self._redact_log_message(str(params)))

        # send the request to the API endpoint
        try:
            if method == 'post':
                response = await self._session.request("POST", url, json=params, timeout=self._timeout)
            else:
                response = await self._session.request("GET", url, params=params, timeout=self._timeout)
        except Exception as exception:
            raise ConnectionFailed(f"{exception}") from exception

        # parse the response and look for errors
        response_status = response.status
        if self._log_http_requests_enabled:
            _LOGGER.debug(
                "[HTTP_RESPONSE] %s: %s",
                response_status,
                self._redact_log_message(str(await response.text())),
            )
        if response_status != 200:
            raise APIError(f"status code {response.status}")
        try:
            response_body = json.loads(await response.text())
        except Exception as exception:
            raise InvalidResponse(f"unable to parse response text {await response.text()}") from exception
        if ( "msg" not in response_body or "code" not in response_body ):
            raise InvalidResponse(f"cannot find msg, code in {response_body}")
        result_msg = response_body["msg"]
        result_code = str(response_body["code"])
        if result_code != "0":
            error_message = result_code + ": " + result_msg
            raise APIError(error_message)

        # return the payload of the reponse
        response_data = response_body["data"] if "data" in response_body else {}
        return response_data

    async def async_api_deviceList(self) -> dict:  # pylint: disable=invalid-name
        """Get connected robots ."""
        # define the api endpoint
        api = ENDPOINT_DEVICE_LIST
        # prepare the payload
        payload = {}
        # call the api
        return await self._async_call_api(api, payload, method="get")

    def check_ctl_response(self, response: dict) -> dict:
        result_msg = response["msg"]
        result_code = str(response["code"])
        if result_code != "0":
            error_message = result_code + ": " + result_msg
            raise CommandError(error_message)

        result_data = response["data"] if "data" in response else {}
        result_ctl = result_data["ctl"] if "ctl" in result_data else {}
        result_ctl_data = result_ctl["data"] if "data" in result_ctl else {}
        ctl_ret = result_ctl_data["ret"] if "ret" in result_ctl_data else ""

        if ctl_ret != "ok":
            error_message = ctl_ret
            raise CommandError(error_message)

        return  result_ctl_data

    async def async_api_setCleaning(self, nickName: str, action: str) -> dict:  # pylint: disable=invalid-name
        """Control cleaning \
            action: start/pause/resume/stop. """
        # define the api endpoint
        api = ENDPOINT_CONTROL
        # prepare the payload
        act = CLEAN_ACTIONS.get(action, CLEAN_ACTIONS["stop"])
        payload = {
            "nickName": nickName,
            "cmd": CMD_CLEAN,
            "act": act,
        }
        _LOGGER.debug(
            "Cleaning act %s - %s", action, act )
        # call the api
        response =  await self._async_call_api(api, payload)
        return self.check_ctl_response(response)

    async def async_api_setCharging(self, nickName: str, action: str) -> dict:  # pylint: disable=invalid-name
        """Control charging \
            action: return_dock / cancel_return. """
        # define the api endpoint
        api = "robot/ctl"
        # prepare the payload
        payload = {
            "nickName": nickName,
            "cmd": CMD_CHARGE,
            "act": CHARGE_ACTIONS.get(action, CHARGE_ACTIONS["cancel_return"]),
        }
        # call the api
        response =  await self._async_call_api(api, payload)
        return self.check_ctl_response(response)

    async def async_api_getCleanState(self, nickName: str) -> dict:  # pylint: disable=invalid-name
        """Get cleaning state \
            return: s-cleaning, p-paused, h-idle. """
        # define the api endpoint
        api = ENDPOINT_CONTROL
        # prepare the payload
        payload = {
            "nickName": nickName,
            "cmd": CMD_GETCLEANSTATE,
            "act": "",
        }
        # call the api
        response =  await self._async_call_api(api, payload)
        return self.check_ctl_response(response)

    def api_translateCleanState(self, state_data: dict) -> str:
        state = state_data["st"]
        return CLEAN_STATES.get(state, "Unknown")

    async def async_api_getChargeState(self, nickName: str) -> dict:  # pylint: disable=invalid-name
        """Get charging state \
            return: Idle, SlotCharging, WireCharging. """
        # define the api endpoint
        api = ENDPOINT_CONTROL
        # prepare the payload
        payload = {
            "nickName": nickName,
            "cmd": CMD_GETCHARGESTATE,
            "act": "",
        }
        # call the api
        response =  await self._async_call_api(api, payload)
        return self.check_ctl_response(response)

    def api_translateChargeState(self, state_data: dict) -> str:
        state = state_data["type"]
        return state
