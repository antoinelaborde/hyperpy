from unittest import mock
from unittest.mock import MagicMock

import numpy as np

from hyperpy.loading import read_mat_file
from hyperpy.loading.utils import read_raw


class TestReadMatFile:
    @mock.patch('hyperpy.loading.utils.loadmat')
    def test_read_mat_file(self, mocked_loadmat):
        mat_dict = {
            "__header__": None,
            "__version__": None,
            "__globals__": None,
            "data": np.array([1])
        }
        mocked_loadmat.return_value = mat_dict
        output = read_mat_file("")

        np.allclose(output, np.array([1]))

class TestReadRaw:
    @mock.patch('hyperpy.loading.utils.np.fromfile')
    @mock.patch('hyperpy.loading.utils.read_hdr_file')
    @mock.patch('hyperpy.loading.utils.open')
    def test_read_raw(self, mocked_open, mocked_read_hdr, mocked_fromfile):
        mat_dict = {
            "bands": 2,
            "lines": 3,
            "samples": 4,
            "header offset": 0
        }
        mocked_read_hdr.return_value = mat_dict
        mocked_open.return_value = MagicMock()
        mocked_fromfile.return_value = np.arange(24)
        raw_results = np.array([[[ 0, 12],
                                 [ 4, 16],
                                 [ 8, 20]],
                                [[ 1, 13],
                                 [ 5, 17],
                                 [ 9, 21]],
                                [[ 2, 14],
                                 [ 6, 18],
                                 [10, 22]],
                                [[ 3, 15],
                                 [ 7, 19],
                                 [11, 23]]])
        output = read_raw("", "")

        np.allclose(output, raw_results)



