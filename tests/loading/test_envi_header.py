from unittest import mock

from hyperpy.loading.envi_header import find_hdr_file
import pytest


class TestFindHdrFile:
    @mock.patch("hyperpy.loading.envi_header.os.path.isfile")
    def test_find_hdr_file_fail(self, mock_isfile):
        mock_isfile.return_value = False
        with pytest.raises(IOError):
            find_hdr_file("")

    @mock.patch("hyperpy.loading.envi_header.os.path.isfile")
    def test_find_hdr_file_file_base(self, mock_isfile):
        mock_isfile.return_value = [True, True]
        raw_file_name = "/dir1/dir2/file.raw"
        hdr_file_name = find_hdr_file(raw_file_name)
        assert hdr_file_name == "/dir1/dir2/file.hdr"

    @mock.patch("hyperpy.loading.envi_header.os.path.isfile")
    def test_find_hdr_file_file_name(self, mock_isfile):
        mock_isfile.return_value = [True, True]
        raw_file_name = "/dir1/dir2/file"
        hdr_file_name = find_hdr_file(raw_file_name)
        assert hdr_file_name == "/dir1/dir2/file.hdr"
