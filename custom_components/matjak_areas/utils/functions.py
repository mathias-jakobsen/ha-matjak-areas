#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from logging import getLogger


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

LOGGER = getLogger(__name__)


#-----------------------------------------------------------#
#       List Functions
#-----------------------------------------------------------#

def flatten_list(list: list) -> list:
    """ Flattens the provided list. """
    return [item for sublist in list for item in sublist]


#-----------------------------------------------------------#
#       Tracker Functions
#-----------------------------------------------------------#
