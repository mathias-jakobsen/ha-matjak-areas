#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .platforms.switch.adaptive_lighting import AdaptiveLightingSwitch
from .utils.registry import get_registry
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from logging import getLogger, Logger


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER: Logger = getLogger(__name__)


#-----------------------------------------------------------#
#       Entry Setup
#-----------------------------------------------------------#

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> bool:
    """ Called when a config entry is being setup.  """
    registry = get_registry(config_entry)

    if registry.config.adaptive_lighting.enable:
        async_add_entities([AdaptiveLightingSwitch(registry, registry.config.adaptive_lighting)])

    return True