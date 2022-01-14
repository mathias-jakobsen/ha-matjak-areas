#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .binary_sensor_aggregation_config import BinarySensorAggregationConfig
from .entities_config import EntitiesConfig
from .presence_config import PresenceConfig
from .sensor_aggregation_config import SensorAggregationConfig
from typing import Any, TypedDict


#-----------------------------------------------------------#
#       Types
#-----------------------------------------------------------#

class ConfigEntryOptions(TypedDict):
    areas: list[str]
    entities: dict[str, Any]
    presence: dict[str, Any]
    sensor_aggregation: dict[str, Any]
    binary_sensor_aggregation: dict[str, Any]


#-----------------------------------------------------------#
#       RegistryConfig
#-----------------------------------------------------------#

class RegistryConfig:
    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    areas: list[str]
    binary_sensor_aggregation: BinarySensorAggregationConfig
    entities: EntitiesConfig
    presence: PresenceConfig
    sensor_aggregation: SensorAggregationConfig


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, config: ConfigEntryOptions) -> None:
        """ Triggered after the class has initially been initialized. """
        self.areas = config.get("areas", [])
        self.entities = EntitiesConfig(**config.get("entities", {}))
        self.presence = PresenceConfig(**config.get("presence", {}))
        self.binary_sensor_aggregation = BinarySensorAggregationConfig(**config.get("binary_sensor_aggregation", {}))
        self.sensor_aggregation = SensorAggregationConfig(**config.get("sensor_aggregation", {}))

