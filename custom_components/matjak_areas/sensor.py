#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import (
    AGGREGATE_MODE_SUM,
    CONF_DEVICE_CLASSES,
    DOMAIN,
    Features
)
from .utils.ma_entity import MA_Entity
from .utils.ma_registry import MA_Registry
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change
from logging import getLogger
from statistics import mean
from typing import Any, Callable


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       Entry Setup
#-----------------------------------------------------------#

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable) -> bool:
    """ Called when a config entry is being setup.  """
    registry = hass.data[DOMAIN][config_entry.entry_id]
    feature_aggregation_config = registry.get_feature(Features.SENSOR_AGGREGATION)

    if feature_aggregation_config:
        async_add_entities(create_aggregation_sensors(hass, registry, feature_aggregation_config))

    return True


#-----------------------------------------------------------#
#       Sensor Setup
#-----------------------------------------------------------#

def create_aggregation_sensors(hass: HomeAssistant, registry: MA_Registry, config: dict[str, Any]) -> Any:
    """ Creates the aggregation sensors. """
    return [AggregationSensor(registry, device_class) for device_class in config.get(CONF_DEVICE_CLASSES)]


#-----------------------------------------------------------#
#       AggregationSensor
#-----------------------------------------------------------#

class AggregationSensor(MA_Entity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, registry: MA_Registry, device_class: str):
        self._device_class   : str         = device_class
        self._entities       : list[str]   = []
        self._registry       : MA_Registry = registry
        self._state_listener : Callable    = None


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def device_class(self) -> str:
        """ Gets the device class of the sensor. """
        return self._device_class

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """ Gets the attributes. """
        return {}

    @property
    def name(self) -> str:
        """ Gets the name. """
        return f"{self._registry.name} {self._device_class.capitalize()}"

    @property
    def unit_of_measurement(self) -> str:
        """ Gets the unit of measurement. """
        for entity_id in self._entities:
            state = self.hass.states.get(entity_id)

            if state is None:
                continue

            return state.attributes.get(CONF_UNIT_OF_MEASUREMENT)

        return ""


    #--------------------------------------------#
    #       Methods - Setup/Update/Remove
    #--------------------------------------------#

    async def async_setup(self, *args: Any) -> None:
        """ Triggered when the entity is being setup. """
        self.async_on_remove(self._registry.add_update_listener(self.async_on_registry_updated))
        await self._async_setup()

    async def async_update_state(self) -> None:
        """ Updates the entity. """
        self.state = self._get_state()
        self.async_schedule_update_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """ Triggered when the entity is being removed. """
        if self._state_listener:
            self._state_listener()


    #--------------------------------------------#
    #       Event handlers
    #--------------------------------------------#

    async def async_on_registry_updated(self) -> None:
        """ Triggered when the MA_Registry is updated. """
        await self._async_setup()

    async def async_on_state_change(self, *args) -> None:
        """ Triggered when the tracked entities changes state. """
        await self.async_update_state()


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    async def _async_setup(self) -> None:
        """ Sets up the entity list and listeners. """
        self._entities = self._registry.get_entities(domains=[SENSOR_DOMAIN], device_classes=[self._device_class])

        if self._state_listener:
            self._state_listener()

        self._state_listener = async_track_state_change(self.hass, self._entities, self.async_on_state_change)
        await self.async_update_state()

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

    def _setup_listeners(self) -> None:
        """ Sets up the state listeners. """
        if self._state_listener:
            self._state_listener()

        self._state_listener = async_track_state_change(self.hass, self._entities, self.async_on_state_change)
