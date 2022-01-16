#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..config.base_config import BaseConfig
from .flow_builder import FlowBuilder
from homeassistant.data_entry_flow import FlowResult
from logging import getLogger
from typing import Any, Type
import voluptuous as vol


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

# --- Configuration Keys -----
CONF_CURRENT_STEP = "current_step"
CONF_NEXT_STEP = "next_step"

# --- Logger -----
LOGGER = getLogger(__name__)

# --- Steps -----
STEP_INIT = "init"
STEP_SAVE = "-- Save & Exit --"


#-----------------------------------------------------------#
#       OptionsFlowBuilder
#-----------------------------------------------------------#

class OptionsFlowBuilder(FlowBuilder):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __post_init__(self) -> None:
        self._step_titles: dict[str, str] = {}


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def add_step(self, step_id: str, step_title: str, config_type: Type[BaseConfig], *args: Any, **kwargs: Any) -> None:
        if step_title in self._step_titles.values():
            raise ValueError(f"Step title must be unique. {step_title} is already in use.")

        async def async_step(user_input: dict[str, Any] = None) -> FlowResult:
            config = self.configs[step_id]
            errors = {}

            if user_input:
                next_step = user_input.pop(CONF_NEXT_STEP)
                config = config_type(**user_input)
                is_valid, errors = config.validate(self.flow_handler.hass)

                if is_valid:
                    self.configs[step_id] = config

                    if next_step == STEP_SAVE:
                        return self.flow_handler.async_create_entry(title="", data=self.config_parser(self.configs))
                    else:
                        next_step = self._get_step_id(next_step)
                        return await getattr(self.flow_handler, self.format_step_function_name(next_step))()

            step_list = list(self._step_titles.values()) + [STEP_SAVE]
            schema = config.get_schema(self.flow_handler.hass, **self._get_schema_kwargs()).extend({ vol.Required(CONF_NEXT_STEP, default=step_list[step_list.index(step_title) + 1]): vol.In(step_list) })

            return self.flow_handler.async_show_form(step_id=self.format_step_id(step_id), data_schema=schema, errors=errors)

        self.configs[step_id] = config_type(*args, **kwargs)
        self._step_titles[step_id] = step_title

        setattr(self.flow_handler, self.format_step_function_name(step_id), async_step)

    def format_step_id(self, step_id: str) -> str:
        """ Formats the step id. """
        if list(self.configs.keys()).index(step_id) == 0:
            return STEP_INIT

        return step_id

    def format_step_function_name(self, step_id: str) -> str:
        return super().format_step_function_name(self.format_step_id(step_id))


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_schema_kwargs(self) -> dict:
        """ Gets the kwargs passed to the schema builders. """
        return {
            "config_entry": self.config_entry,
            "configs": self.configs
        }

    def _get_step_id(self, step_title: str) -> str:
        """ Gets the step title. """
        for key, value in self._step_titles.items():
            if value == step_title:
                return key

        return None

