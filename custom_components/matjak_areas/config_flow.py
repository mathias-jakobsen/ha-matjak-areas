#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import (
    DOMAIN,
    CONF_AREAS,
    CONF_DEVICE_CLASSES,
    CONF_ENABLE,
    CONF_ENTITIES,
    CONF_EXCLUDE_ENTITIES,
    CONF_GO_BACK,
    CONF_INCLUDE_ENTITIES,
    CONF_NAME,
    CONF_SELECTED_AREAS,
    CONF_STATES_ON,
    FEATURE_PRESENCE,
    FEATURE_SENSOR_AGGREGATION
)
from .utils.functions import flatten_list
from homeassistant.components.sensor import DEVICE_CLASSES
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry, config_validation as cv, entity_registry
from homeassistant.helpers.template import area_entities
from typing import Any, Dict, List, Union
import voluptuous as vol


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

# ------ Errors --------------
ERROR_AREA_REQUIRED = "area_required"
ERROR_NAME_REQUIRED = "name_required"

# ------ Steps ---------------
STEP_INIT = "init"
STEP_PRESENCE = "presence"
STEP_SENSOR_AGGREGATION = "sensor_aggregation"
STEP_USER = "user"


#-----------------------------------------------------------#
#       Steps
#-----------------------------------------------------------#

class Matjak_ConfigFlow_Steps:
    @staticmethod
    def init(hass: HomeAssistant, data: Dict[str, Any] = {}) -> vol.Schema:
        areas = area_registry.async_get(hass).async_list_areas()
        area_names = [area.name for area in areas]

        return vol.Schema({
            vol.Optional(CONF_NAME, default=data.get(CONF_NAME, "")): str,
            vol.Required(CONF_AREAS, default=data.get(CONF_AREAS, [])): cv.multi_select(area_names)
        })

