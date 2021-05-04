import matplotlib
from matplotlib import colors
import numpy as np

def get_custom_cmap(cmap_name: str, cmap_len: int):
    """
    Create a custom discrete matplotlib colormap
    :param cmap_name: name of the matplotlib colormap.
    :param cmap_len: number of discrete sections.
    :return:
    """
    color_map = matplotlib.cm.get_cmap(cmap_name)
    cmap = colors.ListedColormap([color_map(i) for i in range(cmap_len)])
    bounds = np.arange(cmap_len + 1).tolist()
    norm = colors.BoundaryNorm(bounds, cmap.N)
    return color_map, cmap, norm
