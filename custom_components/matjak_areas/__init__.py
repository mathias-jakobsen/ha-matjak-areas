#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import (
    DOMAIN,
    PLATFORMS
)
from .utils.matjak_area import MatjakArea
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import IntegrationError
from logging import getLogger
from typing import Any, Dict


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__package__)
REMOVE_LISTENERS = {}


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

    REMOVE_LISTENERS[config_entry.entry_id] = config_entry.add_update_listener(async_update_options)

    for platform in PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, platform))

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

    REMOVE_LISTENERS[config_entry.entry_id]()

    return unload_ok

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Called when a config entry is being removed. """
    pass