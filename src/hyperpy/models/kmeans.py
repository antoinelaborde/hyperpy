from typing import Tuple, Optional, Union

from hyperpy.spectral import SpectralCube, as_cube
from sklearn.cluster import KMeans
import numpy as np

from hyperpy.models.utils import sub_sampling


def kmeans(spectral: SpectralCube, sub_sampling_size: Union[float, int, None] = None, **kwargs) -> Tuple[KMeans, SpectralCube]:
    """
    Performs a k-means clustering.
    :param spectral:
    :param sub_sampling_size: sub sample the data to perform the kmeans fit.
    :param kwargs:
    :return:
    """
    data = spectral.get_matrix()
    k_means = KMeans(**kwargs)

    if sub_sampling_size:
        data_fit = sub_sampling(data, sub_sampling_size)
        k_means.fit_predict(data_fit)
        k_means_predictions = k_means.predict(data)
    else:
        k_means_predictions = k_means.fit_predict(data)

    k_means_cube = as_cube(k_means_predictions, spectral, np.array(['k_means_class']))

    return k_means, k_means_cube



