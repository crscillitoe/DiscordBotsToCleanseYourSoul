"""
Contains helper functions for processing
images and converting them to emojis
"""
from typing import *
from constants_two import color_dictionary
from KDTreeLib.kdtreelib import KDTree, KDValueMapping

value_mappings = [KDValueMapping(point, color_dictionary[point]) for point in color_dictionary.keys()]
tree = KDTree(num_dimensions=3, point_list=value_mappings)

def convert_pixel_to_emoji(red: int, green: int, blue: int ) -> str:
    """
    Given an RGB value (0-255, 0-255, 0-255),
    returns the emoji closest to this color in the
    dictionary.
    """
    return f'{tree.get_nearest_neighbor((red, green, blue)).value}'

def convert_image_to_string(image):
    to_return = ''
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            red: int   = image[i][j][0]
            green: int = image[i][j][1]
            blue: int  = image[i][j][2]
            to_return += convert_pixel_to_emoji(red, green, blue)
        to_return += '|'

    return to_return