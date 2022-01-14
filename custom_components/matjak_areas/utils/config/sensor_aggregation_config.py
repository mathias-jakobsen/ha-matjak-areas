#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .base_config import BaseConfig
from dataclasses import dataclass, field
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from typing import Any, ClassVar
import voluptuous as vol


#-----------------------------------------------------------#
#       SensorAggregationConfig
#-----------------------------------------------------------#

@dataclass
class SensorAggregationConfig(BaseConfig):
    #--------------------------------------------#
    #       Constants
    #--------------------------------------------#

    DEVICE_CLASSES: ClassVar[list[str]] = [
        SensorDeviceClass.CURRENT,
        SensorDeviceClass.ENERGY,
        SensorDeviceClass.HUMIDITY,
        SensorDeviceClass.ILLUMINANCE,
        SensorDeviceClass.POWER,
        SensorDeviceClass.TEMPERATURE
    ]

    MODE_SUM_DEVICE_CLASSES: ClassVar[list[str]] = [
        SensorDeviceClass.CURRENT,
        SensorDeviceClass.ENERGY,
        SensorDeviceClass.POWER
    ]


    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    device_classes: list[str] = field(default_factory=list)
    enable: bool = False


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __post_init__(self) -> None:
        """ Triggered after the class has initially been initialized. """
        pass


    #--------------------------------------------#
    #       Overridable Methods
    #--------------------------------------------#

    def get_schema(self, hass: HomeAssistant, **kwargs: Any) -> vol.Schema:
        device_classes = self.device_classes + [device_class for device_class in self.DEVICE_CLASSES if device_class not in self.device_classes]

        return vol.Schema({
            vol.Required("enable", default=self.enable): bool,
            vol.Required("device_classes", default=self.device_classes): cv.multi_select(device_classes)
        })

