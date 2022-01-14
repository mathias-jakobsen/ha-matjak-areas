#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .platforms.sensor.aggregation import AggregationSensor
from .utils.registry import get_registry
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from logging import getLogger, Logger
from typing import Callable


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER: Logger = getLogger(__name__)


#-----------------------------------------------------------#
#       Entry Setup
#-----------------------------------------------------------#

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable) -> bool:
    """ Called when a config entry is being setup.  """
    registry = get_registry(config_entry)

    if registry.config.sensor_aggregation.enable:
        entities = [AggregationSensor(registry, device_class) for device_class in registry.config.sensor_aggregation.device_classes]
        async_add_entities(entities)

    return True
