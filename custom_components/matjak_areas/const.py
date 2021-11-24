#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_DOOR,
    DEVICE_CLASS_GAS,
    DEVICE_CLASS_LIGHT,
    DEVICE_CLASS_MOISTURE,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OCCUPANCY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESENCE,
    DEVICE_CLASS_PROBLEM,
    DEVICE_CLASS_SAFETY,
    DEVICE_CLASS_SMOKE,
    DEVICE_CLASS_WINDOW,
)
from homeassistant.components.sensor import (
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_TEMPERATURE
)


#-----------------------------------------------------------#
#       Component
#-----------------------------------------------------------#

DOMAIN = "matjak_areas"
PLATFORMS = []


#-----------------------------------------------------------#
#       Configuration Keys
#-----------------------------------------------------------#

CONF_AREAS = "areas"
CONF_DEVICE_CLASS = "device_class"
CONF_DEVICE_CLASSES = "device_classes"
CONF_ENABLE = "enable"
CONF_ENTITIES = "entities"
CONF_EXCLUDE_ENTITIES = "exclude_entities"
CONF_FEATURES = "features"
CONF_GO_BACK = "go_back"
CONF_INCLUDE_ENTITIES = "include_entities"
CONF_NAME = "name"
CONF_SELECTED_AREAS = "selected_areas"
CONF_STATES_ON = "states_on"


#-----------------------------------------------------------#
#       Features
#-----------------------------------------------------------#

FEATURE_PRESENCE = "Presence"
FEATURE_SENSOR_AGGREGATION = "Sensor Aggregation"
FEATURE_BINARY_SENSOR_AGGREGATION = "Binary Sensor Aggregation"
FEATURES = [FEATURE_PRESENCE, FEATURE_SENSOR_AGGREGATION, FEATURE_BINARY_SENSOR_AGGREGATION]


#-----------------------------------------------------------#
#       Features
#-----------------------------------------------------------#

AGGREGATE_BINARY_SENSOR_CLASSES = [
    DEVICE_CLASS_WINDOW,
    DEVICE_CLASS_DOOR,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_MOISTURE,
    DEVICE_CLASS_LIGHT,
    DEVICE_CLASS_OCCUPANCY
]

AGGREGATE_SENSOR_CLASSES = [
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE
]

AGGREGATE_MODE_SUM = [DEVICE_CLASS_POWER, DEVICE_CLASS_CURRENT, DEVICE_CLASS_ENERGY]
