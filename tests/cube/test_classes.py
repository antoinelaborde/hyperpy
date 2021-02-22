from unittest import mock

import numpy as np
import pytest
from mock import Mock

from hyperpy import exceptions
from hyperpy.cube.classes import SpectralCube, as_cube


class TestSpectralCube:
    def test___post_init__(self):
        # Wrong shape
        with pytest.raises(exceptions.DataDimensionError):
            SpectralCube(np.zeros((2, 2)), None)
        # Wrong domain shape
        with pytest.raises(exceptions.DataDimensionError):
            SpectralCube(np.zeros((2, 2, 2)), np.zeros((2, 2, 2)))
        # Wrong domain dimension
        with pytest.raises(exceptions.WrongDomainDimension):
            SpectralCube(np.zeros((2, 2, 3)), np.zeros((4,)))
        cube = SpectralCube(np.zeros((2, 2, 3)), np.zeros((3,)))
        assert cube.shape == (2, 2, 3)

    def test_get_matrix(self):
        test_cube = np.array(
            [
                [[1, 2], [3, 4], [5, 6]],
                [[7, 8], [9, 10], [11, 12]],
                [[13, 14], [15, 16], [17, 18]],
            ]
        )
        expected_mat = np.array(
            [
                [1, 2],
                [3, 4],
                [5, 6],
                [7, 8],
                [9, 10],
                [11, 12],
                [13, 14],
                [15, 16],
                [17, 18],
            ]
        )

        spectral_cube = SpectralCube(data=test_cube, domain=np.array([1, 2]))
        test_mat = spectral_cube.get_matrix()

        np.allclose(expected_mat, test_mat)

    @mock.patch("hyperpy.cube.classes.read_mat_file")
    def test_from_mat_file_without_domain(self, mocked_read_mat):
        test_cube = np.array(
            [
                [[1, 2], [3, 4], [5, 6]],
                [[7, 8], [9, 10], [11, 12]],
                [[13, 14], [15, 16], [17, 18]],
            ]
        )
        test_domain = np.array([1, 2])
        mocked_read_mat.return_value = test_cube

        spectral_cube = SpectralCube.from_mat_file(data_file_name="")

        np.allclose(spectral_cube.data, test_cube)
        np.allclose(spectral_cube.domain, test_domain)

    @mock.patch("hyperpy.cube.classes.read_mat_file")
    def test_from_mat_file_with_domain(self, mocked_read_mat):
        test_cube = np.array(
            [
                [[1, 2], [3, 4], [5, 6]],
                [[7, 8], [9, 10], [11, 12]],
                [[13, 14], [15, 16], [17, 18]],
            ]
        )
        test_domain = np.array([10, 12])
        mocked_read_mat.side_effect = [test_cube, test_domain]

        spectral_cube = SpectralCube.from_mat_file(data_file_name="")

        np.allclose(spectral_cube.data, test_cube)
        np.allclose(spectral_cube.domain, test_domain)

    @mock.patch("hyperpy.cube.classes.read_specim")
    def test_from_specim(self, mocked_read_specim):
        test_cube = np.array(
            [
                [[1, 2], [3, 4], [5, 6]],
                [[7, 8], [9, 10], [11, 12]],
                [[13, 14], [15, 16], [17, 18]],
            ]
        )
        test_domain = np.array([10, 12])
        mocked_read_specim.return_value = [test_cube, test_domain]

        spectral_cube = SpectralCube.from_specim(data_file_name="")

        np.allclose(spectral_cube.data, test_cube)
        np.allclose(spectral_cube.domain, test_domain)

    @mock.patch("hyperpy.cube.classes.read_hyspex")
    def test_from_hyspex(self, mocked_read_hyspex):
        test_cube = np.array(
            [
                [[1, 2], [3, 4], [5, 6]],
                [[7, 8], [9, 10], [11, 12]],
                [[13, 14], [15, 16], [17, 18]],
            ]
        )
        test_domain = np.array([10, 12])
        mocked_read_hyspex.return_value = [test_cube, test_domain]

        spectral_cube = SpectralCube.from_hyspex(data_file_name="", end_white_index=1)

        np.allclose(spectral_cube.data, test_cube)
        np.allclose(spectral_cube.domain, test_domain)


class TestAsCube:
    @mock.patch("hyperpy.cube.classes.SpectralCube.__new__")
    def test_as_cube(self, mocked_spectral_cube_new):
        data = [[1, 2], [3, 4]]
        domain = [1]
        spectral_cube = Mock(spec=SpectralCube, shape=(4, 1))
        as_cube(data, spectral_cube, domain=domain)

        reshaped_array = np.array([[1], [2], [2], [3]])

        assert mocked_spectral_cube_new.called_once_with(
            data=reshaped_array, domain=[1]
        )
