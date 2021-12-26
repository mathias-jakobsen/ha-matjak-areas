#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import (
    DOMAIN,
    PLATFORMS
)
from .utils.ma_registry import MA_Registry
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import IntegrationError
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_ENTITY_REGISTRY_UPDATED
from homeassistant.helpers.event import async_call_later
from logging import getLogger
from typing import Any, Dict


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)
REGISTRY_LISTENER = None


#-----------------------------------------------------------#
#       Registry Listener Setup
#-----------------------------------------------------------#

def setup_registry_listener(hass: HomeAssistant) -> None:
    """ Sets up the registry listener. """
    debounce_listener = None
    debounce_time = 1
    registry_listeners = []
    should_reload = True

    async def async_reload(*args: Any) -> None:
        nonlocal should_reload
        LOGGER.debug("Registry Updated -> Updating MA Registries")
        should_reload = False

        for registry in hass.data[DOMAIN].values():
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


#-----------------------------------------------------------#
#       Setup
#-----------------------------------------------------------#

async def async_setup(hass: HomeAssistant, config: Dict[Any, str]) -> bool:
    """ Called when the component is being setup. """
    if DOMAIN in config:
        raise IntegrationError(f"{DOMAIN} can only be loaded from the UI. Remove {DOMAIN} from your YAML configuration.")

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Called when a config entry is being setup.  """
    global REGISTRY_LISTENER

    data = hass.data.setdefault(DOMAIN, {})
    data[config_entry.entry_id] = MA_Registry(hass, config_entry)

    if REGISTRY_LISTENER is None:
        REGISTRY_LISTENER = setup_registry_listener(hass)

    for platform in PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, platform))

    config_entry.async_on_unload(config_entry.add_update_listener(async_update_options))
    return True

async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Called when a config entry is being updated. """
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Called when a config entry is being unloaded. """
    unload_ok = all(
        [
            await hass.config_entries.async_forward_entry_unload(config_entry, platform)
            for platform in PLATFORMS
        ]
    )

    data = hass.data[DOMAIN]

    if unload_ok:
        data.pop(config_entry.entry_id)

    return unload_ok

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Called when a config entry is being removed. """
    global REGISTRY_LISTENER

    if len(hass.data[DOMAIN]) == 0:
        hass.data.pop(DOMAIN)
        REGISTRY_LISTENER()
        REGISTRY_LISTENER = None