class Matjak_OptionsFlow_Steps:
    @staticmethod
    def init(hass: HomeAssistant, data: Dict[str, Any] = {}) -> vol.Schema:
        selected_exclude_entity_ids = data.get(CONF_EXCLUDE_ENTITIES, [])
        selected_include_entity_ids = data.get(CONF_INCLUDE_ENTITIES, [])

        area_entity_ids = sorted(flatten_list([area_entities(hass, area) for area in data.get(CONF_AREAS, [])]))
        all_entity_ids = sorted([entity_id for entity_id in hass.states.async_entity_ids() if entity_id not in area_entity_ids])

        exclude_entity_ids = selected_exclude_entity_ids + [entity_id for entity_id in area_entity_ids if entity_id not in selected_exclude_entity_ids]
        include_entity_ids = selected_include_entity_ids + [entity_id for entity_id in all_entity_ids if entity_id not in selected_include_entity_ids]

        return vol.Schema({
            vol.Required(CONF_SELECTED_AREAS): ", ".join(data.get(CONF_AREAS, [])),
            vol.Required(CONF_EXCLUDE_ENTITIES, default=selected_exclude_entity_ids): cv.multi_select(exclude_entity_ids),
            vol.Required(CONF_INCLUDE_ENTITIES, default=selected_include_entity_ids): cv.multi_select(include_entity_ids)
        })

    @staticmethod
    def presence(hass: HomeAssistant, data: Dict[str, Any] = {}) -> vol.Schema:
        feature_data = data.get(FEATURE_PRESENCE, {})
        excluded_entity_ids = data.get(CONF_EXCLUDE_ENTITIES, [])
        selected_entity_ids = [entity_id for entity_id in feature_data.get(CONF_ENTITIES, []) if entity_id not in excluded_entity_ids]
        selected_include_entity_ids = data.get(CONF_INCLUDE_ENTITIES, [])
        area_entity_ids = sorted(flatten_list([area_entities(hass, area) for area in data.get(CONF_AREAS, [])]))
        filtered_area_entity_ids = [entity_id for entity_id in area_entity_ids if entity_id not in excluded_entity_ids]
        entity_ids = selected_entity_ids + [entity_id for entity_id in filtered_area_entity_ids + selected_include_entity_ids if entity_id not in selected_entity_ids]

        return vol.Schema({
            vol.Required(CONF_ENABLE, default=feature_data.get(CONF_ENABLE, False)): bool,
            vol.Required(CONF_ENTITIES, default=selected_entity_ids): cv.multi_select(entity_ids),
            vol.Required(CONF_STATES_ON, default=", ".join(feature_data.get(CONF_STATES_ON, []))): str,
            vol.Required(CONF_GO_BACK, default=False): bool
        })

    @staticmethod
    def sensor_aggregation(hass: HomeAssistant, data: Dict[str, Any] = {}) -> vol.Schema:
        feature_data = data.get(FEATURE_SENSOR_AGGREGATION, {})
        selected_device_classes = feature_data.get(CONF_DEVICE_CLASSES, [])
        device_classes = selected_device_classes + [device_class for device_class in DEVICE_CLASSES if device_class not in selected_device_classes]

        return vol.Schema({
            vol.Required(CONF_ENABLE, default=feature_data.get(CONF_ENABLE, False)): bool,
            vol.Required(CONF_DEVICE_CLASSES, default=selected_device_classes): cv.multi_select(device_classes),
            vol.Required(CONF_GO_BACK, default=False): bool
        })


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
    #       Methods
    #--------------------------------------------#

    async def async_step_user(self, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """ The user step of the flow. """
        errors = {}

        if user_input is not None:
            if len(user_input[CONF_AREAS]) == 0:
                errors[CONF_AREAS] = ERROR_AREA_REQUIRED

            if len(user_input[CONF_AREAS]) > 1 and not user_input[CONF_NAME]:
                errors[CONF_NAME] = ERROR_NAME_REQUIRED

            if len(errors) == 0:
                if not user_input[CONF_NAME]:
                    user_input[CONF_NAME] = user_input[CONF_AREAS][0]

                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        schema = Matjak_ConfigFlow_Steps.init(self.hass, user_input or {})
        return self.async_show_form(step_id=STEP_USER, data_schema=schema, errors=errors)


#-----------------------------------------------------------#
#       Options Flow
#-----------------------------------------------------------#

class Matjak_OptionsFlow(OptionsFlow):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, config_entry: ConfigEntry):
        self._config_entry = config_entry
        self._data = { **config_entry.data, **config_entry.options }


    #--------------------------------------------#
    #       Steps - Init
    #--------------------------------------------#

    async def async_step_init(self, user_input: Union[Dict[str, Any], None] = None) -> Dict[str, Any]:
        """ The init step of the flow. """
        if user_input is not None:
            user_input.pop(CONF_SELECTED_AREAS)
            self._data.update(user_input)
            return await self.async_step_presence()

        schema = Matjak_OptionsFlow_Steps.init(self.hass, self._data)
        return self.async_show_form(step_id=STEP_INIT, data_schema=schema)

    async def async_step_presence(self, user_input: Union[Dict[str, Any], None] = None) -> Dict[str, Any]:
        """ The presence step of the flow. """
        if user_input is not None:
            go_back = user_input.pop(CONF_GO_BACK)
            user_input[CONF_STATES_ON] = cv.ensure_list_csv(user_input[CONF_STATES_ON])
            self._data.setdefault(FEATURE_PRESENCE, {}).update(user_input)

            if go_back:
                return await self.async_step_init()

            return await self.async_step_sensor_aggregation()

        schema = Matjak_OptionsFlow_Steps.presence(self.hass, self._data)
        return self.async_show_form(step_id=STEP_PRESENCE, data_schema=schema)

    async def async_step_sensor_aggregation(self, user_input: Union[Dict[str, Any], None] = None) -> Dict[str, Any]:
        """ The sensor aggregation step of the flow. """
        if user_input is not None:
            go_back = user_input.pop(CONF_GO_BACK)
            self._data.setdefault(FEATURE_SENSOR_AGGREGATION, {}).update(user_input)

            if go_back:
                return await self.async_step_presence()

            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)

        schema = Matjak_OptionsFlow_Steps.sensor_aggregation(self.hass, self._data)
        return self.async_show_form(step_id=STEP_SENSOR_AGGREGATION, data_schema=schema)