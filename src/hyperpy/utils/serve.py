import os
import pickle
from typing import Any, Union

import pandas as pd
import time
import socket
import signal
import numpy as np


# Utils for serve features
# TODO:
# - Add the figure_script in the bokeh_serve_log
# - Add a function to get the status of all runing server: data/figure_script/host


def create_tmp_dir(tmp_folder_name: str, root_tmp_path: str="/tmp") -> str:
    """
    Create a temporary directory
    :param tmp_folder_name: name of the temporary folder
    :param root_tmp_path: name of the root temporary path
    :return: path the temporary dir
    """
    path = os.path.join(root_tmp_path, tmp_folder_name)
    if not (os.path.isdir(path)):
        os.mkdir(path)
    return path


def save_tmp(data: Any, tmp_filename: str, tmp_path: str) -> str:
    """
    Pickle data in the temporary folder.
    :param data: data to be pickled.
    :param tmp_filename: name of the tmp file.
    :param tmp_path: tmp file path.
    :return: path
    """
    path = os.path.join(tmp_path, tmp_filename)
    if not (os.path.isfile(path)):
        with open(path, "wb") as f:
            pickle.dump(data, f)
    return path


def update_port_use(port: Union[int, float], pid: Union[int, float], look_file_path: str, tmp_path: str):
    """
    Put port use information in a csv file.
    :param port: port number (can be nan for init)
    :param pid: process' PID (can be nan for init)
    :param look_file_path: path to the look file
    :param tmp_path:
    :return:
    """
    # Save a temp file with the port used and their PID
    if os.path.isfile(tmp_path):
        info = {
            "port": port,
            "pid": pid,
            "look_file": look_file_path,
            "time": int(time.time() * 1000.0),
        }
        # Read csv file
        port_use = pd.read_csv(tmp_path)
        # Update it
        port_use = port_use.append(info, ignore_index=True)
        # Save
        port_use.to_csv(tmp_path, index=False)
    else:
        info = {
            "port": [port],
            "pid": [pid],
            "look_file": [look_file_path],
            "time": [int(time.time() * 1000.0)],
        }
        port_use = pd.DataFrame.from_dict(info)
        port_use.to_csv(tmp_path, index=False)


def is_port_in_use(port: int) -> bool:
    """
    Test if the localhost port number is used.
    :param port: port number
    :return: boolean
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def get_port_use(info_file_path: str, port=None) -> dict:
    """
    Get information of port use: port/pid/look_file/time
    :param info_file_path: path to the info file.
    :param port: port number
    :return: dict with info
    """
    if os.path.isfile(info_file_path):
        port_use = pd.read_csv(info_file_path)
    else:
        # Initialize with NaN
        update_port_use(np.nan, np.nan, "", info_file_path)
        port_use = pd.read_csv(info_file_path)
    if port is not None:
        # Filter on port number
        port_use_filter = port_use[port_use.port == port]
        # Get the last in time
        output = port_use_filter.sort_values("time", ascending=False).iloc[0].to_dict()
        return output
    else:
        return port_use.to_dict('list')


def free_port(info_file_path: str, port: int):
    """
    Kill the process linked to the localhost port
    :param info_file_path: path to the info file.
    :param port: port number
    :return:
    """
    info = get_port_use(info_file_path, port)
    os.kill(info["pid"], signal.SIGTERM)
