#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from ..const import (
    CONF_AREAS,
    CONF_DEVICE_CLASS,
    CONF_ENABLE,
    CONF_EXCLUDE_ENTITIES,
    CONF_INCLUDE_ENTITIES,
    CONF_NAME
)
from .functions import flatten_list
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry
from homeassistant.helpers.template import area_entities
from logging import getLogger
from typing import Any, Dict, List


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       MatjakArea
#-----------------------------------------------------------#

class MatjakArea:
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, id: str, config: Dict[str, Any]):
        self._areas    : List[str]      = config.get(CONF_AREAS)
        self._config   : Dict[str, Any] = config
        self._entities : List[str]      = self._process_entity_config(hass, config)
        self._hass     : HomeAssistant  = hass
        self._id       : str            = id
        self._name     : str            = config.get(CONF_NAME)


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _process_entity_config(self, hass: HomeAssistant, config: Dict[str, Any]) -> List[str]:
        """ Processes the entity configuration, resulting a list of entities. """
        area_entity_ids = flatten_list([area_entities(hass, area) for area in config.get(CONF_AREAS, [])])
        excluded_entity_ids = config.get(CONF_EXCLUDE_ENTITIES, [])
        included_entity_ids = config.get(CONF_INCLUDE_ENTITIES, [])
        filtered_area_entity_ids = [entity_id for entity_id in area_entity_ids if entity_id not in excluded_entity_ids]
        entities = filtered_area_entity_ids + included_entity_ids

        for entity_id in entities:
            entity = entity_registry.async_get(hass).async_get(entity_id)

            if entity is None or entity.disabled:
                entities.remove(entity_id)

        return entities


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def name(self) -> str:
        """ Gets the name of the area (group). """
        return self._name


    #--------------------------------------------#
    #       Methods - Getters
    #--------------------------------------------#

    def get_feature(self, feature: str) -> Dict[str, Any]:
        """ Gets a specific feature. """
        feature_config = self._config.get(feature, None)

        if feature_config and not feature_config.get(CONF_ENABLE, False):
            return None

        return feature_config

    def get_entities(self, domains: List[str] = None, device_classes: List[str] = None) -> List[str]:
        """ Gets a list of entities. """
        result = []

        for entity_id in self._entities:
            state = self._hass.states.get(entity_id)

            if state is None:
                continue

            if domains is not None and entity_id.split(".")[0] not in domains:
                continue

            if device_classes is not None:
                if state.attributes.get(CONF_DEVICE_CLASS, None) not in device_classes:
                    continue

            result.append(entity_id)

        return result
