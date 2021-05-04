from sklearn.base import TransformerMixin
from typing import Union, Optional

import numpy as np
from hyperpy.spectral import Spectral, SpectralMat, SpectralCube
from sklearn.utils import resample

class DataSampler:
    """
    DataSampler provides an object to subsample
    """
    def __init__(self, spectral: Spectral, size: Union[float, int], random_state: Optional[float] = None):
        """
        Take a spectral structure
        """
        self.spectral = spectral
        if isinstance(spectral, SpectralMat):
            self.n_sample = self.spectral.data.shape[0]
        elif isinstance(spectral, SpectralCube):
            self.n_sample = self.spectral.data.shape[0]*self.spectral.data.shape[0]

        if isinstance(size, float) and 0 < size <= 1:
            self.shape = int(np.ceil(self.n_sample * size))
        elif isinstance(size, int) and size > 0:
            self.shape = size
        else:
            raise ValueError

        self.random_state = random_state

    def sample(self) -> np.array:
        """
        provide a sampling with sklearn resample, manage the seed,
        :return:
        """

        if not(hasattr(self, 'data')):
            self.data = self.spectral.get_matrix()
        return resample(self.data, n_samples=self.shape, replace=False, random_state=self.random_state)

    def fit_on(self, predictor: TransformerMixin):
        """
        :return:
        """
        predictor.fit(self.sample())
        return predictor