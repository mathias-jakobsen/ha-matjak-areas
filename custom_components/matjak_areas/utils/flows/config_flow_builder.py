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
CONF_GO_BACK = "go_back"
CONF_TITLE = "title"

# --- Logger -----
LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       ConfigFlowBuilder
#-----------------------------------------------------------#

class ConfigFlowBuilder(FlowBuilder):
    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def add_step(self, step_id: str, config_type: Type[BaseConfig], defaults: dict[str, Any] = {}) -> None:
        async def async_step(user_input: dict[str, Any] = None) -> FlowResult:
            step_list = list(self.configs.keys())
            config = self.configs[step_id]
            errors = {}

            if user_input:
                if user_input.pop(CONF_GO_BACK, False):
                    back_step_function = getattr(self.flow_handler, self.format_step_function_name(step_list[step_list.index(step_id) - 1]))
                    return await back_step_function()

                new_config = config_type(**user_input)
                is_valid, errors = new_config.validate(self.flow_handler.hass)

                if is_valid:
                    self.configs[step_id] = new_config

                    if step_list[-1] == step_id:
                        return self._flow_handler.async_create_entry(title=user_input.get(CONF_TITLE, ""), data=self.config_parser(self.configs))
                    else:
                        return await getattr(self.flow_handler, self.format_step_function_name(step_list[step_list.index(step_id) + 1]))()

            schema = config.get_schema(self.flow_handler.hass)

            if step_list.index(step_id) > 0:
                schema = schema.extend({ vol.Required(CONF_GO_BACK, default=False): bool })

            return self.flow_handler.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

        self.configs[step_id] = config_type(**defaults)
        setattr(self.flow_handler, self.format_step_function_name(step_id), async_step)

