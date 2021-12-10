#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import (
    AGGREGATE_BINARY_SENSOR_CLASSES,
    AGGREGATE_SENSOR_CLASSES,
    CONF_AREAS,
    CONF_AUTO_RELOAD,
    CONF_DEVICE_CLASSES,
    CONF_ENABLE,
    CONF_ENTITIES,
    CONF_EXCLUDE_ENTITIES,
    CONF_GO_BACK,
    CONF_INCLUDE_ENTITIES,
    CONF_NAME,
    CONF_SELECTED_AREAS,
    CONF_STATES_ON,
    DOMAIN,
    FEATURE_BINARY_SENSOR_AGGREGATION,
    FEATURE_PRESENCE,
    FEATURE_SENSOR_AGGREGATION
)
from .utils.flow_builder import FlowBuilder
from .utils.functions import flatten_list
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import area_registry, config_validation as cv, entity_registry
from homeassistant.helpers.template import area_entities, area_id, area_name
from logging import getLogger
from typing import Any, Dict, Tuple, Union
import voluptuous as vol


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

# ------ Errors --------------
ERROR_AREA_REQUIRED = "area_required"
ERROR_NAME_REQUIRED = "name_required"

# ------ Steps ---------------
STEP_BINARY_SENSOR_AGGREGATION = "binary_sensor_aggregation"
STEP_ENTITIES = "entities"
STEP_INIT = "init"
STEP_PRESENCE = "presence"
STEP_SENSOR_AGGREGATION = "sensor_aggregation"
STEP_USER = "user"


#-----------------------------------------------------------#
#       Config Flow
#-----------------------------------------------------------#

