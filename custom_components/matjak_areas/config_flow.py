#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import DOMAIN
from .utils.config import AdaptiveLightingConfig, AreaConfig, BaseConfig, BinarySensorAggregationConfig, EntitiesConfig, InitConfig, PresenceConfig, SensorAggregationConfig
from .utils.flows import ConfigFlowBuilder, OptionsFlowBuilder
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from logging import getLogger, Logger


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER: Logger = getLogger(__name__)


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
        self._flow_builder = ConfigFlowBuilder(self, self._parse_configuration)
        self._flow_builder.add_step("user", InitConfig)


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def _parse_configuration(self, configs: dict[str, BaseConfig]) -> dict:
        """ Parses the configuration to a dictionary. """
        return { **configs.pop("user").__dict__ }


#-----------------------------------------------------------#
#       Options Flow
#-----------------------------------------------------------#

class Matjak_OptionsFlow(OptionsFlow):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, config_entry: ConfigEntry):
        self._data = { **config_entry.options }
        self._flow_builder = OptionsFlowBuilder(self, config_entry, self._parse_configuration)
        self._flow_builder.add_step("areas", "Areas", AreaConfig, self._data.get("areas", {}))
        self._flow_builder.add_step("entities", "Entities", EntitiesConfig, **self._data.get("entities", {}))
        self._flow_builder.add_step("presence", "Presence Detection", PresenceConfig, **self._data.get("presence", {}))
        self._flow_builder.add_step("sensor_aggregation", "Sensor Aggregation", SensorAggregationConfig, **self._data.get("sensor_aggregation", {}))
        self._flow_builder.add_step("binary_sensor_aggregation", "Binary Sensor Aggregation", BinarySensorAggregationConfig, **self._data.get("binary_sensor_aggregation", {}))
        self._flow_builder.add_step("adaptive_lighting", "Adaptive Lighting", AdaptiveLightingConfig, **self._data.get("adaptive_lighting", {}))


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def _parse_configuration(self, configs: dict[str, BaseConfig]) -> dict:
        """ Parses the configuration to a dictionary. """
        return { **configs.pop("areas").__dict__, **{ key: value.__dict__ for key, value in configs.items() } }
