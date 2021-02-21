from typing import Tuple

import numpy as np

from hyperpy.exceptions import DataDimensionError, ArrayDimensionError


class RectangleMask:
    """
    Numpy array with rectangle mask to be applied on 2d or 3d array.
    """

    def __init__(self, shape: Tuple[int, int], x_mask: Tuple[int, int], y_mask: Tuple[int, int]):
        """
        :param shape: (x_shape, y_shape) for the original array.
        :param x_mask: first and last indexes for the mask on the 0-axis.
        :param y_mask: first and last indexes for the mask on the 1-axis.
        """
        self.shape = shape
        self.x_mask = x_mask
        self.y_mask = y_mask

    def get_binary_mask(self) -> np.array:
        """
        Create a binary mask.
        :return: numpy array with binary mask.
        """
        self.rectangle_mask = np.zeros(self.shape)
        self.rectangle_mask[:] = False
        self.rectangle_mask[self.x_mask[0]: self.x_mask[1], self.y_mask[0]: self.y_mask[1]] = True
        return self.rectangle_mask

    def apply(self, array: np.array) -> np.array:
        """
        Apply the rectangle mask on the array.
        :param array: numpy array to mask.
        :return: masked numpy array.
        """
        if array.shape[:2] != self.shape[:2]:
            raise ArrayDimensionError(array.shape, self.shape)
        if len(array.shape) == 3:
            masked_array = array[
                           self.x_mask[0]: self.x_mask[1], self.y_mask[0]: self.y_mask[1], :
                           ]
        elif len(array.shape) == 2:
            masked_array = array[
                           self.x_mask[0]: self.x_mask[1], self.y_mask[0]: self.y_mask[1]
                           ]
        else:
            raise DataDimensionError(len(array.shape), "2 or 3")
        return masked_array


def get_max_rectangle_mask(mask: np.array) -> RectangleMask:
    """
    Get the largest rectangle mask from the input mask.
    :param mask: original mask to transform.
    :return: RectangleMask instance
    """
    true_pos_x, true_pos_y = np.where(mask)
    cut_x0, cut_xf = np.min(true_pos_x), np.max(true_pos_x) + 1
    cut_y0, cut_yf = np.min(true_pos_y), np.max(true_pos_y) + 1
    # Prevent from larger boundaries
    cut_x0 = 0 if cut_x0 < 0 else cut_x0
    cut_y0 = 0 if cut_y0 < 0 else cut_y0
    cut_xf = mask.shape[0] - 1 if cut_xf > mask.shape[0] else cut_xf
    cut_yf = mask.shape[1] - 1 if cut_yf > mask.shape[1] else cut_yf
    # Cut the cube with rectangle shape
    rectangle_mask = RectangleMask(mask.shape, (cut_x0, cut_xf), (cut_y0, cut_yf))
    return rectangle_mask
