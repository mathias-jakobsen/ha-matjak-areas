#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import (
    CONF_AREAS,
    CONF_DEVICE_CLASS,
    CONF_ENABLE,
    CONF_EXCLUDE_ENTITIES,
    CONF_INCLUDE_ENTITIES,
    CONF_NAME
)
from .functions import flatten_list
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.template import area_entities
from logging import getLogger
from types import MethodType
from typing import Any, Callable, cast, TypedDict, Union
import weakref


#-----------------------------------------------------------#
#       Types
#-----------------------------------------------------------#

UpdateListener = Callable[[], None]
RemoveListener = Callable[[], None]

class RegistryConfig(TypedDict):
    areas: list[str]
    exclude_entities: list[str]
    include_entities: list[str]
    name: str


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       MA_Registry
#-----------------------------------------------------------#

class MA_Registry:
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self._config       : RegistryConfig       = { **config_entry.data, **config_entry.options }
        self._config_entry : ConfigEntry          = config_entry
        self._entities     : list[str]            = self._process_entity_config(hass, config_entry, self._config)
        self._hass         : HomeAssistant        = hass
        self._listeners    : list[UpdateListener] = []
        self._name         : str                  = self._config.get(CONF_NAME)
        config_entry.async_on_unload(self._setup_listeners())


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def name(self) -> str:
        return self._name


    #--------------------------------------------#
    #       Methods - Listeners
    #--------------------------------------------#

    def add_update_listener(self, listener: UpdateListener) -> RemoveListener:
        """ Adds an update listener. """
        weak_listener = self._create_weak_listener(listener)
        self._listeners.append(weak_listener)
        return lambda: self._listeners.remove(weak_listener)


    #--------------------------------------------#
    #       Methods - Getters
    #--------------------------------------------#

    def get_feature(self, feature: str) -> dict[str, Any]:
        """ Gets a specific feature. """
        feature_config = self._config.get(feature, None)

        if feature_config and not feature_config.get(CONF_ENABLE, False):
            return None

        return feature_config

    def get_entities(self, domains: list[str] = None, device_classes: list[str] = None) -> list[str]:
        """ Gets a list of entities. """
        result = []

        for entity_id in self._entities:
            state = self._hass.states.get(entity_id)

            if state is None:
                continue

            if domains is not None and entity_id.split(".")[0] not in domains:
                continue

            if device_classes is not None:
                if state.attributes.get(CONF_DEVICE_CLASS, None) not in device_classes:
                    continue

            result.append(entity_id)

        return result


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _create_weak_listener(self, listener: Callable) -> Union[weakref.WeakMethod[MethodType], weakref.ref]:
        """ Creates a weak listener from a listener. """
        return weakref.WeakMethod(cast(MethodType, listener)) if hasattr(listener, "__self__") else weakref.ref(listener)

    def _process_entity_config(self, hass: HomeAssistant, config_entry: ConfigEntry, config: dict[str, Any]) -> list[str]:
        """ Processes the entity configuration, resulting a list of entities. """
        area_entity_ids = flatten_list([area_entities(hass, area) for area in config.get(CONF_AREAS, [])])
        excluded_entity_ids = config.get(CONF_EXCLUDE_ENTITIES, [])
        included_entity_ids = config.get(CONF_INCLUDE_ENTITIES, [])
        entry_entity_ids = [entry.entity_id for entry in entity_registry.async_entries_for_config_entry(entity_registry.async_get(hass), config_entry.entry_id)]
        filtered_area_entity_ids = [entity_id for entity_id in area_entity_ids if entity_id not in excluded_entity_ids + entry_entity_ids]
        entities = filtered_area_entity_ids + included_entity_ids

        # check disabled devices?

        for entity_id in entities:
            entity = entity_registry.async_get(hass).async_get(entity_id)

            if entity is not None and entity.disabled:
                entities.remove(entity_id)

        return entities

    def _setup_listeners(self) -> None:
        """ Sets up the event listeners. """
        debounce_listener = None
        debounce_time = 1
        should_reload = True

        async def async_reload(*args: Any) -> None:
            nonlocal should_reload
            LOGGER.debug("Registry updated")
            should_reload = False
            self._entities = self._process_entity_config(self._hass, self._config_entry, self._config)
            for listener in self._listeners:
                self._hass.async_create_task(listener()())
            should_reload = True

        async def async_on_registry_update(*args: Any) -> None:
            nonlocal debounce_listener, debounce_time, should_reload

            if not self._hass.is_running:
                return

            if not should_reload:
                return

            if debounce_listener:
                debounce_listener()

            debounce_listener = async_call_later(self._hass, debounce_time, async_reload)

        self._config_entry.async_on_unload(self._hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, async_on_registry_update))
        self._config_entry.async_on_unload(self._hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, async_on_registry_update))

        return lambda: debounce_listener and debounce_listener()