#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .base_config import BaseConfig
from dataclasses import dataclass, field
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.media_player import MediaPlayerDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from typing import Any, ClassVar
import voluptuous as vol


#-----------------------------------------------------------#
#       PresenceConfig
#-----------------------------------------------------------#

@dataclass
class PresenceConfig(BaseConfig):
    #--------------------------------------------#
    #       Constants
    #--------------------------------------------#

    DEVICE_CLASSES: ClassVar[list[str]] = [BinarySensorDeviceClass.MOTION.value, BinarySensorDeviceClass.OCCUPANCY.value, BinarySensorDeviceClass.PRESENCE.value]
    DOMAINS: ClassVar[list[str]] = ["binary_sensor", "media_player", "person"]


    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    clear_timeout: int = 0
    enable: bool = False
    device_class: str = DEVICE_CLASSES[1]
    device_classes: dict[str, list[str]] = field(default_factory=lambda: {"binary_sensor": [BinarySensorDeviceClass.MOTION.value, BinarySensorDeviceClass.OCCUPANCY.value, BinarySensorDeviceClass.PRESENCE.value]})
    domains: list[str] = field(default_factory=lambda: [PresenceConfig.DOMAINS[0]])
    states_on: list[str] = field(default_factory=lambda: ["on", "playing", "home", "open"])


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __post_init__(self) -> None:
        """ Triggered after the class has initially been initialized. """
        if isinstance(self.device_classes, list):
            self.device_classes = self._device_classes_to_dict(self.device_classes)

        if isinstance(self.states_on, str):
            self.states_on = cv.ensure_list_csv(self.states_on)


    #--------------------------------------------#
    #       Overridable Methods
    #--------------------------------------------#

    def get_schema(self, hass: HomeAssistant, **kwargs: Any) -> vol.Schema:
        binary_sensor_device_classes = [f"binary_sensor: {item.value}" for item in BinarySensorDeviceClass]
        media_player_device_classes = [f"media_player: {item.value}" for item in MediaPlayerDeviceClass]

        all_device_classes = [item for item in binary_sensor_device_classes + media_player_device_classes if item not in self.device_classes]
        selected_device_classes = self._device_classes_to_list(self.device_classes)

        device_classes = selected_device_classes + [item for item in all_device_classes if item not in selected_device_classes]
        domains = self.domains + [item for item in self.DOMAINS if item not in self.domains]

        return vol.Schema({
            vol.Required("enable", default=self.enable): bool,
            vol.Required("domains", default=self.domains): cv.multi_select(domains),
            vol.Required("device_classes", default=selected_device_classes): cv.multi_select(device_classes),
            vol.Required("states_on", default=", ".join(self.states_on)): str,
            vol.Required("clear_timeout", default=self.clear_timeout): vol.All(int, vol.Range(min=0)),
            vol.Required("device_class", default=self.device_class): vol.In(self.DEVICE_CLASSES)
        })


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _device_classes_to_dict(self, device_classes: list[str]) -> dict[str, list[str]]:
        """ Processes the device classss input to a dictionary. """
        result: dict[str, list[str]] = {}

        for item in device_classes:
            domain, device_class = item.replace(" ", "").split(":")

            if domain not in result:
                result[domain] = []

            result[domain].append(device_class)

        return result

    def _device_classes_to_list(self, device_classes: dict[str, list[str]]) -> list[str]:
        """ Processes the device classes dictionary to a user input list. """
        result: list[str] = []

        for domain, device_classes in device_classes.items():
            for device_class in device_classes:
                result.append(f"{domain}: {device_class}")

        return result

