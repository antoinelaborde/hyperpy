from dataclasses import dataclass
from typing import Optional, Union

import holoviews as hv
import numpy as np
import panel as pn
from holoviews import streams, opts
from sklearn.decomposition import PCA

from hyperpy.spectral import SpectralCube
from hyperpy.models.utils import sub_sampling

hv.extension('bokeh')


@dataclass
class DynamicFigure:

    def __init__(self):
        self.layout = None

    def serve(self):
        """
        Serve the figure
        :return:
        """
        self.server = pn.serve(self.layout)

    def stop(self):
        """
        Stops the server
        :return:
        """
        self.server.stop()


@dataclass
class PCAFigure(DynamicFigure):
    spectral_cube: SpectralCube
    color_map: str = 'viridis'
    image_width: int = 900
    image_height: int = 450
    nbr_components: Optional[int] = None
    sub_sampling_size: Union[float, int, None] = None

    def __post_init__(self):
        """
        :return:
        """
        self._pca_transform()

        (shape_x, shape_y, n_component) = self.scores_cube.shape

        self.ds = hv.Dataset(
            (np.arange(n_component), np.arange(shape_y), np.arange(shape_x), self.scores_cube),
            ['Principal Component', 'x', 'y'], 'Cube')

        im = self.ds.to(hv.Image, ['x', 'y'], dynamic=True)
        self.layout = im.opts(
            opts.Image(cmap=self.color_map, width=self.image_width, height=self.image_height))

    def _pca_transform(self):
        """
        :return:
        """
        map_shape = self.spectral_cube.shape[:2]
        data_matrix = self.spectral_cube.get_matrix()
        n_components = self.nbr_components or min(data_matrix.shape)
        self.pca = PCA(n_components=n_components)

        if self.sub_sampling_size:
            data_fit = sub_sampling(data_matrix, self.sub_sampling_size)
            self.pca.fit_transform(data_fit)
            scores = self.pca.transform(data_matrix)
        else:
            scores = self.pca.fit_transform(data_matrix)
        self.scores_cube = scores.reshape(map_shape + (n_components,))


@dataclass
class BoxROIFigure(DynamicFigure):
    spectral_cube: SpectralCube
    color_map: str = 'viridis'
    image_width: int = 900
    image_height: int = 450
    spectral_axis_name: str = "wavelengths"

    def __post_init__(self):
        """
        :return:
        """
        data = self.spectral_cube.data

        self.ds = hv.Dataset((np.arange(data.shape[2]), np.arange(data.shape[1]), np.arange(data.shape[0]),
                              data), [self.spectral_axis_name, 'x', 'y'], 'Cube')
        # maybe PolyEdit as well
        # polys = hv.Polygons([hv.Box(int(self.image_width / 2), int(self.image_height / 2), int(self.image_height / 2))])
        # self.box_stream = streams.PolyEdit(source=polys)
        polys = hv.Polygons([])
        self.box_stream = streams.BoxEdit(source=polys)

        hlines = hv.HoloMap({i: hv.VLine(i) for i in range(data.shape[2])}, 'wavelengths')
        dmap = hv.DynamicMap(self.roi_curves, streams=[self.box_stream])

        im = self.ds.to(hv.Image, ['x', 'y'], dynamic=True)
        self.layout = (im * polys + dmap * hlines).opts(
            opts.Image(cmap=self.color_map, width=self.image_width, height=self.image_height),
            opts.Curve(width=650, height=450, framewise=True),
            opts.Polygons(fill_alpha=0.2, line_color='white'),
            opts.VLine(color='black'))

    def get_roi(self) -> dict:
        """
        Get ROI coordinates
        :return:
        """
        return self.box_stream.data

    def roi_curves(self, data):
        """
        :param data:
        :return:
        """
        if not data or not any(len(d) for d in data.values()):
            return hv.NdOverlay({0: hv.Curve([], self.spectral_axis_name, 'Reflectance')})

        curves = {}
        data = zip(data['x0'], data['x1'], data['y0'], data['y1'])
        for i, (x0, x1, y0, y1) in enumerate(data):
            selection = self.ds.select(x=(x0, x1), y=(y0, y1))
            curves[i] = hv.Curve(selection.aggregate(self.spectral_axis_name, np.mean))
        return hv.NdOverlay(curves)
