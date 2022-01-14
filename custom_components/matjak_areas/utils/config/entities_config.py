#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..functions import flatten_list
from .area_config import AreaConfig
from .base_config import BaseConfig
from dataclasses import dataclass, field
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_registry
from homeassistant.helpers.template import area_entities
from typing import Any
import voluptuous as vol


#-----------------------------------------------------------#
#       EntitiesConfig
#-----------------------------------------------------------#

@dataclass
class EntitiesConfig(BaseConfig):
    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    exclude_entities: list[str] = field(default_factory=list)
    include_entities: list[str] = field(default_factory=list)


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

        area_entity_ids = sorted(flatten_list([area_entities(hass, area) for area in area_config.areas]))
        entry_entity_ids = [entry.entity_id for entry in entity_registry.async_entries_for_config_entry(entity_registry.async_get(hass), config_entry.entry_id)]
        all_entity_ids = sorted([entity_id for entity_id in hass.states.async_entity_ids() if entity_id not in area_entity_ids + entry_entity_ids])

        exclude_entity_ids = self.exclude_entities + [entity_id for entity_id in area_entity_ids if entity_id not in self.exclude_entities]
        include_entity_ids = self.include_entities + [entity_id for entity_id in all_entity_ids if entity_id not in self.include_entities]

        return vol.Schema({
            vol.Required("exclude_entities", default=self.exclude_entities): cv.multi_select(exclude_entity_ids),
            vol.Required("include_entities", default=self.include_entities): cv.multi_select(include_entity_ids)
        })

