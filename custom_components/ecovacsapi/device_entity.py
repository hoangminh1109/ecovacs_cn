"""Classes for representing entities beloging to an Imou channel."""
import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union

from .api import EcovacsAPIClient
from .const import (
    BUTTONS,
    SENSORS,
    CONTROLS,
    CLEAN_STATES,
)
from .exceptions import APIError, InvalidResponse, NotConnected

_LOGGER: logging.Logger = logging.getLogger(__package__)

class EcovacsEntity(ABC):
    """A representation of a sensor within an Imou Channel."""

    def __init__(
        self,
        api_client: EcovacsAPIClient,
        device_name: str,
        sensor_type: str,
        sensor_param: str,
        sensor_description: str,
    ) -> None:
        """Initialize common parameters."""
        self.api_client = api_client
        self._device_name = device_name
        self._sensor_param = sensor_param
        self._sensor_type = sensor_type
        self._description = sensor_description
        self._enabled = True
        self._updated = False
        self._device_instance = None
        self._attributes: Dict[str, str] = {}

    def get_device_name(self) -> str:
        """Get device name."""
        return self._device_name

    def get_type(self) -> str:
        """Get type."""
        return self._sensor_type

    def get_name(self) -> str:
        """Get name."""
        return f"{self._sensor_type} {self._sensor_param}"

    def get_description(self) -> str:
        """Get description."""
        return self._description

    def set_enabled(self, value: bool) -> None:
        """Set enable."""
        self._enabled = value

    def is_enabled(self) -> bool:
        """If enabled."""
        return self._enabled

    def is_updated(self) -> bool:
        """If has been updated at least once."""
        return self._updated

    def set_device(self, device_instance) -> None:
        """Set the device instance this entity is belonging to."""
        self._device_instance = device_instance

    def get_attributes(self) -> dict:
        """Entity attributes."""
        return self._attributes

    async def _async_is_ready(self) -> bool:
        """Check if the sensor is fully ready."""
        # check if the sensor is enabled
        if not self._enabled:
            return False
        # wake up the device if a dormant device and sleeping
        if self._device_instance is not None:
            awake = await self._device_instance.async_wakeup()
            if awake:
                return True
            return False
        return True

    @abstractmethod
    async def async_update(self, **kwargs):
        """Update the entity."""


class EcovacsSensor(EcovacsEntity):
    """A representation of a sensor within an IMOU Device."""

    def __init__(
        self,
        api_client: EcovacsAPIClient,
        device_name: str,
        sensor_type: str,
        sensor_param: str,
    ) -> None:
        """
        Initialize the instance.

        Parameters:
            api_client: an instance ofthe API client
            device_id: the device id
            device_name: the device name
            sensor_type: the sensor type from const SENSORS
        """
        super().__init__(api_client, device_name, sensor_type, sensor_param, f"{SENSORS[sensor_type]} {sensor_param}")
        # keep track of the status of the sensor
        self._state = None

    async def async_update(self, **kwargs):
        """Update the entity."""
        if not await self._async_is_ready():
            return

        # status sensor
        if self._sensor_type == "cleanState":
            # get the device and channel status
            clean_state_data = await self.api_client.async_api_getCleanState(self._device_name)
            if "ret" not in clean_state_data:
                raise InvalidResponse(f"state not found in {clean_state_data}")
            if clean_state_data["ret"] == "ok":
                self._state = CLEAN_STATES.get(clean_state_data["st"], "unknown")

        # status sensor
        if self._sensor_type == "chargeState":
            # get the device and channel status
            charge_state_data = await self.api_client.async_api_getChargeState(self._device_name)
            if "ret" not in charge_state_data:
                raise InvalidResponse(f"state not found in {charge_state_data}")
            if charge_state_data["ret"] == "ok":
                self._state = charge_state_data["type"]


        _LOGGER.debug(
            "[%s] updating %s, value is %s",
            self.get_name(),
            self.get_description(),
            self._state,
        )
        if not self._updated:
            self._updated = True

    def get_state(self) -> Optional[str]:
        """Return the state."""
        return self._state

