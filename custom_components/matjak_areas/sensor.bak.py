#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import (
    AGGREGATE_MODE_SUM,
    CONF_DEVICE_CLASSES,
    DOMAIN,
    FEATURE_SENSOR_AGGREGATION
)
from .utils.matjak_area import MatjakArea
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT, EVENT_HOMEASSISTANT_START, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from logging import getLogger
from statistics import mean
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
    feature_aggregation_config = matjak_area.get_feature(FEATURE_SENSOR_AGGREGATION)

    if feature_aggregation_config:
        async_add_entities(create_aggregation_sensors(hass, matjak_area, feature_aggregation_config))

    return True


#-----------------------------------------------------------#
#       Sensor Setup
#-----------------------------------------------------------#

def create_aggregation_sensors(hass: HomeAssistant, matjak_area: MatjakArea, config: Dict[str, Any]) -> Any:
    """ Creates the aggregation sensors. """
    return [AggregationSensor(matjak_area, config, device_class) for device_class in config.get(CONF_DEVICE_CLASSES)]


#-----------------------------------------------------------#
#       AggregationSensor
#-----------------------------------------------------------#

class AggregationSensor(SensorEntity, RestoreEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, matjak_area: MatjakArea, config: Dict[str, Any], device_class: str):
        self._attributes   : Dict[str, Any] = {}
        self._config       : Dict[str, Any] = config
        self._device_class : str            = device_class
        self._entities     : List[str]      = []
        self._matjak_area  : MatjakArea     = matjak_area
        self._name         : str            = f"{matjak_area.name} {device_class.capitalize()}"
        self._state        : float          = 0
        self._unique_id    : str            = cv.slugify(self._name)


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def device_class(self) -> str:
        """ Gets the device class of the sensor. """
        return self._device_class

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """ Gets the attributes. """
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
    def state(self) -> float:
        """ Gets the state of the entity. """
        return self._state

    @property
    def unique_id(self) -> str:
        """ Gets the unique id of the sensor. """
        return self._unique_id

    @property
    def unit_of_measurement(self) -> str:
        """ Gets the unit of measurement. """
        for entity_id in self._entities:
            state = self.hass.states.get(entity_id)

            if state is None:
                continue

            return state.attributes.get(CONF_UNIT_OF_MEASUREMENT)


    #--------------------------------------------#
    #       Event Handlers
    #--------------------------------------------#

    async def async_added_to_hass(self) -> None:
        """ Triggered when the entity has been added to Home Assistant. """
        if self.hass.is_running:
            await self.async_setup()
        else:
            self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, self.async_setup)

        last_state = await self.async_get_last_state()
        is_new_entry = last_state is None

        if is_new_entry:
            self.async_update_state()
        else:
            self._state = float(last_state.state)
            self.async_schedule_update_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """ Triggered when the entity is being removed from Home Assistant. """
        pass


    #--------------------------------------------#
    #       Methods - Setup
    #--------------------------------------------#

    async def async_setup(self, *args: Any) -> None:
        """ Sets up the entity state and event trackers. """
        self._entities = self._matjak_area.get_entities(domains=[SENSOR_DOMAIN], device_classes=[self._device_class])
        self.async_on_remove(async_track_state_change(self.hass, self._entities, self.async_update_state))


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

    def _get_state(self) -> float:
        """ Reevalutes the state of the entity. """
        states = []

        for entity_id in self._entities:
            state = self.hass.states.get(entity_id)

            if state is None:
                continue

            if state.state == STATE_UNAVAILABLE:
                continue

            states.append(float(state.state))

        if len(states) > 0:
            if self._device_class in AGGREGATE_MODE_SUM:
                return round(sum(states), 2)

            return round(mean(states), 2)

        return STATE_UNKNOWN
