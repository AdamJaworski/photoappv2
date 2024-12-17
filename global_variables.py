import numpy as np

# default settings:
DATA_TYPE = np.uint8

# Colors
BACKGROUND_DARK = '#242424'
BACKGROUND_MIDDLE = '#333333'
BACKGROUND_LIGHT = '#3b3b3b'
DARK_BLUE = '#6E8898'
LIGHT_GREY = '#808782'

# workspace variables
IMAGES = []
"""List of open in project images (ImageW)"""
ACTIVE_INDEX = 0
"""Index of currently open ImageW in workspace """
allow_edit_window_open = True
"""Bool that prevents multiple operations to take place on single image """