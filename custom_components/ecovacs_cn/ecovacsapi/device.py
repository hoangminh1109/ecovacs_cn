"""High level API to discover and interacting with Imou camera channels and their sensors."""
import asyncio
import logging
import re
from typing import Any, Dict, List, Union
import pprint

from .api import EcovacsAPIClient
from .const import (
    BUTTONS,
    SENSORS,
    CONTROLS
)
from .device_entity import (
    EcovacsButton,
    EcovacsSensor,
    EcovacsControl,
    EcovacsEntity
)

from .exceptions import InvalidResponse, EcovacsException

_LOGGER: logging.Logger = logging.getLogger(__package__)

class EcovacsDevice:
    """A abstraction of an IMOU Camera Chanel."""

    def __init__(
        self,
        api_client: EcovacsAPIClient,
        device_name: str,
    ) -> None:
        """
        Initialize the instance.

        Parameters:
            api_client: an ImouAPIClient instance
            device_id: device id
            channel_id: channel_id
        """
        self._api_client = api_client

        self._clean_status = "unknown"
        self._charge_status = "unknown"
        self._device_name = device_name

        self._sensor_instances: Dict[str, list] = {
            "sensor": [],
            "button": [],
            "control": []
        }

        self._initialized = False
        self._enabled = True

    def get_api_client(self) -> EcovacsAPIClient:
        """Get api client."""
        return self._api_client

    def get_device_name(self) -> str:
        """Get device name."""
        return self._device_name

    def set_enabled(self, value: bool) -> None:
        """Set enable."""
        self._enabled = value

    def is_enabled(self) -> bool:
        """Is enabled."""
        return self._enabled

    def get_clean_status(self) -> str:
        """Get clean status."""
        return self._clean_status

    def get_charge_status(self) -> str:
        """Get charge status."""
        return self._charge_status

    def is_online(self) -> bool:
        """Get online status."""
        return self._clean_status != "unknown" or self._charge_status != "unknown"

    def get_all_sensors(self) -> List[EcovacsEntity]:
        """Get all the sensor instances."""
        sensors = []
        for (
            platform,  # pylint: disable=unused-variable
            sensor_instances_array,
        ) in self._sensor_instances.items():
            for sensor_instance in sensor_instances_array:
                sensors.append(sensor_instance)
        return sensors

    def get_sensors_by_platform(self, platform: str) -> List[EcovacsEntity]:
        """Get sensor instances associated to a given platform."""
        if platform not in self._sensor_instances:
            return []
        return self._sensor_instances[platform]


    def to_string(self) -> str:
        """Return the object as a string."""
        return f"{self._device_name}"

    def _add_sensor_instance(self, platform, instance):
        """Add a sensor instance."""
        instance.set_device(self)
        self._sensor_instances[platform].append(instance)

    async def async_initialize(self) -> None:
        """Initialize the instance by retrieving the channel details and associated collections."""
        try:
            # get the details for this device from the API
            device_list = await self._api_client.async_api_deviceList()
            if self._device_name not in device_list:
                raise InvalidResponse(f"Device {self._device_name} doesn't exist")

            # add status sensors
            self._add_sensor_instance(
                "sensor",
                EcovacsSensor(
                    self._api_client,
                    self._device_name,
                    "cleanState",
                    ""
                ),
            )
            self._add_sensor_instance(
                "sensor",
                EcovacsSensor(
                    self._api_client,
                    self._device_name,
                    "chargeState",
                    ""
                ),
            )

            # add buttons
            self._add_sensor_instance(
                "button",
                EcovacsButton(
                    self._api_client,
                    self._device_name,
                    "startClean",
                    ""
                ),
            )
            self._add_sensor_instance(
                "button",
                EcovacsButton(
                    self._api_client,
                    self._device_name,
                    "resumeClean",
                    ""
                ),
            )
            self._add_sensor_instance(
                "button",
                EcovacsButton(
                    self._api_client,
                    self._device_name,
                    "pauseClean",
                    ""
                ),
            )
            self._add_sensor_instance(
                "button",
                EcovacsButton(
                    self._api_client,
                    self._device_name,
                    "stopClean",
                    ""
                ),
            )
            self._add_sensor_instance(
                "button",
                EcovacsButton(
                    self._api_client,
                    self._device_name,
                    "returnDock",
                    ""
                ),
            )
            self._add_sensor_instance(
                "button",
                EcovacsButton(
                    self._api_client,
                    self._device_name,
                    "cancelReturn",
                    ""
                ),
            )

            # add control
            # self._add_sensor_instance(
            #     "control",
            #     EcovacsControl(
            #         self._api_client,
            #         self._device_name,
            #         "controlClean",
            #         ""
            #     ),
            # )

        except EcovacsException as exception:
            _LOGGER.error(f"Exception: {exception.to_string()}")

        # keep track that we have already asked for the device details
        self._initialized = True

    async def async_refresh_status(self) -> None:
        """Refresh status attribute."""
        clean_state = await self._api_client.async_api_getCleanState(self._device_name)
        self._clean_status = self._api_client.api_translateCleanState(clean_state)

        charge_state = await self._api_client.async_api_getChargeState(self._device_name)
        self._charge_status = self._api_client.api_translateChargeState(charge_state)

    async def async_wakeup(self) -> bool:
        """Wake up a dormant device."""
        return True

    async def async_get_data(self) -> bool:
        """Update device properties and its sensors."""
        if not self._enabled:
            return False
        if not self._initialized:
            # get the details of the device first
            await self.async_initialize()
        _LOGGER.debug("[%s] update requested", self.get_device_name())

        # check if the device is online
        await self.async_refresh_status()

        # update the status of all the sensors (if the device is online)
        if self.is_online():
            for (
                platform,  # pylint: disable=unused-variable
                sensor_instances_array,
            ) in self._sensor_instances.items():
                for sensor_instance in sensor_instances_array:
                    await sensor_instance.async_update()

        return True

class EcovacsDiscoverService:
    """Class for discovering Ecovacs devices."""

    def __init__(self, api_client: EcovacsAPIClient) -> None:
        """
        Initialize the instance.

        Parameters:
            api_client: an EcovacsAPIClient instance
        """
        self._api_client = api_client

    async def async_discover_devices(self) -> dict:
        """Discover registered devices and return a dict device name -> device object."""
        _LOGGER.debug("Starting discovery")

        try:
            devices_data = await self._api_client.async_api_deviceList()
            _LOGGER.debug("Discovered %d registered devices", len(devices_data))

            devices = {}
            for device_name in devices_data:
                device = EcovacsDevice(self._api_client, device_name)
                await device.async_initialize()
                devices[f"{device.get_device_name()}"] = device

                # _LOGGER.debug(f"{channel.get_name()}")

        except InvalidResponse as exception:
            _LOGGER.warning("Skipping unrecognized or unsupported device: ", exception.to_string(),)

        except EcovacsException as exception:
            _LOGGER.error(f"Exception: {exception.to_string()}")

        # return a dict with channel full name -> channel instance
        return devices

