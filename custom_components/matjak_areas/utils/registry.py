#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .config import RegistryConfig
from .functions import flatten_list
from .types import RemoveListener
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_CLASS
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.template import area_entities
from logging import getLogger, Logger
from types import MethodType
from typing import Any, Callable, cast, Union
import weakref


#-----------------------------------------------------------#
#       Types
#-----------------------------------------------------------#

RegistryUpdateListener = Callable[[], None]


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER: Logger = getLogger(__name__)


#-----------------------------------------------------------#
#       Variables
#-----------------------------------------------------------#

_registry_listener: RemoveListener = None
_registries: dict[str, MA_Registry] = {}


#-----------------------------------------------------------#
#       MA_Registry
#-----------------------------------------------------------#

class MA_Registry:
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self._config: RegistryConfig = RegistryConfig(config_entry.options)
        self._config_entry: ConfigEntry = config_entry
        self._entities: list[str] = self._process_entity_config(hass, config_entry, self._config)
        self._hass: HomeAssistant = hass
        self._listeners: list[RegistryUpdateListener] = []
        self._name: str = config_entry.title


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def config(self) -> RegistryConfig:
        """ Gets the registry config. """
        return self._config

    @property
    def name(self) -> str:
        """ Gets the name. """
        return self._name


    #--------------------------------------------#
    #       Methods - Updating
    #--------------------------------------------#

    def add_update_listener(self, listener: RegistryUpdateListener) -> RemoveListener:
        """ Adds an update listener. """
        weak_listener = self._create_weak_listener(listener)
        self._listeners.append(weak_listener)
        return lambda: self._listeners.remove(weak_listener)

    def update_entities(self) -> None:
        """ Updates the entity list. """
        self._entities = self._process_entity_config(self._hass, self._config_entry, self._config)
        for listener in self._listeners:
            self._hass.async_create_task(listener()())


    #--------------------------------------------#
    #       Methods - Getters
    #--------------------------------------------#

    def get_entities(self, domains: list[str] = [], device_classes: list[str] = []) -> list[str]:
        """ Gets a list of entities. """
        result = []

        for entity_id in self._entities:
            state = self._hass.states.get(entity_id)

            if state is None:
                continue

            if len(domains) > 0 and entity_id.split(".")[0] not in domains:
                continue

            if len(device_classes) > 0:
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

    def _process_entity_config(self, hass: HomeAssistant, config_entry: ConfigEntry, config: RegistryConfig) -> list[str]:
        """ Processes the entity configuration, resulting a list of entities. """
        area_entity_ids = flatten_list([area_entities(hass, area) for area in config.areas])
        excluded_entity_ids = config.entities.exclude_entities
        included_entity_ids = config.entities.include_entities
        entry_entity_ids = [entry.entity_id for entry in entity_registry.async_entries_for_config_entry(entity_registry.async_get(hass), config_entry.entry_id)]
        filtered_area_entity_ids = [entity_id for entity_id in area_entity_ids if entity_id not in excluded_entity_ids + entry_entity_ids]
        entities = filtered_area_entity_ids + included_entity_ids

        # check disabled devices?

        for entity_id in entities:
            entity = entity_registry.async_get(hass).async_get(entity_id)

            if entity is not None and entity.disabled:
                entities.remove(entity_id)

        return entities


#-----------------------------------------------------------#
#       Public Methods
#-----------------------------------------------------------#

def create_registry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Creates a registry. """
    global _registry_listener

    if _registry_listener is None:
        _registry_listener = setup_listeners(hass)

    _registries[config_entry.entry_id] = MA_Registry(hass, config_entry)

def get_registry(config_entry: ConfigEntry) -> MA_Registry:
    """ Gets a registry. """
    return _registries.get(config_entry.entry_id, None)

def remove_registry(config_entry: ConfigEntry) -> None:
    """ Removes a registry """
    global _registry_listener
    _registries.pop(config_entry.entry_id, None)

    if len(_registries) == 0:
        _registry_listener()
        _registry_listener = None


#-----------------------------------------------------------#
#       Private Methods
#-----------------------------------------------------------#

def setup_listeners(hass: HomeAssistant):
    """ Sets up the registry listener. """
    debounce_listener = None
    debounce_time = 1
    registry_listeners = []
    should_reload = True

    async def async_reload(*args: Any) -> None:
        nonlocal should_reload
        LOGGER.debug("Entity- or Device registry was updated. Updating MA_Registry.")
        should_reload = False

        for registry in _registries.values():
            registry.update_entities()

        should_reload = True

    async def async_on_registry_update(*args: Any) -> None:
        nonlocal debounce_listener, debounce_time, should_reload

        if not hass.is_running:
            return

        if not should_reload:
            return

        if debounce_listener:
            debounce_listener()

        debounce_listener = async_call_later(hass, debounce_time, async_reload)

    def remove_listeners() -> None:
        if debounce_listener:
            debounce_listener()

        while registry_listeners:
            registry_listeners.pop()()

    registry_listeners.append(hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, async_on_registry_update))
    registry_listeners.append(hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, async_on_registry_update))

    return lambda: remove_listeners()