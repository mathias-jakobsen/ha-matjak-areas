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
from homeassistant.const import CONF_ENTITY_ID, EVENT_HOMEASSISTANT_START, STATE_OFF, STATE_ON, STATE_UNAVAILABLE
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
#       PresenceSensor
#-----------------------------------------------------------#

class PresenceSensor(BinarySensorEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, matjak_area: MatjakArea, config: Dict[str, Any]):
        self._attributes  : Dict[str, Any] = {}
        self._config      : Dict[str, Any] = config
        self._entities    : List[str]      = config.get(CONF_ENTITIES)
        self._matjak_area : MatjakArea     = matjak_area
        self._name        : str            = f"{matjak_area.name} Presence"
        self._state       : List[str]      = None
        self._states_on   : List[str]      = config.get(CONF_STATES_ON)
        self._unique_id   : str            = cv.slugify(self._name)


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def device_class(self) -> str:
        """ Gets the device class of the sensor. """
        for entity_id in self._entities:
            domain = entity_id.split(".")[0]

            if domain not in [DEVICE_TRACKER_DOMAIN, PERSON_DOMAIN]:
                return BinarySensorDeviceClass.OCCUPANCY

        return BinarySensorDeviceClass.PRESENCE

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """ Gets the attributes. """
        self._attributes = { CONF_ENTITY_ID: self._state }
        return self._attributes

    @property
    def name(self) -> str:
        """ Gets the name of the entity. """
        return self._name

    @property
    def should_poll(self):
        """ Gets a boolean indicating whether the entity should be polled. """
        return False

    @property
    def state(self) -> str:
        """ Gets the state of the entity. """
        return STATE_ON if len(self._state) > 0 else STATE_OFF

    @property
    def unique_id(self) -> str:
        """ Gets the unique id of the sensor. """
        return self._unique_id


    #--------------------------------------------#
    #       Event Handlers
    #--------------------------------------------#

    async def async_added_to_hass(self) -> None:
        """ Triggered when the entity has been added to Home Assistant. """
        if self.hass.is_running:
            return await self.async_setup()
        else:
            return self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, self.async_setup)

    async def async_will_remove_from_hass(self) -> None:
        """ Triggered when the entity is being removed from Home Assistant. """
        pass


    #--------------------------------------------#
    #       Methods - Setup
    #--------------------------------------------#

    async def async_setup(self, *args: Any) -> None:
        """ Sets up the entity state and event trackers. """
        self.async_on_remove(async_track_state_change(self.hass, self._entities, self.async_update_state))
        await self.async_update_state()


    #--------------------------------------------#
    #       Methods - Updates
    #--------------------------------------------#

    async def async_update_state(self, *args) -> None:
        """ Called when the state of an entity changes. """
        self._state = self._get_state()
        self.async_schedule_update_ha_state(True)


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_state(self) -> bool:
        """ Reevalutes the state of the entity. """
        result = []

        for entity_id in self._entities:
            state = self.hass.states.get(entity_id)

            if state is None:
                continue

            if state.state == STATE_UNAVAILABLE:
                continue

            if state.state in self._states_on:
                result.append(entity_id)

        return result