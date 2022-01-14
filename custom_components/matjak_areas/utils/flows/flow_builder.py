#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..config.base_config import BaseConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.data_entry_flow import FlowHandler
from logging import getLogger
from typing import Any, Callable, Type


#-----------------------------------------------------------#
#       Types
#-----------------------------------------------------------#

ConfigParserCallable = Callable[[dict[str, BaseConfig]], dict]


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

# --- Logger -----
LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       FlowBuilder
#-----------------------------------------------------------#

class FlowBuilder:
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, flow_handler: FlowHandler, config_entry: ConfigEntry, config_parser: ConfigParserCallable = None):
        self._configs: dict[str, BaseConfig] = {}
        self._config_entry = config_entry
        self._config_parser: ConfigParserCallable = config_parser or self.process_configs
        self._flow_handler: FlowHandler = flow_handler
        self.__post_init__()


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def configs(self) -> dict[str, BaseConfig]:
        """ Gets the configuration dictionary. """
        return self._configs

    @property
    def config_entry(self) -> ConfigEntry:
        """ Gets the config_entry. """
        return self._config_entry

    @property
    def config_parser(self) -> ConfigParserCallable:
        """ Gets the configuration parser. """
        return self._config_parser

    @property
    def flow_handler(self) -> FlowHandler:
        """ Gets the flow handler. """
        return self._flow_handler


    #--------------------------------------------#
    #       Post Initialization
    #--------------------------------------------#

    def __post_init__(self) -> None:
        """ Triggered right after initialization. Allows subclasses to define instance variables. """
        pass


    #--------------------------------------------#
    #       Step Methods
    #--------------------------------------------#

    def add_step(self, step_id: str, config_type: Type[BaseConfig], defaults: dict[str, Any] = {}) -> None:
        """ Builds and adds a step to the flow handler. """
        raise NotImplementedError

    def remove_step(self, step_id: str) -> None:
        """ Removes a step from the flow handler. """
        raise NotImplementedError


    #--------------------------------------------#
    #       Helper Methods
    #--------------------------------------------#

    def process_configs(self, configs: dict[str, BaseConfig]) -> dict:
        """ Processes the configurations to a dictionary."""
        return { key: value.__dict__ for key, value in configs.items() }

    def format_step_function_name(self, step_id: str) -> str:
        """ Formats the step function name based on the id. """
        return f"async_step_{step_id}"
