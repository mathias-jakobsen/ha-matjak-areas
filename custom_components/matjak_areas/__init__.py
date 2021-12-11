#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import (
    ATTR_ENTRY_ID,
    CONF_AUTO_RELOAD,
    DOMAIN,
    EVENT,
    PLATFORMS
)
from .utils.matjak_area import MatjakArea
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import Event, HomeAssistant
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


#-----------------------------------------------------------#
#       Auto Reload
#-----------------------------------------------------------#

def setup_auto_reload(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Sets up the auto reloading feature. """
    debounce_listener = None
    debounce_time = 0.5
    reload_listener = None
    should_reload = True

    async def async_reload(*args: Any) -> None:
        nonlocal reload_listener, should_reload

        if reload_listener:
            reload_listener()

        reload_listener = hass.bus.async_listen(EVENT, async_on_reload)
        should_reload = False

        await hass.config_entries.async_reload(config_entry.entry_id)

    async def async_on_registry_update(*args: Any) -> None:
        nonlocal debounce_listener, debounce_time, should_reload

        if not hass.is_running:
            return

        if not should_reload:
            return

        if debounce_listener:
            debounce_listener()

        debounce_listener = async_call_later(hass, debounce_time, async_reload)

    async def async_on_reload(event: Event) -> None:
        nonlocal reload_listener, should_reload

        if event.data.get(ATTR_ENTRY_ID, None) == config_entry.entry_id:
            reload_listener()
            should_reload = True

    config_entry.async_on_unload(hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, async_on_registry_update))
    config_entry.async_on_unload(hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, async_on_registry_update))
    hass.bus.async_fire(EVENT, { ATTR_ENTRY_ID: config_entry.entry_id })


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
    data = hass.data.setdefault(DOMAIN, {})
    data[config_entry.entry_id] = MatjakArea(hass, config_entry.entry_id, config_entry.options)

    for platform in PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, platform))

    if config_entry.options.get(CONF_AUTO_RELOAD, False):
        setup_auto_reload(hass, config_entry)

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
    pass