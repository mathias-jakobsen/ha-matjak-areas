#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..functions import flatten_list
from .area_config import AreaConfig
from .base_config import BaseConfig
from .entities_config import EntitiesConfig
from dataclasses import dataclass, field
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_registry
from homeassistant.helpers.template import area_entities
from typing import Any
import voluptuous as vol


#-----------------------------------------------------------#
#       AdaptiveLightingConfig
#-----------------------------------------------------------#

@dataclass
class AdaptiveLightingConfig(BaseConfig):
    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    enable: bool = False
    entities: list[str] = field(default_factory=list)
    interval: int = 60
    max_brightness_pct: int = 100
    max_color_temp: int = 6500
    min_brightness_pct: int = 1
    min_color_temp: int = 2200
    transition: int = 60


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __post_init__(self) -> None:
        """ Triggered after the class has initially been initialized. """
        pass


    #--------------------------------------------#
    #       Overridable Methods
    #--------------------------------------------#

    def get_schema(self, hass: HomeAssistant, **kwargs: Any) -> vol.Schema:
        area_config: AreaConfig = kwargs.get("configs", {}).get("areas")
        config_entry: ConfigEntry = kwargs.get("config_entry")
        entities_config: EntitiesConfig = kwargs.get("configs", {}).get("entities")

        exclude_entity_ids = entities_config.exclude_entities
        include_entity_ids = entities_config.include_entities

        area_entity_ids = sorted(flatten_list([area_entities(hass, area) for area in area_config.areas]))
        entry_entity_ids = [entry.entity_id for entry in entity_registry.async_entries_for_config_entry(entity_registry.async_get(hass), config_entry.entry_id)]
        light_entity_ids = [entity_id for entity_id in area_entity_ids + include_entity_ids if entity_id not in entry_entity_ids + exclude_entity_ids and entity_id.split(".")[0] == LIGHT_DOMAIN]
        all_entity_ids = self.entities + [entity_id for entity_id in light_entity_ids if entity_id not in self.entities]

        return vol.Schema({
            vol.Required("enable", default=self.enable): bool,
            vol.Required("entities", default=self.entities): cv.multi_select(all_entity_ids),
            vol.Required("interval", default=self.interval): vol.All(int, vol.Range(min=1)),
            vol.Required("transition", default=self.transition): vol.All(int, vol.Range(min=1)),
            vol.Required("min_brightness_pct", default=self.min_brightness_pct): vol.All(int, vol.Range(min=1, max=100)),
            vol.Required("max_brightness_pct", default=self.max_brightness_pct): vol.All(int, vol.Range(min=1, max=100)),
            vol.Required("min_color_temp", default=self.min_color_temp): vol.All(int, vol.Range(min=2200, max=6500)),
            vol.Required("max_color_temp", default=self.max_color_temp): vol.All(int, vol.Range(min=2200, max=6500))
        })

    def validate(self, hass: HomeAssistant) -> tuple[bool, dict[str, str]]:
        errors: dict[str, str] = {}

        if self.min_brightness_pct > self.max_brightness_pct:
            errors["min_brightness_pct"] = "min_brightness_pct_high"

        if self.min_color_temp > self.max_color_temp:
            errors["min_color_temp"] = "min_color_temp_high"

        return len(errors) == 0, errors

