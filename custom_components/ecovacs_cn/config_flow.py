"""Xonfig flow for Ecovacs."""

import logging

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from .ecovacsapi.api import EcovacsAPIClient
from .ecovacsapi.device import EcovacsDiscoverService
from .ecovacsapi.exceptions import EcovacsException
import voluptuous as vol

from .const import (
    CONF_API_URL,
    CONF_DEVICE_NAME,
    CONF_API_KEY,
    CONF_DISCOVERED_DEVICE,
    DEFAULT_API_URL,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

class EcovacsFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Ecovacs_ptz."""

    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize."""
        self._api_url = None
        self._api_key = None
        self._api_client = None
        self._session = None
        self._discovered_devices = {}
        self._discover_service = None
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        return await self.async_step_login()

    # Step: login
    async def async_step_login(self, user_input=None):
        """Ask and validate app id and app secret."""
        self._errors = {}
        if user_input is not None:
            # create an Ecovacs discovery service
            self._session = async_create_clientsession(self.hass)
            self._api_client = EcovacsAPIClient(user_input[CONF_API_URL], user_input[CONF_API_KEY], self._session)
            self._discover_service = EcovacsDiscoverService(self._api_client)
            valid = False
            # check if the provided credentails are working
            try:
                await self._api_client.async_connect()
                valid = True
            except EcovacsException as exception:
                self._errors["base"] = exception.get_title()
                _LOGGER.error(exception.to_string())
            # valid credentials provided
            if valid:
                # store app id and secret for later steps
                self._api_url = user_input[CONF_API_URL]
                self._api_key = user_input[CONF_API_KEY]
                return await self.async_step_discover()

        # by default show up the form
        return self.async_show_form(
            step_id="login",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_URL, default=DEFAULT_API_URL): str,
                    vol.Required(CONF_API_KEY, default = ""): str,
                }
            ),
            errors=self._errors,
        )

    # Step: discover

    async def async_step_discover(self, user_input=None):
        """Discover devices and ask the user to select one."""
        self._errors = {}
        if user_input is not None:
            # get the device instance from the selected input
            device = self._discovered_devices[user_input[CONF_DISCOVERED_DEVICE]]
            if device is not None:
                # set the name
                name = (
                    f"{user_input[CONF_DEVICE_NAME]}"
                    if CONF_DEVICE_NAME in user_input
                    and user_input[CONF_DEVICE_NAME] != ""
                    else device.get_device_name()
                )
                # create the entry
                data = {
                    CONF_API_URL: self._api_url,
                    CONF_DEVICE_NAME: name,
                    CONF_API_KEY: self._api_key,
                }
                await self.async_set_unique_id(f"{device.get_device_name()}")
                return self.async_create_entry(title=name, data=data)

        # discover registered devices
        try:
            self._discovered_devices = await self._discover_service.async_discover_devices()
        except EcovacsException as exception:
            self._errors["base"] = exception.get_title()
            _LOGGER.error(exception.to_string())

        return self.async_show_form(
            step_id="discover",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DISCOVERED_DEVICE): vol.In(
                        self._discovered_devices.keys()
                    ),
                    vol.Optional(CONF_DEVICE_NAME): str,
                }
            ),
            errors=self._errors,
        )
