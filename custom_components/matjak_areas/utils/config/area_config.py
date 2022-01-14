#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .base_config import BaseConfig
from dataclasses import dataclass, field
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry, config_validation as cv
from homeassistant.helpers.template import area_id, area_name
from typing import Any
import voluptuous as vol


#-----------------------------------------------------------#
#       AreaConfig
#-----------------------------------------------------------#

@dataclass
class AreaConfig(BaseConfig):
    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    areas: list[str] = field(default_factory=list)


    #--------------------------------------------#
    #       Overridable Methods
    #--------------------------------------------#

    def get_schema(self, hass: HomeAssistant, **kwargs: Any) -> vol.Schema:
        all_areas = sorted([area.name for area in area_registry.async_get(hass).async_list_areas()])
        selected_areas = [area_name(hass, area) for area in self.areas]
        areas = selected_areas + [area for area in all_areas if area not in selected_areas]

        return vol.Schema({
            vol.Required("areas", default=selected_areas): cv.multi_select(areas)
        })

    def validate(self, hass: HomeAssistant) -> tuple[bool, dict[str, str]]:
        self.areas = [area_id(hass, area) for area in self.areas]
        return super().validate(hass)

