import numpy as np
import pytest

from hyperpy.spectral import RectangleMask, get_max_rectangle_mask
from hyperpy.exceptions import DataDimensionError, ArrayDimensionError


class TestRectangleMask:
    def test___init__(self):
        rectangle_mask = RectangleMask((5, 5), (1, 3), (2, 4))
        assert rectangle_mask.shape == (5, 5)
        assert rectangle_mask.x_mask == (1, 3)
        assert rectangle_mask.y_mask == (2, 4)

    def test_get_binary_mask(self):
        rectangle_mask = RectangleMask((5, 4), (1, 3), (2, 4))
        mask = rectangle_mask.get_binary_mask()
        test_mask = np.array(
            [
                [False, False, False, False],
                [False, False, True, True],
                [False, False, True, True],
                [False, False, False, False],
                [False, False, False, False],
            ]
        )
        assert np.array_equal(mask, test_mask)

    def test_apply_fail_dim(self):
        rectangle_mask = RectangleMask((5, 4), (1, 3), (2, 4))
        with pytest.raises(DataDimensionError):
            rectangle_mask.apply(np.zeros((1, 1, 1)))

    def test_apply_fail_shape(self):
        rectangle_mask = RectangleMask((5, 4), (1, 3), (2, 4))
        with pytest.raises(ArrayDimensionError):
            rectangle_mask.apply(np.zeros((1, 1)))

    def test_apply_2d(self):
        rectangle_mask = RectangleMask((5, 4), (1, 3), (2, 4))
        input_array = np.array(
            [
                [1, 2, 3, 4],
                [5, 6, 7, 8],
                [9, 10, 11, 12],
                [13, 14, 15, 16],
                [17, 18, 19, 20],
            ]
        )
        output_array = np.array([[7, 8], [11, 12]])
        tested_array = rectangle_mask.apply(input_array)
        assert np.array_equal(tested_array, output_array)

    def test_apply_3d(self):
        rectangle_mask = RectangleMask((5, 4), (1, 3), (2, 4))
        input_array = np.array(
            [
                [[1, 1], [2, 2], [3, 3], [4, 4]],
                [[5, 5], [6, 6], [7, 7], [8, 8]],
                [[9, 9], [10, 10], [11, 11], [12, 12]],
                [[13, 13], [14, 14], [15, 15], [16, 16]],
                [[17, 17], [18, 18], [19, 19], [20, 20]],
            ]
        )
        output_array = np.array([[[7, 7], [8, 8]], [[11, 11], [12, 12]]])
        tested_array = rectangle_mask.apply(input_array)
        assert np.array_equal(tested_array, output_array)


class TestGetMaxRectangleMask:
    def test_get_max_rectangle_mask(self):
        input_mask = np.array(
            [
                [False, False, False, False],
                [False, True, True, True],
                [False, False, True, True],
                [False, False, True, False],
                [False, False, False, False],
            ]
        )
        tested_output_mask = np.array(
            [
                [False, False, False, False],
                [False, True, True, True],
                [False, True, True, True],
                [False, True, True, True],
                [False, False, False, False],
            ]
        )
        rectangle_mask = get_max_rectangle_mask(input_mask)
        test_rectangle_mask = RectangleMask((5, 4), (1, 4), (1, 4))

        mask = rectangle_mask.get_binary_mask()
        test_mask = test_rectangle_mask.get_binary_mask()

        assert np.array_equal(mask, test_mask)
