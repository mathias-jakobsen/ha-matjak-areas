#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import (
    CONF_GO_BACK,
    CONF_NAME
)
from homeassistant.data_entry_flow import FlowHandler, FlowResult
from logging import getLogger
from typing import Any, Callable, Dict, List, Tuple
import voluptuous as vol


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       FlowBuilder
#-----------------------------------------------------------#

class FlowBuilder:
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, flow_handler: FlowHandler, data: Dict[str, Any] = {}):
        self._data         : Dict[str, Any] = data
        self._flow_handler : FlowHandler    = flow_handler
        self._steps        : List[str]      = []


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def add_step(self, step_id: str, schema_builder: Callable[[Dict[str, Any]], vol.Schema], validator: Callable[[Dict[str, Any]], Tuple[Dict[str, str], Dict[str, Any]]] = None, next_step: str = None) -> None:
        """ Adds a step. """
        async def async_step(user_input: Dict[str, Any] = None) -> FlowResult:
            errors = {}

            if user_input:
                if validator:
                    errors, user_input = validator(user_input)
                    self._data = { **self._data, **user_input }

                if user_input.pop(CONF_GO_BACK, False):
                    back_step_function = getattr(self._flow_handler, f"async_step_{self._steps[self._steps.index(step_id) - 1]}")
                    return await back_step_function()

                if len(errors) == 0:
                    if next_step is not None:
                        next_step_function = getattr(self._flow_handler, f"async_step_{next_step}")
                        return await next_step_function()
                    else:
                        return self._flow_handler.async_create_entry(title=self._data.get(CONF_NAME, ""), data=self._data)

            schema = schema_builder(self._data)

            if self._steps.index(step_id) > 0:
                schema = schema.extend({ vol.Required(CONF_GO_BACK, default=False): bool })

            return self._flow_handler.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

        if step_id not in self._steps:
            self._steps.append(step_id)

        setattr(self._flow_handler, f"async_step_{step_id}", async_step)

    def remove_step(self, step_id: str) -> None:
        """ Removes a step. """
        if step_id not in self._steps:
            return

        self._steps.remove(step_id)
        delattr(self._flow_handler, f"async_step_{step_id}")
