import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt

plt.style.use("ggplot")

from matplotlib.path import Path
from matplotlib.patches import Polygon

import numpy as np
import copy


class RectangleMask:
    def __init__(self, array_shape, x_mask, y_mask):
        """
        array_shape: (x, y) shape of the original array.
        x_mask: (x_0, x_f) start and end of the mask.
        y_mask: (y_0, y_f) start and end of the mask.
        """
        self.array_shape = array_shape
        self.x_mask = x_mask
        self.y_mask = y_mask

    def get_binary_mask(self):
        """
        create a binary mask for the original array shape
        """
        self.rectangle_mask = np.zeros(self.array_shape)
        self.rectangle_mask[:] = False
        self.rectangle_mask[
            self.x_mask[0] : self.x_mask[1], self.y_mask[0] : self.y_mask[1]
        ] = True
        return self.rectangle_mask

    def apply(self, array):
        """
        apply the rectangle mask on the array of dim 2 or 3.
        If array is 3-dimensional, dim 1 and 2 are used for mask filtering.

        array: array of dim 2 or 3.
        """
        masked_array = None
        if len(array.shape) == 3:
            masked_array = array[
                self.x_mask[0] : self.x_mask[1], self.y_mask[0] : self.y_mask[1], :
            ]
        elif len(array.shape) == 2:
            masked_array = array[
                self.x_mask[0] : self.x_mask[1], self.y_mask[0] : self.y_mask[1]
            ]
        return masked_array


def rectangle_circ_mask(mask):
    """
    get the circumscribed rectangle of the mask

    mask: numpy array, with booleans.

    rectangle_mask: instance of RectangleMask.
    """
    truepos_x, truepos_y = np.where(mask)
    cut_x0, cut_xf = np.min(truepos_x), np.max(truepos_x) + 1
    cut_y0, cut_yf = np.min(truepos_y), np.max(truepos_y) + 1
    # Prevent from larger boundaries
    cut_x0 = 0 if cut_x0 < 0 else cut_x0
    cut_y0 = 0 if cut_y0 < 0 else cut_y0
    cut_xf = mask.shape[0] - 1 if cut_xf > mask.shape[0] else cut_xf
    cut_yf = mask.shape[1] - 1 if cut_yf > mask.shape[1] else cut_yf
    # Cut the cube with rectangle shape
    rectangle_mask = RectangleMask(mask.shape, (cut_x0, cut_xf), (cut_y0, cut_yf))
    return rectangle_mask


def cube_polygon_roi(image, cmap="Greys", aspect=2):
    """
    matplotlib figure interface to select a polygon region of interest selection

    image: numpy array, with 2 dimensions.
    cmap: str, name of the Matplotlib colormap.
    aspect: int, width/weight ratio. Default: 1.

    binary_roi_mask: numpy array containing binary values.
    """
    image_cropped = copy.deepcopy(image)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(image_cropped, interpolation="nearest", cmap=cmap)
    # Correct ratio aspect
    im = ax.get_images()
    extent = im[0].get_extent()
    ax.set_aspect(abs((extent[1] - extent[0]) / (extent[3] - extent[2])) / aspect)
    # Add mask creator
    mask_creator = MaskCreator(ax)
    plt.show()
    # Get mask
    mask = mask_creator.get_mask(image_cropped.shape)
    # Apply the mask on the image
    image_cropped[~mask] = np.uint8(np.clip(image_cropped[~mask] - 100.0, 0, 255))

    plt.imshow(image_cropped)
    plt.title("Region outside of mask is darkened")
    plt.show()
    plt.close()

    return mask


