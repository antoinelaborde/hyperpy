import numpy as np


class RectangleMask:
    def __init__(self, array_shape, x_mask, y_mask):
        """
        array_shape: (x, y) shape of the original array.
        x_mask: (x_0, x_f) start and end of the mask.
        y_mask: (y_0, y_f) start and end of the mask.
        """
        self.array_shape = array_shape
        self.x_mask = x_mask
        self.y_mask = y_mask

    def get_binary_mask(self):
        """
        create a binary mask for the original array shape
        """
        self.rectangle_mask = np.zeros(self.array_shape)
        self.rectangle_mask[:] = False
        self.rectangle_mask[
        self.x_mask[0]: self.x_mask[1], self.y_mask[0]: self.y_mask[1]
        ] = True
        return self.rectangle_mask

    def apply(self, array):
        """
        apply the rectangle mask on the array of dim 2 or 3.
        If array is 3-dimensional, dim 1 and 2 are used for mask filtering.

        array: array of dim 2 or 3.
        """
        masked_array = None
        if len(array.shape) == 3:
            masked_array = array[
                           self.x_mask[0]: self.x_mask[1], self.y_mask[0]: self.y_mask[1], :
                           ]
        elif len(array.shape) == 2:
            masked_array = array[
                           self.x_mask[0]: self.x_mask[1], self.y_mask[0]: self.y_mask[1]
                           ]
        return masked_array


def rectangle_circ_mask(mask):
    """
    get the circumscribed rectangle of the mask

    mask: numpy array, with booleans.

    rectangle_mask: instance of RectangleMask.
    """
    truepos_x, truepos_y = np.where(mask)
    cut_x0, cut_xf = np.min(truepos_x), np.max(truepos_x) + 1
    cut_y0, cut_yf = np.min(truepos_y), np.max(truepos_y) + 1
    # Prevent from larger boundaries
    cut_x0 = 0 if cut_x0 < 0 else cut_x0
    cut_y0 = 0 if cut_y0 < 0 else cut_y0
    cut_xf = mask.shape[0] - 1 if cut_xf > mask.shape[0] else cut_xf
    cut_yf = mask.shape[1] - 1 if cut_yf > mask.shape[1] else cut_yf
    # Cut the cube with rectangle shape
    rectangle_mask = RectangleMask(mask.shape, (cut_x0, cut_xf), (cut_y0, cut_yf))
    return rectangle_mask
