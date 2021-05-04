from typing import Tuple, Union

from hyperpy.spectral import Spectral, as_cube, SpectralCube, SpectralMat
from sklearn.cluster import KMeans
import numpy as np

from hyperpy.utils import DataSampler

def kmeans(spectral: Spectral, sub_sampling_size: Union[float, int, None] = None, **kwargs) -> Tuple[KMeans, SpectralCube]:
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
        ds = DataSampler(spectral, sub_sampling_size)
        k_means = ds.fit_on(k_means)
        k_means_predictions = k_means.predict(data)
    else:
        k_means_predictions = k_means.fit_predict(data)

    if isinstance(spectral, SpectralCube):
        k_means_classes = as_cube(k_means_predictions, spectral, np.array(['k_means_class']))
    else:
        k_means_classes = SpectralMat(data=k_means_predictions, domain=np.array(['k_means_class']))

    return k_means, k_means_classes

def kmeans_plot(kmeans: KMeans, kmeans_classes: Spectral):
    """

    :param kmeans:
    :param kmeans_classes:
    :return:
    """

    pass



