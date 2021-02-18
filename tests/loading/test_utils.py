from unittest import mock
from unittest.mock import MagicMock

import numpy as np

from hyperpy import read_mat_file
from hyperpy.loading.utils import (
    read_raw,
    read_specim,
    get_reflectance,
    add_prefix_filename,
    expand_average,
    read_hyspex,
    get_wavelength,
)


class TestReadMatFile:
    @mock.patch("hyperpy.loading.utils.loadmat")
    def test_read_mat_file(self, mocked_loadmat):
        mat_dict = {
            "__header__": None,
            "__version__": None,
            "__globals__": None,
            "data": np.array([1]),
        }
        mocked_loadmat.return_value = mat_dict
        output = read_mat_file("")

        np.allclose(output, np.array([1]))


class TestReadRaw:
    @mock.patch("hyperpy.loading.utils.np.fromfile")
    @mock.patch("hyperpy.loading.utils.read_hdr_file")
    @mock.patch("hyperpy.loading.utils.open")
    def test_read_raw(self, mocked_open, mocked_read_hdr, mocked_fromfile):
        mat_dict = {"bands": 2, "lines": 3, "samples": 4, "header offset": 0}
        mocked_read_hdr.return_value = mat_dict
        mocked_open.return_value = MagicMock()
        mocked_fromfile.return_value = np.arange(24)
        raw_results = np.array(
            [
                [[0, 12], [4, 16], [8, 20]],
                [[1, 13], [5, 17], [9, 21]],
                [[2, 14], [6, 18], [10, 22]],
                [[3, 15], [7, 19], [11, 23]],
            ]
        )
        output = read_raw("", "")

        np.allclose(output, raw_results)


class TestReadSpecim:
    @mock.patch("hyperpy.loading.utils.get_wavelength")
    @mock.patch("hyperpy.loading.utils.get_reflectance")
    @mock.patch("hyperpy.loading.utils.expand_average")
    @mock.patch("hyperpy.loading.utils.read_raw")
    def test_read_specim(
        self,
        mocked_read_raw,
        mocked_expand_average,
        mocked_get_reflectance,
        mocked_get_wavelengths,
    ):
        mocked_raw = MagicMock(shape=[15, 10])
        mocked_white_ref = MagicMock()
        mocked_black_ref = MagicMock()
        mocked_read_raw.side_effect = [mocked_raw, mocked_white_ref, mocked_black_ref]

        mocked_reflectance = MagicMock()
        mocked_get_reflectance.return_value = mocked_reflectance
        mocked_wavelength = MagicMock()
        mocked_get_wavelengths.return_value = mocked_wavelength

        reflectance, wavelengths = read_specim("filename")

        mocked_read_raw.assert_has_calls(
            [
                mock.call("filename"),
                mock.call("WHITEREF_filename"),
                mock.call("DARKREF_filename"),
            ]
        )

        mocked_expand_average.assert_has_calls(
            [mock.call(mocked_white_ref, 10), mock.call(mocked_black_ref, 10)]
        )

        mocked_get_reflectance.assert_called_once()
        mocked_get_wavelengths.assert_called_once_with("filename")

        assert reflectance == mocked_reflectance
        assert wavelengths == mocked_wavelength


class TestGetReflectance:
    def test_get_reflectance(self):
        raw = np.arange(10, 20)
        white = np.arange(10)
        white_ref = np.arange(10)
        white_ref[white_ref == 0.0] = 1e-9
        reflectance = np.divide(raw, white_ref)
        tested_reflectance = get_reflectance(raw, white)

        np.allclose(reflectance, tested_reflectance)


class TestAddPrefixFilename:
    def test_add_prefix_filename(self):
        path = "/path/filename"
        prefix = "prefix_"
        path_prefix = "/path/prefix_filename"
        tested_path_prefix = add_prefix_filename(path, prefix)
        assert path_prefix == tested_path_prefix


class TestExpandAverage:
    def test_expand_average(self):
        raw_results = np.array(
            [
                [[0, 12], [4, 16], [8, 20]],
                [[1, 13], [5, 17], [9, 21]],
                [[2, 14], [6, 18], [10, 22]],
                [[3, 15], [7, 19], [11, 23]],
            ]
        )

        average_expanded = np.array(
            [
                [[4.0, 16.0], [4.0, 16.0]],
                [[5.0, 17.0], [5.0, 17.0]],
                [[6.0, 18.0], [6.0, 18.0]],
                [[7.0, 19.0], [7.0, 19.0]],
            ]
        )

        test_average_expanded = expand_average(raw_results, 2)
        np.allclose(average_expanded, test_average_expanded)

    class TestReadHyspex:
        @mock.patch("hyperpy.loading.utils.expand_average")
        @mock.patch("hyperpy.loading.utils.get_wavelength")
        @mock.patch("hyperpy.loading.utils.get_reflectance")
        @mock.patch("hyperpy.loading.utils.read_raw")
        def test_read_hyspex(
            self,
            mock_read_raw,
            mock_get_reflectance,
            mock_get_wavelength,
            mock_expand_average,
        ):
            mocked_raw = MagicMock(shape=[15, 10])
            mock_read_raw.return_value = mocked_raw

            white_average_expand = MagicMock()

            mock_expand_average.return_value = white_average_expand

            read_hyspex("filename", 2, 5)

            mock_expand_average.assert_has_calls(
                [
                    mock.call(mocked_raw[:, 2:5, :], 10),
                ]
            )
            mock_get_reflectance.assert_has_calls(
                [mock.call(mocked_raw, white_average_expand)]
            )

            mock_get_wavelength.assert_has_calls([mock.call("filename")])

    class TestGetWavelength:
        @mock.patch("hyperpy.loading.utils.read_hdr_file")
        @mock.patch("hyperpy.loading.utils.find_hdr_file")
        def test_get_wavelength(self, mocked_find_hdr, mocked_read_hdr_file):
            hdr_file = {"wavelength": "42"}
            mocked_find_hdr.return_value = "hdr_file"
            mocked_read_hdr_file.return_value = hdr_file
            test_wavelength = get_wavelength("filename")
            assert test_wavelength == np.array([42])
