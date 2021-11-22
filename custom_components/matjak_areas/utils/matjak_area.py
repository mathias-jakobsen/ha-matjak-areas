#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from ..const import (
    CONF_AREAS,
    CONF_EXCLUDE_ENTITIES,
    CONF_INCLUDE_ENTITIES
)
from .functions import flatten_list
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import area_entities
from typing import Any, Dict, List


#-----------------------------------------------------------#
#       Class - MatjakArea
#-----------------------------------------------------------#

class MatjakArea:
    #--------------------------------------------#
    #       Static Properties
    #--------------------------------------------#

    _INSTANCES = {}


    #--------------------------------------------#
    #       Static Methods
    #--------------------------------------------#

    @staticmethod
    def get(id: str) -> MatjakArea:
        """ Gets a MatjakArea from its id. """
        return MatjakArea._INSTANCES.get(id)


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, id: str, config: Dict[str, Any]):
        self._config = config
        self._entities = self._process_entity_config(hass, config)
        self._hass = hass
        self._id = id

        MatjakArea._INSTANCES[id] = self


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _process_entity_config(self, hass: HomeAssistant, config: Dict[str, Any]) -> List[str]:
        """ Processes the entity configuration, resulting a list of entities. """
        area_entity_ids = flatten_list([area_entities(hass, area) for area in config.get(CONF_AREAS, [])])
        excluded_entity_ids = config.get(CONF_EXCLUDE_ENTITIES)
        included_entity_ids = config.get(CONF_INCLUDE_ENTITIES)
        filtered_area_entity_ids = [entity_id for entity_id in area_entity_ids if entity_id not in excluded_entity_ids]

        return filtered_area_entity_ids + included_entity_ids


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def get_feature(self, feature: str) -> Dict[str, Any]:
        """ Gets a specific feature. """
        return self._config.get(feature, None)

    def get_entities(self, domains: List[str] = [], device_classes: List[str] = []) -> List[str]:
        """ Gets a list of entities. """
        pass
