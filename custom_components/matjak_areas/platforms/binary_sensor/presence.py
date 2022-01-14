#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from ...utils.config import PresenceConfig
from ...utils.entity import MA_BinarySensorEntity
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.helpers.event import async_call_later, async_track_state_change
from logging import getLogger, Logger
from typing import Any, Callable


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER: Logger = getLogger(__name__)


#-----------------------------------------------------------#
#       PresenceSensor
#-----------------------------------------------------------#

class PresenceSensor(MA_BinarySensorEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __post_init__(self, config: PresenceConfig):
        self._clear_timeout: int = config.clear_timeout
        self._clear_listener: Callable = None
        self._config: PresenceConfig = config
        self._device_class: str = config.device_class
        self._device_classes: dict[str, list[str]] = config.device_classes
        self._domains: list[str] = config.domains
        self._entities: list[str] = []
        self._entities_on: list[str] = []
        self._states_on: list[str] = config.states_on
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
        return f"{self.registry.name} Presence"


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    async def async_clean_up(self) -> None:
        if self._clear_listener:
            self._clear_listener()

        if self._state_listener:
            self._state_listener()

    async def async_setup(self, *args: Any) -> None:
        self._entities = self._get_entities()

        if self._state_listener:
            self._state_listener()

        self._state_listener = async_track_state_change(self.hass, self._entities, self.async_on_state_change)
        await self.async_update_state()

    async def async_update_state(self) -> None:
        def async_clear(*args: Any) -> None:
            self.state = False

        self._entities_on = self._get_entities_on()

        if len(self._entities_on) == 0:
            if self._clear_listener is None:
                self._clear_listener = async_call_later(self.hass, self._clear_timeout, async_clear)
        else:
            if self._clear_listener:
                self._clear_listener()
                self._clear_listener = None

            self.state = True
            self.async_schedule_update_ha_state()


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

    def _get_entities(self) -> list[str]:
        """ Gets a list of entities to track. """
        result = []

        for domain in self._domains:
            result = result + self.registry.get_entities(domains=[domain], device_classes=self._device_classes.get(domain, []))

        return result

    def _get_entities_on(self) -> list[str]:
        """ Gets the entities that are on. """
        result = []

        for entity_id in self._entities:
            state = self.hass.states.get(entity_id)

            if state is None:
                continue

            if state.state in self._states_on:
                result.append(entity_id)

        return result
