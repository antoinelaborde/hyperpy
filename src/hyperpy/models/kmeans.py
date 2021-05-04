import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from typing import Tuple, Union, Optional

from hyperpy.spectral import Spectral, as_cube, SpectralCube, SpectralMat
from hyperpy.utils import DataSampler
from hyperpy.utils.visualization import get_custom_cmap


def kmeans(spectral: Spectral, sub_sampling_size: Union[float, int, None] = None, **kwargs) -> Tuple[
    KMeans, SpectralCube]:
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


def kmeans_cube_plot(kmeans: KMeans, kmeans_classes: SpectralCube, colormap_name: str = 'Set1',
                     barycenter_domain: Optional[np.array] = None):
    """
    Plot the score map of kmeans classes and the barycenters.
    :param kmeans: instance of KMeans.
    :param kmeans_classes: instance of SpectralCube class containing the kmeans classes
    :param colormap_name: name of the matplotlib colormap
    :param barycenter_domain: domain array for the barycenters (if None, only a range).
    :return:
    """
    barycenter_domain = barycenter_domain or np.arange(kmeans.cluster_centers_.shape[1])
    unique_classes = np.unique(kmeans_classes.data)
    nbr_unique_classes = len(unique_classes)
    color_map, cmap, norm = get_custom_cmap(colormap_name, nbr_unique_classes)

    fig = plt.figure(figsize=(15, 10))
    axes = fig.subplots(2)
    axes[0].imshow(kmeans_classes.data, cmap=cmap, norm=norm)
    for index, barycenter in enumerate(kmeans.cluster_centers_):
        axes[1].plot(barycenter_domain, barycenter, color=color_map(index), linewidth=3)
    axes[1].set_xlim((barycenter_domain.min(), barycenter_domain.max()))
    axes[1].grid()
    plt.show()
