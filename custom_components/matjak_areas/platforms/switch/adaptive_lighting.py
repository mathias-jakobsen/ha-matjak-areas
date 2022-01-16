#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...utils.config import AdaptiveLightingConfig
from ...utils.entity import MA_SwitchEntity


#-----------------------------------------------------------#
#       AdaptiveLightingSwitch
#-----------------------------------------------------------#

class AdaptiveLightingSwitch(MA_SwitchEntity):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __post_init__(self, config: AdaptiveLightingConfig) -> None:
        self._config: AdaptiveLightingConfig = config

        self._max_brightness_pct: int = config.max_brightness_pct
        self._min_brightness_pct: int = config.min_brightness_pct

        self._min_color_temp: int = config.min_color_temp
        self._max_color_temp: int = config.max_color_temp

        self._interval: int = config.interval
        self._transition: int = config.transition

        self._entities: list[str] = config.entities