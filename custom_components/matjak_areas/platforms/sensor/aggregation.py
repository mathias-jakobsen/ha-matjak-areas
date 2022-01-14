#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from ...utils.entity import MA_SensorEntity
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN, SensorDeviceClass
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers.event import async_track_state_change
from logging import getLogger, Logger
from statistics import mean
from typing import Any, Callable


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

AGGREGATE_MODE_SUM: list[str] = [
    SensorDeviceClass.CURRENT,
    SensorDeviceClass.ENERGY,
    SensorDeviceClass.POWER
]
LOGGER: Logger = getLogger(__name__)


#-----------------------------------------------------------#
#       AggregationSensor
#-----------------------------------------------------------#

class AggregationSensor(MA_SensorEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __post_init__(self, device_class: str):
        self._device_class: str = device_class
        self._entities: list[str] = []
        self._state_listener: Callable  = None


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
        return f"{self.registry.name} {self._device_class.capitalize()}"

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

    async def async_clean_up(self) -> None:
        if self._state_listener:
            self._state_listener()

    async def async_setup(self, *args: Any) -> None:
        await self.async_clean_up()
        self._entities = self.registry.get_entities(domains=[SENSOR_DOMAIN], device_classes=[self._device_class])
        self._state_listener = async_track_state_change(self.hass, self._entities, self.async_on_state_change)
        await self.async_update_state()

    async def async_update_state(self) -> None:
        self.state = self._get_state()


    #--------------------------------------------#
    #       Event handlers
    #--------------------------------------------#

    async def async_on_registry_updated(self) -> None:
        await self.async_setup()

    async def async_on_state_change(self, *args) -> None:
        """ Triggered when the tracked entities changes state. """
        await self.async_update_state()


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

            if state.state in [STATE_UNAVAILABLE, STATE_UNKNOWN]:
                continue

            states.append(float(state.state))

        if len(states) > 0:
            if self._device_class in AGGREGATE_MODE_SUM:
                return round(sum(states), 2)

            return round(mean(states), 2)

        return STATE_UNKNOWN