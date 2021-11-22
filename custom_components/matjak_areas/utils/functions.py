#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from typing import List


#-----------------------------------------------------------#
#       List Functions
#-----------------------------------------------------------#

def flatten_list(list: List) -> List:
    """ Flattens the provided list. """
    return [item for sublist in list for item in sublist]