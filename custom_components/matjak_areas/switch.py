#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import (
    CONF_ENTITIES,
    CONF_INDIVIDUAL_CONTROL,
    CONF_INTERVAL,
    CONF_MAX_BRIGHTNESS_PCT,
    CONF_MAX_COLOR_TEMP,
    CONF_MIN_BRIGHTNESS_PCT,
    CONF_MIN_COLOR_TEMP,
    CONF_TRANSITION,
    DOMAIN,
    Features
)
from .utils.ma_entity import MA_SwitchEntity
from .utils.ma_registry import MA_Registry
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from logging import getLogger
from typing import Any, Callable, TypedDict
import datetime


#-----------------------------------------------------------#
#       Types
#-----------------------------------------------------------#

class AdaptiveLightingConfig(TypedDict):
    enable             : bool
    entities           : list[str]
    transition         : int
    duration           : int
    min_brightness_pct : int
    max_brightness_pct : int
    min_color_temp     : int
    max_color_temp     : int
    individual_control : bool


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       Entry Setup
#-----------------------------------------------------------#

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: Callable) -> bool:
    """ Called when a config entry is being setup.  """
    registry = hass.data[DOMAIN][config_entry.entry_id]
    feature_adaptive_lighting_config = registry.get_feature(Features.ADAPTIVE_LIGHTING)

    if feature_adaptive_lighting_config:
        async_add_entities([create_adaptive_lighting_switch(hass, registry, feature_adaptive_lighting_config)])

    return True


#-----------------------------------------------------------#
#       Switch Setup
#-----------------------------------------------------------#

def create_adaptive_lighting_switch(hass: HomeAssistant, registry: MA_Registry, config: dict[str, Any]) -> Any:
    """ Creates the aggregation sensors. """
    return AdaptiveLightingSwitch(registry, config)


#-----------------------------------------------------------#
#       AdaptiveLightingSwitch
#-----------------------------------------------------------#

class AdaptiveLightingSwitch(MA_SwitchEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, registry: MA_Registry, config: AdaptiveLightingConfig):
        super().__init__(registry)
        self._config_entities   : list[str]      = config.get(CONF_ENTITIES)
        self._registry_entities : list[str]      = []
        self._entities          : list[str]      = []
        self._listeners         : list[Callable] = []

        # --- Brightness ----------
        self._min_brightness_pct : int = config.get(CONF_MIN_BRIGHTNESS_PCT)
        self._max_brightness_pct : int = config.get(CONF_MAX_BRIGHTNESS_PCT)

        # --- Color Temperature ----------
        self._min_color_temp : int = config.get(CONF_MIN_COLOR_TEMP)
        self._max_color_temp : int = config.get(CONF_MAX_COLOR_TEMP)

        # --- Other ----------
        self._individual_control : bool = config.get(CONF_INDIVIDUAL_CONTROL)
        self._interval           : int  = config.get(CONF_INTERVAL)
        self._transition         : int  = config.get(CONF_TRANSITION)


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """ Gets the attributes. """
        return {}

    @property
    def name(self) -> str:
        """ Gets the name. """
        return f"{self._registry.name} Adaptive Lighting"


    #--------------------------------------------#
    #       Methods - Setup / Clean Up
    #--------------------------------------------#

    async def async_clean_up(self) -> None:
        while self._listeners:
            self._listeners.pop()()

    async def async_setup(self, *args: Any) -> None:
        await self.async_clean_up()
        self._registry_entities = self.registry.get_entities(domains=[LIGHT_DOMAIN])
        self._entities = [entity_id for entity_id in self._registry_entities if entity_id in self._config_entities]
        self._listeners.append(async_track_time_interval(self.hass, self.async_on_interval, datetime.timedelta(seconds=self._interval)))
        self._listeners.append(track_manual_control(self.hass, self._registry_entities, self.async_on_manual_control, self.is_context_internal))


    #--------------------------------------------#
    #       Event handlers
    #--------------------------------------------#

    async def async_on_registry_updated(self) -> None:
        await self.async_setup()

    async def async_on_interval(self, *args: Any) -> None:
        """ Triggered when the interval has been reached. """
        pass

    async def async_on_manual_control(self, entity_ids: list[str], context: Context) -> None:
        """ Triggered when manual control is detected. """
        LOGGER.debug(f"Manual control detected: {entity_ids}")

        # off, disable control
        # on, check for changes in