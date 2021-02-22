from unittest import mock

import numpy as np
import pandas as pd
import signal

from hyperpy.utils.serve import (
    create_tmp_dir,
    save_tmp,
    update_port_use,
    get_port_use,
    free_port,
)


class TestCreateTmpDir:
    @mock.patch("hyperpy.utils.serve.os.path.isdir")
    @mock.patch("hyperpy.utils.serve.os.mkdir")
    def test_create_tmp_dir(self, mock_mkdir, mock_isidr):
        mock_isidr.return_value = False
        create_tmp_dir("name")
        mock_mkdir.assert_called_once_with("/tmp/name")

    @mock.patch("hyperpy.utils.serve.os.path.isdir")
    @mock.patch("hyperpy.utils.serve.os.mkdir")
    def test_create_tmp_dir_exist(self, mock_mkdir, mock_isidr):
        mock_isidr.return_value = True
        path = create_tmp_dir("name")
        mock_mkdir.assert_not_called()
        assert path == "/tmp/name"


class TestSaveTmp:
    @mock.patch("hyperpy.utils.serve.os.path.isfile")
    @mock.patch("hyperpy.utils.serve.pickle.dump")
    def test_save_tmp_exist(self, mock_dump, mock_isfile):
        mock_isfile.return_value = True
        save_tmp(np.array([]), "file", "/tmp")
        mock_dump.assert_not_called()

    @mock.patch("hyperpy.utils.serve.os.path.isfile")
    @mock.patch("hyperpy.utils.serve.pickle.dump")
    def test_save_tmp_exist(self, mock_dump, mock_isfile):
        mock_isfile.return_value = False
        mock_open = mock.mock_open(read_data="")
        with mock.patch("builtins.open", mock_open):
            save_tmp(np.array([]), "file", "/tmp")
            mock_dump.assert_called_once()


class TestUpdatePortUse:
    @mock.patch("hyperpy.utils.serve.pd.read_csv")
    @mock.patch("hyperpy.utils.serve.os.path.isfile")
    def test_update_port_use_existing(self, mock_to_csv, mock_isfile, mock_read_csv):
        mock_isfile.return_value = True
        df = pd.DataFrame(
            {"port": [0], "pid": [1], "look_file": ["file"], "time": [12]}
        )
        mock_read_csv.return_value = df
        update_port_use(42, 42, "new_file", "path")
        # TODO

    @mock.patch("hyperpy.utils.serve.pd.read_csv")
    @mock.patch("hyperpy.utils.serve.os.path.isfile")
    def test_update_port_use_existing(self, mock_isfile, mock_read_csv):
        mock_isfile.return_value = False
        mock_read_csv.return_value = pd.DataFrame(
            {"port": [0], "pid": [1], "look_file": ["file"], "time": [12]}
        )
        update_port_use(42, 42, "new_file", "path")
        # TODO


class TestGetPortUse:
    @mock.patch("hyperpy.utils.serve.os.path.isfile")
    @mock.patch("hyperpy.utils.serve.pd.read_csv")
    def test_get_port_use_none(self, mock_read_csv, mock_isfile):
        mock_isfile.return_value = True
        info_csv = pd.DataFrame(
            {
                "port": [0, 1],
                "pid": [1, 2],
                "look_file": ["file", "file"],
                "time": [12, 13],
            }
        )
        mock_read_csv.return_value = info_csv
        output = get_port_use("csv")
        assert output == {
            "port": [0, 1],
            "pid": [1, 2],
            "look_file": ["file", "file"],
            "time": [12, 13],
        }

    @mock.patch("hyperpy.utils.serve.os.path.isfile")
    @mock.patch("hyperpy.utils.serve.pd.read_csv")
    def test_get_port_use_not_none(self, mock_read_csv, mock_isfile):
        mock_isfile.return_value = True
        info_csv = pd.DataFrame(
            {
                "port": [0, 1],
                "pid": [1, 2],
                "look_file": ["file", "file"],
                "time": [12, 13],
            }
        )
        mock_read_csv.return_value = info_csv
        output = get_port_use("csv", 0)
        assert output == {"port": 0, "pid": 1, "look_file": "file", "time": 12}

    @mock.patch("hyperpy.utils.serve.os.path.isfile")
    @mock.patch("hyperpy.utils.serve.update_port_use")
    @mock.patch("hyperpy.utils.serve.pd.read_csv")
    def test_get_port_use_not_none(
        self, mock_read_csv, mock_update_port_use, mock_isfile
    ):
        mock_isfile.return_value = False
        info_csv = pd.DataFrame(
            {
                "port": [0, 1],
                "pid": [1, 2],
                "look_file": ["file", "file"],
                "time": [12, 13],
            }
        )
        mock_read_csv.return_value = info_csv
        output = get_port_use("csv", 0)
        assert output == {"port": 0, "pid": 1, "look_file": "file", "time": 12}


class TestFreePort:
    @mock.patch("hyperpy.utils.serve.os.kill")
    @mock.patch("hyperpy.utils.serve.get_port_use")
    def test_get_port_use_none(self, mock_port_info, mock_kill):
        mock_port_info.return_value = {"pid": 42}
        free_port("csv", 42)
        mock_port_info.assert_called_once_with("csv", 42)
        mock_kill.assert_called_once_with(42, signal.SIGTERM)
