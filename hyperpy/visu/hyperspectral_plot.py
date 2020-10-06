from typing import Union

import matplotlib.pyplot as plt

from hyperpy.cube.classes import SpectralCube


def cube_slice(spectral_cube: SpectralCube, domain_index: int, title: Union[str, None] = None):
    """
    Display a spectral_cube instance at a slice_index.
    :param spectral_cube: SpectralCube instance.
    :param domain_index: index of the domain to display.
    :param title: title of the figure.
    :return:
    """

    domain_value = spectral_cube.domain[domain_index]
    subtitle = f"\n{domain_value}"

    title = title or ""
    title_label = title + subtitle

    figure = plt.figure()
    axes = figure.add_subplot()
    axes.imshow(spectral_cube.data[:, :, domain_index])
    axes.set_title(title_label)
    plt.axis('off')
    plt.show()
