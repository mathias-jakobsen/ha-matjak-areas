#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN


#-----------------------------------------------------------#
#       Component
#-----------------------------------------------------------#

DOMAIN = "matjak_areas"
PLATFORMS = [BINARY_SENSOR_DOMAIN, SENSOR_DOMAIN]