class MaskCreator(object):
    """An interactive polygon editor.
    Parameters
    ----------
    poly_xy : list of (float, float)
        List of (x, y) coordinates used as vertices of the polygon.
    max_ds : float
        Max pixel distance to count as a vertex hit.
    Key-bindings
    ------------
    't' : toggle vertex markers on and off.  When vertex markers are on,
          you can move them, delete them
    'd' : delete the vertex under point
    'i' : insert a vertex at point.  You must be within max_ds of the
          line connecting two existing vertices

    Source: https://gist.github.com/tonysyu/3090704
    """

    def __init__(self, ax, poly_xy=None, max_ds=10):
        self.showverts = True
        self.max_ds = max_ds
        if poly_xy is None:
            poly_xy = default_vertices(ax)
        self.poly = Polygon(poly_xy, animated=True, fc="y", ec="none", alpha=0.4)

        ax.add_patch(self.poly)
        ax.set_clip_on(False)
        ax.set_title(
            "Click and drag a point to move it; "
            "'i' to insert; 'd' to delete.\n"
            "Close figure when done."
        )
        self.ax = ax

        x, y = zip(*self.poly.xy)
        self.line = plt.Line2D(
            x, y, color="none", marker="o", mfc="r", alpha=0.8, animated=True
        )
        self._update_line()
        self.ax.add_line(self.line)

        self.poly.add_callback(self.poly_changed)
        self._ind = None  # the active vert

        canvas = self.poly.figure.canvas
        canvas.mpl_connect("draw_event", self.draw_callback)
        canvas.mpl_connect("button_press_event", self.button_press_callback)
        canvas.mpl_connect("button_release_event", self.button_release_callback)
        canvas.mpl_connect("key_press_event", self.key_press_callback)
        canvas.mpl_connect("motion_notify_event", self.motion_notify_callback)
        self.canvas = canvas

    def get_mask(self, shape):
        """Return image mask given by mask creator"""
        h, w = shape
        y, x = np.mgrid[:h, :w]
        points = np.transpose((x.ravel(), y.ravel()))
        # mask = matplotlib.path.contains_points(points, self.verts)
        mask = Path(self.verts).contains_points(points)
        # mask = self.verts.contains_points(points)
        return mask.reshape(h, w)

    def poly_changed(self, poly):
        "this method is called whenever the polygon object is called"
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        # Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state

    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def button_press_callback(self, event):
        "whenever a mouse button is pressed"
        ignore = not self.showverts or event.inaxes is None or event.button != 1
        if ignore:
            return
        self._ind = self.get_ind_under_cursor(event)

    def button_release_callback(self, event):
        "whenever a mouse button is released"
        ignore = not self.showverts or event.button != 1
        if ignore:
            return
        self._ind = None

    def key_press_callback(self, event):
        "whenever a key is pressed"
        if not event.inaxes:
            return
        if event.key == "t":
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts:
                self._ind = None
        elif event.key == "d":
            ind = self.get_ind_under_cursor(event)
            if ind is None:
                return
            if ind == 0 or ind == self.last_vert_ind:
                print("Cannot delete root node")
                return
            self.poly.xy = [tup for i, tup in enumerate(self.poly.xy) if i != ind]
            self._update_line()
        elif event.key == "i":
            xys = self.poly.get_transform().transform(self.poly.xy)
            p = event.x, event.y  # cursor coords
            for i in range(len(xys) - 1):
                s0 = xys[i]
                s1 = xys[i + 1]
                d = dist_point_to_segment(p, s0, s1)
                if d <= self.max_ds:
                    self.poly.xy = np.array(
                        list(self.poly.xy[: i + 1])
                        + [(event.xdata, event.ydata)]
                        + list(self.poly.xy[i + 1 :])
                    )
                    self._update_line()
                    break
        self.canvas.draw()

    def motion_notify_callback(self, event):
        ignore = (
            not self.showverts
            or event.inaxes is None
            or event.button != 1
            or self._ind is None
        )
        if ignore:
            return
        x, y = event.xdata, event.ydata

        if self._ind == 0 or self._ind == self.last_vert_ind:
            self.poly.xy[0] = x, y
            self.poly.xy[self.last_vert_ind] = x, y
        else:
            self.poly.xy[self._ind] = x, y
        self._update_line()

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def _update_line(self):
        # save verts because polygon gets deleted when figure is closed
        self.verts = self.poly.xy
        self.last_vert_ind = len(self.poly.xy) - 1
        self.line.set_data(zip(*self.poly.xy))

    def get_ind_under_cursor(self, event):
        "get the index of the vertex under cursor if within max_ds tolerance"
        # display coords
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x) ** 2 + (yt - event.y) ** 2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]
        if d[ind] >= self.max_ds:
            ind = None
        return ind


def default_vertices(ax):
    """Default to rectangle that has a quarter-width/height border."""
    xlims = ax.get_xlim()
    ylims = ax.get_ylim()
    w = np.diff(xlims)
    h = np.diff(ylims)
    x1, x2 = xlims + w // 4 * np.array([1, -1])
    y1, y2 = ylims + h // 4 * np.array([1, -1])
    return ((x1, y1), (x1, y2), (x2, y2), (x2, y1))


def dist(x, y):
    """
    Return the distance between two points.
    """
    d = x - y
    return np.sqrt(np.dot(d, d))


def dist_point_to_segment(p, s0, s1):
    """
    Get the distance of a point to a segment.

      *p*, *s0*, *s1* are *xy* sequences

    This algorithm from
    http://geomalgorithms.com/a02-_lines.html
    """
    p = np.asarray(p, float)
    s0 = np.asarray(s0, float)
    s1 = np.asarray(s1, float)
    v = s1 - s0
    w = p - s0

    c1 = np.dot(w, v)
    if c1 <= 0:
        return dist(p, s0)

    c2 = np.dot(v, v)
    if c2 <= c1:
        return dist(p, s1)

    b = c1 / c2
    pb = s0 + b * v
    return dist(p, pb)
