#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import (
    CONF_ENTITIES,
    CONF_STATES_ON,
    DOMAIN,
    FEATURE_BINARY_SENSOR_AGGREGATION,
    FEATURE_PRESENCE
)
from .utils.matjak_area import MatjakArea
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER_DOMAIN
from homeassistant.components.person import DOMAIN as PERSON_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_START, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change
from logging import getLogger
from typing import Any, Callable, Dict, List


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


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


    return True
