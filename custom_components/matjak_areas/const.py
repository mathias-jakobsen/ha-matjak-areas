#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from homeassistant.backports.enum import StrEnum
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER_DOMAIN
from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN, MediaPlayerDeviceClass
from homeassistant.components.person import DOMAIN as PERSON_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN, SensorDeviceClass


#-----------------------------------------------------------#
#       Component
#-----------------------------------------------------------#

DOMAIN = "matjak_areas"
PLATFORMS = [BINARY_SENSOR_DOMAIN, SENSOR_DOMAIN]


#-----------------------------------------------------------#
#       Configuration Keys
#-----------------------------------------------------------#

CONF_AREA_ID = "area_id"
CONF_AREAS = "areas"
CONF_BINARY_SENSOR_DEVICE_CLASSES = "binary_sensor_device_classes"
CONF_CLEAR_TIMEOUT = "clear_timeout"
CONF_DEVICE_CLASS = "device_class"
CONF_DEVICE_CLASSES = "device_classes"
CONF_DOMAINS = "domains"
CONF_ENABLE = "enable"
CONF_ENTITIES = "entities"
CONF_EXCLUDE_ENTITIES = "exclude_entities"
CONF_FEATURES = "features"
CONF_GO_BACK = "go_back"
CONF_INCLUDE_ENTITIES = "include_entities"
CONF_MEDIA_PLAYER_DEVICE_CLASSES = "media_player_device_classes"
CONF_NAME = "name"
CONF_STATES_ON = "states_on"


#-----------------------------------------------------------#
#       Config/Options Flow
#-----------------------------------------------------------#

DEFAULT_CLEAR_TIMEOUT = 60
DEFAULT_PRESENCE_DOMAINS = [BINARY_SENSOR_DOMAIN]
DEFAULT_PRESENCE_BINARY_SENSOR_DEVICE_CLASSES = [BinarySensorDeviceClass.MOTION, BinarySensorDeviceClass.OCCUPANCY]
DEFAULT_PRESENCE_MEDIA_PLAYER_DEVICE_CLASSES = [MediaPlayerDeviceClass.TV]
DEFAULT_STATES_ON = ["on", "playing", "home", "open"]


#-----------------------------------------------------------#
#       Features
#-----------------------------------------------------------#

class Features(StrEnum):
    PRESENCE = "Presence"
    BINARY_SENSOR_AGGREGATION = "Binary Sensor Aggregation"
    SENSOR_AGGREGATION = "Sensor Aggregation"


#-----------------------------------------------------------#
#       Presence Domains
#-----------------------------------------------------------#

PRESENCE_DOMAINS = [
    BINARY_SENSOR_DOMAIN,
    DEVICE_TRACKER_DOMAIN,
    MEDIA_PLAYER_DOMAIN,
    PERSON_DOMAIN
]


#-----------------------------------------------------------#
#       Aggregate Device Classes
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
