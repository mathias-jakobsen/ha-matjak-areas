#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN, SensorDeviceClass


#-----------------------------------------------------------#
#       Component
#-----------------------------------------------------------#

DOMAIN = "matjak_areas"
EVENT = f"{DOMAIN}_event"
PLATFORMS = [BINARY_SENSOR_DOMAIN, SENSOR_DOMAIN]


#-----------------------------------------------------------#
#       Attribute Keys
#-----------------------------------------------------------#

ATTR_ENTRY_ID = "entry_id"


#-----------------------------------------------------------#
#       Configuration Keys
#-----------------------------------------------------------#

CONF_AREA_ID = "area_id"
CONF_AREAS = "areas"
CONF_AUTO_RELOAD = "auto_reload"
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
    BinarySensorDeviceClass.WINDOW,
    BinarySensorDeviceClass.DOOR,
    BinarySensorDeviceClass.MOTION,
    BinarySensorDeviceClass.MOISTURE,
    BinarySensorDeviceClass.LIGHT,
    BinarySensorDeviceClass.OCCUPANCY
]

AGGREGATE_SENSOR_CLASSES = [
    SensorDeviceClass.CURRENT,
    SensorDeviceClass.ENERGY,
    SensorDeviceClass.HUMIDITY,
    SensorDeviceClass.ILLUMINANCE,
    SensorDeviceClass.POWER,
    SensorDeviceClass.TEMPERATURE
]

AGGREGATE_MODE_SUM = [
    SensorDeviceClass.CURRENT,
    SensorDeviceClass.ENERGY,
    SensorDeviceClass.POWER
]
