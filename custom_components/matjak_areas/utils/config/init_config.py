#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .base_config import BaseConfig
from homeassistant.core import HomeAssistant
from dataclasses import dataclass
from typing import Any
import voluptuous as vol


#-----------------------------------------------------------#
#       InitConfig
#-----------------------------------------------------------#

@dataclass
class InitConfig(BaseConfig):
    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    title: str = ""


    #--------------------------------------------#
    #       Overridable Methods
    #--------------------------------------------#

    def get_schema(self, hass: HomeAssistant, **kwargs: Any) -> vol.Schema:
        return vol.Schema({
            vol.Required("title", default=self.title): str,
        })


