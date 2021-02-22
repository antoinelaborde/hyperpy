import numpy as np
import pytest

from hyperpy.exceptions import ArrayDimensionError
from hyperpy.preprocessing.utils import savitzky_golay, resize_x


class TestSavitzkyGolay:
    def test_savitzky_golay(self):
        data = np.array([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]])

        filters, data_extended = savitzky_golay(data, 3, 0, 0)
        np.testing.assert_almost_equal(filters, np.array([1 / 3, 1 / 3, 1 / 3]))
        np.testing.assert_almost_equal(
            data_extended, np.array([[0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 3, 4, 5, 6]])
        )


class TestResizeX:
    def test_resize_x_fail(self):
        with pytest.raises(ArrayDimensionError):
            resize_x(np.array([[[0], [1], [2]], [[0], [1], [2]]]))

    def test_resize_x_2d(self):
        x = np.array([[0, 1], [2, 3]])
        resized = resize_x(x)
        np.testing.assert_almost_equal(x, resized)

    def test_resize_x_1d(self):
        x = np.array([0, 1, 2, 3])
        resized = resize_x(x)
        np.testing.assert_almost_equal(resized, np.array([[0, 1, 2, 3]]))
