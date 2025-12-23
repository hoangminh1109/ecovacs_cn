"""
Custom integration to integrate China domestic Ecovacs cleaning robot with Home Assistant.

For more details about this integration, please refer to
https://github.com/hoangminh1109/ecovacs_cn
"""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from .ecovacsapi.api import EcovacsAPIClient
from .ecovacsapi.device import EcovacsDevice
from .ecovacsapi.exceptions import EcovacsException

from .const import (
    CONF_API_URL,
    CONF_API_KEY,
    CONF_DEVICE_NAME,
    DEFAULT_API_URL,
    DOMAIN,
    OPTION_API_TIMEOUT,
    OPTION_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    PLATFORMS
)
from .coordinator import EcovacsDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
    session = async_get_clientsession(hass)

    # retrieve the configuration entry parameters
    _LOGGER.debug("Loading entry %s", entry.entry_id)
    device_name = entry.data.get(CONF_DEVICE_NAME)
    api_url = entry.data.get(CONF_API_URL)
    api_key = entry.data.get(CONF_API_KEY)
    _LOGGER.debug("Setting up device %s (%s)", device_name)

    # create an Ecovacs api client instance
    api_client = EcovacsAPIClient(api_url, api_key, session)
    timeout = entry.options.get(OPTION_API_TIMEOUT, None)
    if isinstance(timeout, str):
        timeout = None if timeout == "" else int(timeout)
    if timeout is not None:
        _LOGGER.debug("Setting API timeout to %d", timeout)
        api_client.set_timeout(timeout)

    # create an Ecovacs device instance
    device = EcovacsDevice(api_client, device_name)
    if device_name is not None:
        device.get_device_name()

    # initialize the device so to discover all the sensors
    try:
        await device.async_initialize()
    except EcovacsException as exception:
        _LOGGER.error(exception.to_string())
        raise EcovacsException() from exception
    # at this time, all sensors must be disabled (will be enabled individually by async_added_to_hass())
    for sensor_instance in device.get_all_sensors():
        sensor_instance.set_enabled(False)

    # create a coordinator
    coordinator = EcovacsDataUpdateCoordinator(
        hass, device, entry.options.get(OPTION_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )
    # fetch the data
    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    # store the coordinator so to be accessible by each platform
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # for each enabled platform, forward the configuration entry for its setup
    for platform in PLATFORMS:
        coordinator.platforms.append(platform)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.add_update_listener(async_reload_entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.debug("Unloading entry %s", entry.entry_id)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
