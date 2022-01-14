#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from homeassistant.core import HomeAssistant
from dataclasses import dataclass
from typing import Any
import voluptuous as vol


#-----------------------------------------------------------#
#       BaseConfig
#-----------------------------------------------------------#

@dataclass
class BaseConfig:
    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def get_schema(self, hass: HomeAssistant, **kwargs: Any) -> vol.Schema:
        """ Gets the associated voluptuous schema. """
        return vol.Schema({}, extra=vol.REMOVE_EXTRA)

    def validate(self, hass: HomeAssistant) -> tuple[bool, dict[str, str]]:
        """ Validates the configuration. """
        return True, {}