#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import (
    FEATURE_PRESENCE
)
from .utils.matjak_area import MatjakArea
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


#-----------------------------------------------------------#
#       Entry Setup
#-----------------------------------------------------------#

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Called when a config entry is being setup.  """
    matjak_area = MatjakArea.get(config_entry.entry_id)
    feature_config = matjak_area.get_feature(FEATURE_PRESENCE)

    if feature_config:
        pass # create presence sensor

    return True

