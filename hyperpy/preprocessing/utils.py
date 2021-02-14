import numpy as np
from hyperpy import exceptions


def savitzky_golay(y, window_size, polynomial_order, derivation_order=0):
    """
    Compute a Savitzky Golay filter
    y: numpy array, signal to process.
    window_size: int, must be odd, size of the window for the polynomial fitting.
    polynomial_order: int, must be higher than derivate_order, order of the polynomial fitting.
    derivate_order: int, order of the derivation.

    m: filter to apply row wise.
    y: y with extra values to compensate for the filter lost.
    """
    order_range = range(polynomial_order + 1)
    half_window = (window_size - 1) // 2

    # Precompute coefficients
    b = np.mat(
        [[k ** i for i in order_range] for k in range(-half_window, half_window + 1)]
    )
    m = np.linalg.pinv(b).A[derivation_order]

    # pad the signal at the extremes with
    # values taken from the signal itself
    # firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])

    firstvals = np.tile(y[:, 0], (half_window, 1)).T - np.abs(
        y[:, 1 : half_window + 1][:, ::-1] - np.tile(y[:, 0], (half_window, 1)).T
    )

    # lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    lastvals = np.tile(y[:, -1], (half_window, 1)).T + np.abs(
        y[:, -half_window - 1 : -1][:, ::-1] - np.tile(y[:, -1], (half_window, 1)).T
    )

    y = np.concatenate((firstvals, y, lastvals), axis=1)
    return m, y


def resize_x(X):
    """
    Change the shape of X so that it has two dimensions.
    X: numpy array.
    """
    if len(X.shape) == 1:
        return np.expand_dims(X, axis=1).T
    elif len(X.shape) == 2:
        return X
    else:
        raise exceptions.ArrayDimensionError(len(X.shape), (1, 2))
