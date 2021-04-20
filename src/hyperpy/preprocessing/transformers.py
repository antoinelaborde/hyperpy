from copy import deepcopy

import numpy as np
from sklearn.base import TransformerMixin

from hyperpy.preprocessing.utils import savitzky_golay, resize_x

"""
Future implementation:
Baseline removal: http://wiki.eigenvector.com/index.php?title=Wlsbaseline
https://rasmusbro.wixsite.com/chemometricresources/single-post/2020/02/09/Preprocessing-of-chemometric-data

"""

class DomainSelection(TransformerMixin):
    """
    Select a subspace of domain.
    """
    def __init__(self, selection: np.array, domain: np.array):
        self.name = "Domain selection"
        self.short_name = "domain selection"
        self.selection = selection
        self.domain = domain

    def fit(self, X: np.array, y=None):
        return self

    def transform(self, X: np.array) -> np.array:
        self.domain = self.domain[self.selection]
        return X[:, self.selection]

class Log(TransformerMixin):
    """
    Log transformation of the data.
    Y = -log(X)
    """

    def __init__(self):
        self.name = "Logarithmic transformation"
        self.short_name = "Log"

    def fit(self, X: np.array, y=None):
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Apply negative logarithmic transformation log(1/x) or -log(x)
        :param X: numpy array.
        :return: numpy array.
        """
        X_log = -np.log10(X)
        return X_log


class Positive(TransformerMixin):
    """
    Add the minimal value of X if negative.
    Y = X + min(X) if min(X) < 0
    Y = X else
    """

    def __init__(self):
        self.name = "Positive transformation"
        self.short_name = "Pos"

    def fit(self, X: np.array, y=None):
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Add the minimum value of the all matrix X to each row.
        :param X: numpy array.
        :return: numpy array.
        """
        if np.min(X) < 0:
            X_pos = X - np.min(X)
        else:
            X_pos = X
        return X_pos


class StandardNormalVariate(TransformerMixin):
    """
    Standardize the row of the matrix by removing the mean and dividing the standard deviation.
    Y = (X - mean(X)) / std(X)
    Warning: the mean and std are computed row wise.
    """

    def __init__(self):
        self.name = "Standard Normal Variate"
        self.short_name = "SNV"

    def fit(self, X: np.array, y=None):
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Remove the mean and reduce by the standard deviation row wise.
        :param X: numpy array.
        :return: numpy array.
        """
        X_val = deepcopy(X)
        X_val = resize_x(X_val)
        mean = np.tile(np.mean(X_val, axis=1), (X_val.shape[1], 1)).T
        std = np.tile(np.std(X_val, axis=1), (X_val.shape[1], 1)).T
        X_snv = (X_val - mean) / std
        return X_snv


class MeanCentering(TransformerMixin):
    """
    Center the row of the matrix by removing the mean.
    Y = (X - mean(X))
    Warning: the mean is computed row wise.
    """

    def __init__(self):
        self.name = "Mean centering"
        self.short_name = "MR"

    def fit(self, X: np.array, y=None) -> np.array:
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Remove the mean row wise.
        :param X: numpy array.
        :return: numpy array.
        """
        X_val = deepcopy(X)
        X_val = resize_x(X_val)
        mean = np.tile(np.mean(X_val, axis=1), (X_val.shape[1], 1)).T
        X_mean_centering = X_val - mean
        return X_mean_centering


class SavitzkyGolay(TransformerMixin):
    """
    Use a Savitzky Golay filter row wise to derivate and/or smooth the signal in row.
    """

    def __init__(self, window_size=7, polynomial_order=2, derivation_order=1):
        self.name = "Savitzky Golay filter"
        self.short_name = "SG"
        self.window_size = window_size
        self.polynomial_order = polynomial_order
        self.derivation_order = derivation_order

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        filter_, X_extended = savitzky_golay(
            X, self.window_size, self.polynomial_order, self.derivation_order
        )
        X_sg = np.apply_along_axis(np.convolve, 1, X_extended, filter_, mode="valid")
        return X_sg


class MultiplicativeScatterCorrection(TransformerMixin):
    """
    Perform a linear regression between the row of X and a reference spectrum (X_m) and correct the row using the regression coefficients.
    X_i = a_i + b_i X_m
    X_i^msc = (X_i - a_i)/b_i
    """

    def __init__(self):
        self.name = "Multiplicative Scatter Correction"
        self.short_name = "MSC"

    def fit(self, X, y=None):
        """
        Set the reference spectrum
        """
        X_val = resize_x(X)
        if X_val.shape[0] == 1 and y is None:
            raise ValueError(
                "A reference spectrum y must be given for X with only one row."
            )
        if y is None:
            self.reference = np.mean(X, axis=0)
        else:
            if y.shape != (1, X_val.shape[1]):
                raise ValueError(
                    f"The reference must be of shape {(1, X_val.shape[1])} but is ({y.shape})"
                )
            else:
                self.reference = y
        return self

    def transform(self, X):
        X = resize_x(X)
        X_msc = np.zeros_like(X)
        for i in range(X.shape[0]):
            fit = np.polyfit(self.reference, X[i, :], 1, full=True)
            X_msc[i, :] = np.divide((X[i, :] - fit[0][1]), fit[0][0])
        return X_msc


class Normalization(TransformerMixin):
    """
    Normalize each row with 1-norm, 2-norm or inf-norm
    """

    def __init__(self, norm: str = "l1"):
        NORMALIZATION_NORM = ["l1", "l2", "inf"]
        self.name = "Normalization"
        self.short_name = "Norm"
        if norm.lower() not in NORMALIZATION_NORM:
            raise ValueError(
                f"{norm} is an invalid value for norm. Should be among {NORMALIZATION_NORM}"
            )
        self.norm = norm

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_val = resize_x(X)
        if self.norm == "l1":
            norm_matrix = np.tile(
                np.linalg.norm(X_val, ord=1, axis=1, keepdims=True), (1, X_val.shape[1])
            )
        elif self.norm == "l2":
            norm_matrix = np.tile(
                np.linalg.norm(X_val, ord=2, axis=1, keepdims=True), (1, X_val.shape[1])
            )
        elif self.norm == "inf":
            norm_matrix = np.tile(
                np.linalg.norm(X_val, ord=np.inf, axis=1, keepdims=True),
                (1, X_val.shape[1]),
            )
        X_norm = np.divide(X_val, norm_matrix)
        return X_norm
