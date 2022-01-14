#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from ...utils.entity import MA_BinarySensorEntity
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.const import CONF_ENTITY_ID, STATE_ON
from homeassistant.helpers.event import async_track_state_change
from logging import getLogger, Logger
from typing import Any, Callable


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER: Logger = getLogger(__name__)


#-----------------------------------------------------------#
#       AggregateSensor
#-----------------------------------------------------------#

class AggregationSensor(MA_BinarySensorEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __post_init__(self, device_class: str):
        self._device_class: str = device_class
        self._entities: list[str] = []
        self._entities_on: list[str] = []
        self._state_listener: Callable = None


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def device_class(self) -> str:
        """ Gets the device class. """
        return self._device_class

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """ Gets the attributes. """
        return { CONF_ENTITY_ID: self._entities_on }

    @property
    def name(self) -> str:
        """ Gets the name. """
        return f"{self.registry.name} {self._device_class.capitalize()}"


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    async def async_clean_up(self) -> None:
        if self._state_listener:
            self._state_listener()

    async def async_setup(self, *args: Any) -> None:
        await self.async_clean_up()
        self._entities = self._get_entities()
        self._state_listener = async_track_state_change(self.hass, self._entities, self.async_on_state_change)
        await self.async_update_state()

    async def async_update_state(self) -> None:
        self._entities_on = self._get_entities_on()
        self.state = len(self._entities_on) > 0


    #--------------------------------------------#
    #       Event handlers
    #--------------------------------------------#

    async def async_on_registry_updated(self) -> None:
        """ Triggered when the MA_Registry is updated. """
        await self.async_setup()

    async def async_on_state_change(self, *args) -> None:
        """ Triggered when the tracked entities changes state. """
        await self.async_update_state()


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_entities(self) -> list[str]:
        """ Gets a list of entities to track. """
        return self.registry.get_entities(domains=[BINARY_SENSOR_DOMAIN], device_classes=[self._device_class])

    def _get_entities_on(self) -> list[str]:
        """ Gets the entities that are on. """
        result = []

        for entity_id in self._entities:
            state = self.hass.states.get(entity_id)

            if state is None:
                continue

            if state.state == STATE_ON:
                result.append(entity_id)

        return result
