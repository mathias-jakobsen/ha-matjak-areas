#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import (
    CONF_BINARY_SENSOR_DEVICE_CLASSES,
    CONF_DEVICE_CLASSES,
    CONF_DOMAINS,
    CONF_MEDIA_PLAYER_DEVICE_CLASSES,
    CONF_STATES_ON,
    DOMAIN,
    Features
)
from .utils.ma_entity import MA_BinarySensorEntity
from .utils.ma_registry import MA_Registry
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN, BinarySensorDeviceClass
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENTITY_ID, STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change
from logging import getLogger
from typing import Any, Callable, TypedDict


#-----------------------------------------------------------#
#       Types
#-----------------------------------------------------------#

class PresenceConfig(TypedDict):
    enable: bool
    entities: list[str]
    states_on: list[str]


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
    feature_aggregation_config = registry.get_feature(Features.BINARY_SENSOR_AGGREGATION)
    feature_presence_config = registry.get_feature(Features.PRESENCE)

    if feature_aggregation_config:
        async_add_entities(create_aggregate_sensors(hass, registry, feature_aggregation_config))

    if feature_presence_config:
        async_add_entities([create_presence_sensor(hass, registry, feature_presence_config)])

    return True


#-----------------------------------------------------------#
#       Sensor Setup
#-----------------------------------------------------------#

def create_presence_sensor(hass: HomeAssistant, registry: MA_Registry, config: dict[str, Any]) -> PresenceSensor:
    """ Handles the creation of the presence sensor. """
    return PresenceSensor(registry, config)

def create_aggregate_sensors(hass: HomeAssistant, registry: MA_Registry, config: dict[str, Any]) -> list[AggregateSensor]:
    """ Handles the creation of the aggregation sensors. """
    result = []

    for device_class in config.get(CONF_DEVICE_CLASSES, []):
        result.append(AggregateSensor(registry, device_class))

    return result


#-----------------------------------------------------------#
#       PresenceSensor
#-----------------------------------------------------------#

class PresenceSensor(MA_BinarySensorEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, registry: MA_Registry, config: PresenceConfig):
        self._config         : PresenceConfig       = config
        self._device_classes : dict[str, list[str]] = { BINARY_SENSOR_DOMAIN: config.get(CONF_BINARY_SENSOR_DEVICE_CLASSES), MEDIA_PLAYER_DOMAIN: config.get(CONF_MEDIA_PLAYER_DEVICE_CLASSES) }
        self._domains        : list[str]            = config.get(CONF_DOMAINS)
        self._entities       : list[str]            = []
        self._entities_on    : list[str]            = []
        self._registry       : MA_Registry          = registry
        self._states_on      : list[str]            = config.get(CONF_STATES_ON)
        self._state_listener : Callable             = None


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def device_class(self) -> str:
        """ Gets the device class. """
        if BINARY_SENSOR_DOMAIN in self._domains:
            return BinarySensorDeviceClass.OCCUPANCY

        return BinarySensorDeviceClass.PRESENCE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """ Gets the attributes. """
        return { CONF_ENTITY_ID: self._entities_on }

    @property
    def name(self) -> str:
        """ Gets the name. """
        return f"{self._registry.name} Presence"


    #--------------------------------------------#
    #       Methods - Setup/Update/Remove
    #--------------------------------------------#

    async def async_setup(self, *args: Any) -> None:
        """ Triggered when the entity is being setup. """
        self.async_on_remove(self._registry.add_update_listener(self.async_on_registry_updated))
        await self._async_setup()

    async def async_update_state(self) -> None:
        """ Updates the entity. """
        self._entities_on = self._get_entities_on()
        self.state = len(self._entities_on) > 0
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
        self._entities = self._get_entities()

        if self._state_listener:
            self._state_listener()

        self._state_listener = async_track_state_change(self.hass, self._entities, self.async_on_state_change)
        await self.async_update_state()

    def _get_entities(self) -> list[str]:
        """ Gets a list of entities to track. """
        result = []

        for domain in self._domains:
            result = result + self._registry.get_entities(domains=[domain], device_classes=self._device_classes.get(domain, []))

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


#-----------------------------------------------------------#
#       AggregateSensor
#-----------------------------------------------------------#

class AggregateSensor(MA_BinarySensorEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, registry: MA_Registry, device_class: str):
        self._device_class   : str         = device_class
        self._entities       : list[str]   = []
        self._entities_on    : list[str]   = []
        self._registry       : MA_Registry = registry
        self._state_listener : Callable    = None


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
        return f"{self._registry.name} {self._device_class.capitalize()}"


    #--------------------------------------------#
    #       Methods - Setup/Update
    #--------------------------------------------#

    async def async_setup(self, *args: Any) -> None:
        """ Triggered when the entity is being setup. """
        self.async_on_remove(self._registry.add_update_listener(self.async_on_registry_updated))
        await self._async_setup()

    async def async_update_state(self) -> None:
        """ Updates the entity. """
        self._entities_on = self._get_entities_on()
        self.state = len(self._entities_on) > 0
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
        self._entities = self._get_entities()

        if self._state_listener:
            self._state_listener()

        self._state_listener = async_track_state_change(self.hass, self._entities, self.async_on_state_change)
        await self.async_update_state()

    def _get_entities(self) -> list[str]:
        """ Gets a list of entities to track. """
        return self._registry.get_entities(domains=[BINARY_SENSOR_DOMAIN], device_classes=[self._device_class])

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

