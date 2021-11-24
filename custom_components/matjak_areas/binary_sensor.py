#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import (
    CONF_DEVICE_CLASS,
    DOMAIN,
    FEATURE_BINARY_SENSOR_AGGREGATION,
    FEATURE_PRESENCE
)
from .utils.matjak_area import MatjakArea
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from typing import Any, Callable, Dict


#-----------------------------------------------------------#
#       Entry Setup
#-----------------------------------------------------------#

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable) -> bool:
    """ Called when a config entry is being setup.  """
    matjak_area = hass.data[DOMAIN][config_entry.entry_id]
    feature_aggregation_config = matjak_area.get_feature(FEATURE_BINARY_SENSOR_AGGREGATION)
    feature_presence_config = matjak_area.get_feature(FEATURE_PRESENCE)

    if feature_aggregation_config:
        pass # create binary sensor aggregations

    if feature_presence_config:
        async_add_entities([create_presence_sensor(hass, matjak_area, feature_presence_config)])

    return True


#-----------------------------------------------------------#
#       Sensor Setup
#-----------------------------------------------------------#

def create_presence_sensor(hass: HomeAssistant, matjak_area: MatjakArea, config: Dict[str, Any]) -> PresenceSensor:
    """ Handles the creation of the presence sensor. """
    return PresenceSensor(matjak_area, config)


#-----------------------------------------------------------#
#       Class: PresenceSensor
#-----------------------------------------------------------#

class PresenceSensor(BinarySensorEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, matjak_area: MatjakArea, config: Dict[str, Any]):
        self._config = config
        self._device_class = config.get(CONF_DEVICE_CLASS)
        self._matjak_area = matjak_area
        self._unique_id = f"{cv.slugify(matjak_area.name)}_presence_sensor"


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def device_class(self) -> str:
        return self._device_class

    @property
    def unique_id(self) -> str:
        return self._unique_id