class EcovacsButton(EcovacsEntity):
    """A representation of a button within an IMOU Device."""

    def __init__(
        self,
        api_client: EcovacsAPIClient,
        device_name: str,
        sensor_type: str,
        sensor_param: str,
    ) -> None:
        """
        Initialize the instance.

        Parameters:
            api_client: an instance ofthe API client
            device_name: the device name
            sensor_type: the sensor type from const BUTTON
        """
        super().__init__(api_client, device_name, sensor_type, sensor_param, f"{BUTTONS[sensor_type]} {sensor_param}")

    async def async_press(self) -> None:
        """Press action."""
        if not await self._async_is_ready():
            return

        if self._sensor_type == "startClean":
            # start clean
            await self.api_client.async_api_setCleaning(self._device_name, "start")

        if self._sensor_type == "stopClean":
            # stop clean
            await self.api_client.async_api_setCleaning(self._device_name, "stop")

        if self._sensor_type == "pauseClean":
            # pause clean
            await self.api_client.async_api_setCleaning(self._device_name, "pause")

        if self._sensor_type == "resumeClean":
            # resume clean
            await self.api_client.async_api_setCleaning(self._device_name, "resume")

        if self._sensor_type == "returnDock":
            # return to dock
            await self.api_client.async_api_setCharging(self._device_name, "return_dock")

        if self._sensor_type == "cancelReturn":
            # cancel returning to dock
            await self.api_client.async_api_setCharging(self._device_name, "cancel_return")

        _LOGGER.debug(
            "[%s] pressed button %s",
            self.get_name(),
            self.get_description(),
        )
        if not self._updated:
            self._updated = True

    async def async_update(self, **kwargs):
        """Update the entity."""
        return

## EcovacsControl is mediaplayer-like with Start/Pause/Stop control for cleaning. It is not fully implemented yet
class EcovacsControl(EcovacsEntity):
    """A representation of a button within an IMOU Device."""

    def __init__(
        self,
        api_client: EcovacsAPIClient,
        device_name: str,
        sensor_type: str,
        sensor_param: str,
    ) -> None:
        """
        Initialize the instance.

        Parameters:
            api_client: an instance ofthe API client
            device_name: the device name
            sensor_type: the sensor type from const BUTTON
        """
        super().__init__(api_client, device_name, sensor_type, sensor_param, f"{CONTROLS[sensor_type]} {sensor_param}")
        # keep track of the status of the control
        self._state = None

    def get_state(self) -> Optional[str]:
        """Return the state."""
        return self._state

    async def async_start(self) -> None:
        """Press start/resume action."""
        if not await self._async_is_ready():
            return

        if self._state == "idle":
            # start clean
            await self.api_client.async_api_setCleaning(self._device_name, "start")
            self._state = "clean"
            _LOGGER.debug(
                "[%s] controlled %s %s",
                self.get_name(),
                self.get_description(),
                "start",
            )

        if self._state == "paused":
            # start clean
            await self.api_client.async_api_setCleaning(self._device_name, "resume")
            self._state = "clean"
            _LOGGER.debug(
                "[%s] controlled %s %s",
                self.get_name(),
                self.get_description(),
                "resume",
            )
        if not self._updated:
            self._updated = True

    async def async_pause(self) -> None:
        """Press pause action."""
        if not await self._async_is_ready():
            return

        # pause clean
        await self.api_client.async_api_setCleaning(self._device_name, "pause")
        self._state = "pause"

        _LOGGER.debug(
            "[%s] controlled %s %s",
            self.get_name(),
            self.get_description(),
            "pause",
        )
        if not self._updated:
            self._updated = True

    async def async_stop(self) -> None:
        """Press stop action."""
        if not await self._async_is_ready():
            return

        # pause clean
        await self.api_client.async_api_setCleaning(self._device_name, "stop")
        self._state = "stop"

        _LOGGER.debug(
            "[%s] controlled %s %s",
            self.get_name(),
            self.get_description(),
            "stop",
        )
        if not self._updated:
            self._updated = True

    async def async_update(self, **kwargs):
        """Update the entity."""
        return



