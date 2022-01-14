#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import DOMAIN
from .registry import MA_Registry
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EVENT_HOMEASSISTANT_START, STATE_OFF, STATE_ON
from homeassistant.core import Context, State
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.template import is_template_string, Template
from homeassistant.helpers.typing import StateType
from homeassistant.util import get_random_string
from logging import getLogger
from typing import Any, Callable, Union, final


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

CONTEXT_PREFIX_LENGTH = 6
CONTEXT_MAX_LENGTH = 36
LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       MA_Entity
#-----------------------------------------------------------#

class MA_Entity(RestoreEntity, Entity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, registry: MA_Registry, *args: Any, **kwargs: Any):
        self._context_unique_id: str = get_random_string(6)
        self._registry: MA_Registry = registry
        self.__post_init__(*args, **kwargs)

    def __post_init__(self, *args, **kwargs) -> None:
        pass


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def registry(self) -> MA_Registry:
        """ Gets the MA_Registry. """
        return self._registry

    @property
    def should_poll(self) -> bool:
        """ Gets a boolean indicating whether the entity should be polled for state updates. """
        return False

    @property
    def unique_id(self) -> str:
        """ Gets the unique id. """
        return cv.slugify(self.name)


    #--------------------------------------------#
    #       Event Handlers
    #--------------------------------------------#

    async def async_added_to_hass(self) -> None:
        """ Triggered when the entity has been added to HomeAssistant. """
        if self.hass.is_running:
            await self.async_setup()
        else:
            self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, self.async_setup)

        await self.async_initialize(await self.async_get_last_state())

    async def async_will_remove_from_hass(self) -> None:
        """ Triggered when the entity is about to be removed from HomeAssistant. """
        await self.async_clean_up()


    #--------------------------------------------#
    #       Overridable Methods
    #--------------------------------------------#

    async def async_clean_up(self) -> None:
        """ Cleans up the entity. """
        pass

    async def async_initialize(self, last_state: Union[State, None]) -> None:
        """ Triggered when the entity has been added. """
        pass

    async def async_setup(self, *args: Any) -> None:
        """ Sets up the entity when Homeassistant has fully started. """
        pass


    #--------------------------------------------#
    #       Overridable Event Handlers
    #--------------------------------------------#

    async def async_on_registry_updated(self) -> None:
        """ Triggered when the MA registry is updated. """
        pass


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def create_context(self) -> Context:
        """ Creates a new context. """
        return Context(id=f"{self._context_unique_id}{get_random_string(CONTEXT_MAX_LENGTH)}"[:CONTEXT_MAX_LENGTH])

    def is_context_internal(self, context: Context) -> bool:
        """ Determines whether the context is of internal origin (created by the class instance). """
        return context.id.startswith(self._context_unique_id)

    def call_service(self, domain: str, service: str, **service_data: Any) -> Context:
        """ Calls a service. """
        context = self.create_context()
        parsed_service_data = self._parse_service_data(service_data)
        self.hass.async_create_task(self.hass.services.async_call(domain, service, parsed_service_data, context=context))
        return context

    def fire_event(self, event_type: str, **event_data: Any) -> Context:
        """ Fires an event using the Home Assistant event bus. """
        context = self.create_context()
        self.hass.bus.async_fire(event_type, event_data, context=context)
        return context


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _parse_service_data(self, service_data: dict[str, Any]) -> dict[str, Any]:
        """ Parses the service data by rendering possible templates. """
        result = {}

        for key, value in service_data.items():
            if isinstance(value, str) and is_template_string(value):
                try:
                    template = Template(value, self.hass)
                    result[key] = template.async_render()
                except Exception as e:
                    LOGGER.warn(f"Error parsing {key} in service_data {service_data}: Invalid template was given -> {value}.")
                    LOGGER.warn(e)
            else:
                result[key] = value

        return result


#-----------------------------------------------------------#
#       MA_SensorEntity
#-----------------------------------------------------------#

class MA_SensorEntity(MA_Entity):
    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    _state: StateType = None


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def state(self) -> StateType:
        """ Gets the state. """
        return self._state

    @state.setter
    def state(self, value: StateType) -> None:
        """ Sets the state. """
        self._state = value
        self.async_schedule_update_ha_state()


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    @final
    async def async_initialize(self, last_state: Union[State, None]) -> None:
        self.async_on_remove(self.registry.add_update_listener(self.async_on_registry_updated))

        if last_state:
            self.state = last_state.state
        else:
            await self.async_update_state()


    #--------------------------------------------#
    #       Overridable Methods
    #--------------------------------------------#

    async def async_update_state(self) -> None:
        """ Updates the entity state. """
        pass


#-----------------------------------------------------------#
#       MA_BinarySensorEntity
#-----------------------------------------------------------#

class MA_BinarySensorEntity(MA_SensorEntity):
    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @MA_SensorEntity.state.getter
    def state(self) -> StateType:
        return STATE_ON if super().state else STATE_OFF


#-----------------------------------------------------------#
#       MA_SwitchEntity
#-----------------------------------------------------------#

class MA_SwitchEntity(MA_Entity, SwitchEntity):
    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    _is_on: bool = None
    _registry_listener: Callable = None


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @final
    @property
    def is_on(self) -> bool:
        """ Gets a boolean indicating whether the entity is turned on. """
        return self._is_on


    #--------------------------------------------#
    #       Methods (Setup/Clean Up)
    #--------------------------------------------#

    @final
    async def async_initialize(self, last_state: Union[State, None]) -> None:
        self._is_on = last_state and last_state.state == STATE_ON

        if self._is_on:
            self._registry_listener = self.registry.add_update_listener(self.async_on_registry_updated)

        self.async_schedule_update_ha_state()


    #--------------------------------------------#
    #       Methods (Turn On/Turn Off)
    #--------------------------------------------#

    @final
    async def async_turn_off(self, **kwargs: Any) -> None:
        """ Turns off the entity. """
        if not self._is_on:
            return

        self._is_on = False
        self._registry_listener()

        await self.async_clean_up()

    @final
    async def async_turn_on(self, **kwargs: Any) -> None:
        """ Turns on the entity. """
        if self._is_on:
            return

        self._is_on = True
        self._registry_listener = self.registry.add_update_listener(self.async_on_registry_updated)

        await self.async_setup()

