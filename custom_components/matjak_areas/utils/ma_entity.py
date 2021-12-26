#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from homeassistant.const import EVENT_HOMEASSISTANT_START, STATE_OFF, STATE_ON
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType
from logging import getLogger
from typing import Any


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       MA_Entity
#-----------------------------------------------------------#

class MA_Entity(RestoreEntity, Entity):
    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    _state : StateType = None


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def should_poll(self) -> bool:
        """ Gets a boolean indicating whether the entity should be polled for state updates. """
        return False

    @property
    def state(self) -> StateType:
        """ Gets the state. """
        return self._state

    @state.setter
    def state(self, value: StateType) -> None:
        self._state = value

    @property
    def unique_id(self) -> str:
        """ Gets the unique id. """
        return cv.slugify(self.name)


    #--------------------------------------------#
    #       Event Handlers
    #--------------------------------------------#

    async def async_added_to_hass(self) -> None:
        """ Triggered when the entity has been added to Home Assistant. """
        async def async_initialize(*args: Any) -> None:
            await self.async_setup()

        if self.hass.is_running:
            await async_initialize()
        else:
            self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, async_initialize)

        last_state = await self.async_get_last_state()

        if last_state:
            self._state = last_state.state
            self.async_schedule_update_ha_state()
        else:
            await self.async_update_state()

    async def async_will_remove_from_hass(self) -> None:
        """ Triggered when the entity is being removed from Home Assistant. """
        pass


    #--------------------------------------------#
    #       Overridable Methods
    #--------------------------------------------#

    async def async_setup(self) -> None:
        """ Triggered when the entity is being setup. """
        pass

    async def async_update_state(self) -> None:
        """ Updates the entity state. """
        self.async_schedule_update_ha_state()


#-----------------------------------------------------------#
#       MA_BinarySensorEntity
#-----------------------------------------------------------#

class MA_BinarySensorEntity(MA_Entity):
    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @MA_Entity.state.getter
    def state(self) -> StateType:
        return STATE_ON if super().state else STATE_OFF
