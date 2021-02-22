from typing import Tuple

import numpy as np

from hyperpy import exceptions


def savitzky_golay(
    data: np.array, window_size: int, polynomial_order: int, derivation_order: int = 0
) -> Tuple[np.array, np.array]:
    """
    Compute a Savistky Golay filter to apply row wise and extrapolated data to compensate for filter loss.
    :param data: numpy array containing data in rows.
    :param window_size: size of the filter's window.
    :param polynomial_order: order of the polynomial's filter.
    :param derivation_order: order of the derivation.
    :return: filter, data_extended
    """
    order_range = range(polynomial_order + 1)
    half_window = (window_size - 1) // 2

    # Precompute coefficients
    b = np.mat(
        [[k ** i for i in order_range] for k in range(-half_window, half_window + 1)]
    )
    filter_values = np.linalg.pinv(b).A[derivation_order]

    # pad the signal at the extremes with
    # values taken from the signal itself
    # firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    firstvals = np.tile(data[:, 0], (half_window, 1)).T - np.abs(
        data[:, 1 : half_window + 1][:, ::-1] - np.tile(data[:, 0], (half_window, 1)).T
    )
    # lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    lastvals = np.tile(data[:, -1], (half_window, 1)).T + np.abs(
        data[:, -half_window - 1 : -1][:, ::-1]
        - np.tile(data[:, -1], (half_window, 1)).T
    )
    data_extended = np.concatenate((firstvals, data, lastvals), axis=1)
    return filter_values, data_extended


def resize_x(x: np.array) -> np.array:
    """
    Change the shape of X so that is has two dimensions.
    :param x: numpy array
    :return: numpy array with two dimensions
    """
    if len(x.shape) == 1:
        return np.expand_dims(x, axis=1).T
    elif len(x.shape) == 2:
        return x
    else:
        raise exceptions.ArrayDimensionError(len(x.shape), (1, 2))