class Matjak_ConfigFlow(ConfigFlow, domain=DOMAIN):
    #--------------------------------------------#
    #       Static Properties
    #--------------------------------------------#

    VERSION = 1


    #--------------------------------------------#
    #       Static Methods
    #--------------------------------------------#

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> Matjak_OptionsFlow:
        """ Gets the options flow. """
        return Matjak_OptionsFlow(config_entry)


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self):
        self._flow_builder = FlowBuilder(self)
        self._flow_builder.add_step(STEP_USER, self.step_user_schema_builder, self.step_user_schema_validator)


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def step_user_schema_builder(self, data: Dict[str, Any]) -> vol.Schema:
        areas = area_registry.async_get(self.hass).async_list_areas()
        area_names = sorted([area.name for area in areas])

        return vol.Schema({
            vol.Optional(CONF_NAME, default=data.get(CONF_NAME, "")): str,
            vol.Required(CONF_AREAS, default=data.get(CONF_AREAS, [])): cv.multi_select(area_names)
        })

    def step_user_schema_validator(self, user_input: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
        errors = {}

        if len(user_input[CONF_AREAS]) == 0:
            errors[CONF_AREAS] = ERROR_AREA_REQUIRED

        if len(user_input[CONF_AREAS]) > 1 and not user_input[CONF_NAME]:
            errors[CONF_NAME] = ERROR_NAME_REQUIRED

        if len(errors) == 0:
            if not user_input[CONF_NAME]:
                user_input[CONF_NAME] = user_input[CONF_AREAS][0]

            user_input[CONF_AREAS] = [area_id(self.hass, area) for area in user_input[CONF_AREAS]]

        return errors, user_input


#-----------------------------------------------------------#
#       Options Flow
#-----------------------------------------------------------#

class Matjak_OptionsFlow(OptionsFlow):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, config_entry: ConfigEntry):
        self._config_entry = config_entry
        self._flow_builder = FlowBuilder(self, { **config_entry.data, **config_entry.options })
        self._flow_builder.add_step(STEP_INIT, self.step_init_schema_builder, self.step_init_schema_validator, STEP_ENTITIES)
        self._flow_builder.add_step(STEP_ENTITIES, self.step_entities_schema_builder, self.step_entities_schema_validator, STEP_PRESENCE)
        self._flow_builder.add_step(STEP_PRESENCE, self.step_presence_schema_builder, self.step_presence_schema_validator, STEP_SENSOR_AGGREGATION)
        self._flow_builder.add_step(STEP_SENSOR_AGGREGATION, self.step_sensor_aggregation_schema_builder, self.step_sensor_aggregation_schema_validator)


    #--------------------------------------------#
    #       Init Step
    #--------------------------------------------#

    def step_init_schema_builder(self, data: Dict[str, Any]) -> vol.Schema:
        selected_area_ids = data.get(CONF_AREAS, [])
        selected_area_names = [area_name(self.hass, area_id) for area_id in selected_area_ids]

        all_area_ids = sorted([area.id for area in area_registry.async_get(self.hass).async_list_areas()])
        all_area_names = [area_name(self.hass, area_id) for area_id in all_area_ids]

        area_names = selected_area_names + [area_name for area_name in all_area_names if area_name not in selected_area_names]

        return vol.Schema({
            vol.Required(CONF_AUTO_RELOAD, default=data.get(CONF_AUTO_RELOAD, False)): bool,
            vol.Required(CONF_AREAS, default=selected_area_names): cv.multi_select(area_names)
        })

    def step_init_schema_validator(self, user_input: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
        user_input[CONF_AREAS] = [area_id(self.hass, area) for area in user_input[CONF_AREAS]]
        return {}, user_input


    #--------------------------------------------#
    #       Entities Step
    #--------------------------------------------#

    def step_entities_schema_builder(self, data: Dict[str, Any]) -> vol.Schema:
        selected_exclude_entity_ids = data.get(CONF_EXCLUDE_ENTITIES, [])
        selected_include_entity_ids = data.get(CONF_INCLUDE_ENTITIES, [])

        area_entity_ids = sorted(flatten_list([area_entities(self.hass, area) for area in data.get(CONF_AREAS, [])]))
        entry_entity_ids = [entry.entity_id for entry in entity_registry.async_entries_for_config_entry(entity_registry.async_get(self.hass), self._config_entry.entry_id)]
        all_entity_ids = sorted([entity_id for entity_id in self.hass.states.async_entity_ids() if entity_id not in area_entity_ids])

        exclude_entity_ids = selected_exclude_entity_ids + [entity_id for entity_id in area_entity_ids if entity_id not in selected_exclude_entity_ids and entity_id not in entry_entity_ids]
        include_entity_ids = selected_include_entity_ids + [entity_id for entity_id in all_entity_ids if entity_id not in selected_include_entity_ids and entity_id not in entry_entity_ids]

        return vol.Schema({
            vol.Required(CONF_EXCLUDE_ENTITIES, default=selected_exclude_entity_ids): cv.multi_select(exclude_entity_ids),
            vol.Required(CONF_INCLUDE_ENTITIES, default=selected_include_entity_ids): cv.multi_select(include_entity_ids)
        })

    def step_entities_schema_validator(self, user_input: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
        return {}, user_input


    #--------------------------------------------#
    #       Presence Step
    #--------------------------------------------#

    def step_presence_schema_builder(self, data: Dict[str, Any]) -> vol.Schema:
        feature_data = data.get(FEATURE_PRESENCE, {})
        excluded_entity_ids = data.get(CONF_EXCLUDE_ENTITIES, [])
        selected_entity_ids = [entity_id for entity_id in feature_data.get(CONF_ENTITIES, []) if entity_id not in excluded_entity_ids]
        selected_include_entity_ids = data.get(CONF_INCLUDE_ENTITIES, [])
        area_entity_ids = sorted(flatten_list([area_entities(self.hass, area) for area in data.get(CONF_AREAS, [])]))
        entry_entity_ids = [entry.entity_id for entry in entity_registry.async_entries_for_config_entry(entity_registry.async_get(self.hass), self._config_entry.entry_id)]
        filtered_area_entity_ids = [entity_id for entity_id in area_entity_ids if entity_id not in excluded_entity_ids and entity_id not in entry_entity_ids]
        entity_ids = selected_entity_ids + [entity_id for entity_id in filtered_area_entity_ids + selected_include_entity_ids if entity_id not in selected_entity_ids]
        default_states_on = ["on", "playing", "home"]

        return vol.Schema({
            vol.Required(CONF_ENABLE, default=feature_data.get(CONF_ENABLE, False)): bool,
            vol.Required(CONF_ENTITIES, default=selected_entity_ids): cv.multi_select(entity_ids),
            vol.Required(CONF_STATES_ON, default=", ".join(feature_data.get(CONF_STATES_ON, default_states_on))): str
        })

    def step_presence_schema_validator(self, user_input: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
        user_input[CONF_STATES_ON] = cv.ensure_list_csv(user_input[CONF_STATES_ON])
        return {}, { CONF_GO_BACK: user_input.pop(CONF_GO_BACK), FEATURE_PRESENCE: user_input }


    #--------------------------------------------#
    #       Sensor Aggregation Step
    #--------------------------------------------#

    def step_sensor_aggregation_schema_builder(self, data: Dict[str, Any]) -> vol.Schema:
        feature_data = data.get(FEATURE_SENSOR_AGGREGATION, {})
        selected_device_classes = feature_data.get(CONF_DEVICE_CLASSES, [])
        device_classes = selected_device_classes + [device_class for device_class in AGGREGATE_SENSOR_CLASSES if device_class not in selected_device_classes]

        return vol.Schema({
            vol.Required(CONF_ENABLE, default=feature_data.get(CONF_ENABLE, False)): bool,
            vol.Required(CONF_DEVICE_CLASSES, default=selected_device_classes): cv.multi_select(device_classes)
        })

    def step_sensor_aggregation_schema_validator(self, user_input: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
        return {}, { CONF_GO_BACK: user_input.pop(CONF_GO_BACK), FEATURE_SENSOR_AGGREGATION: user_input }