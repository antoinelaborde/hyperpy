import os
import pickle
import pandas as pd
import time
import socket
import signal
import numpy as np


# Utils for serve features
# TODO:
# - Add the figure_script in the bokeh_serve_log
# - Add a function to get the status of all runing server: data/figure_script/host


def create_tmp_dir(tmp_folder_name, root_tmp_path="/tmp"):
    """
    create a temporary directory

    tmp_folder_name: str, name of the directory

    path: str, complete path
    """
    path = os.path.join(root_tmp_path, tmp_folder_name)
    if not(os.path.isdir(path)):
        os.mkdir(path)
    return path

def save_tmp(data, name, tmp_path):
    """
    save with pickle data under name in the temporary dir in tmp_path

    data: data to pickle
    name: str, name of the tmp file.
    tmp_path: str, path to the tmp file.

    path: str, path to the tmp file.
    """
    
    path = os.path.join(tmp_path, name)
    if not(os.path.isfile(path)):
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    return path

def update_port_use(port, pid, look_file_path, tmp_path):
    """
    create or update a csv file for port use information

    port: int, number of the port.
    pid: int, PID of the process.
    look_file_path: str, path to the looked file.
    tmp_path: str, tmp path to save the file in.

    """
    # Save a temp file with the port used and their PID
    if os.path.isfile(tmp_path):
        info = {"port": port, 'pid': pid, "look_file": look_file_path, 'time': int(time.time()*1000.0)}
        # Read csv file
        port_use = pd.read_csv(tmp_path)
        # Update it
        port_use = port_use.append(info, ignore_index=True)
        # Save
        port_use.to_csv(tmp_path, index=False)
    else: 
        info = {"port": [port], 'pid': [pid], "look_file": [look_file_path], 'time': [int(time.time()*1000.0)]}
        port_use = pd.DataFrame.from_dict(info)
        port_use.to_csv(tmp_path, index=False)

def is_port_in_use(port):
    """
    check if port is in use

    bool: true if port is used
    """
    #To check if the port is in use 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def get_port_use(info_file_path, port=None):
    """
    get port_use information

    info_file_path: str, path to the file.
    port: int or None, number of the port. If None, returns the complete file.

    return dict info.
    """
    if os.path.isfile(info_file_path):
        port_use = pd.read_csv(info_file_path)
    else:
        # Initialize with NaN
        update_port_use(np.nan, np.nan, '', info_file_path)
        port_use = pd.read_csv(info_file_path)
    if port is not None:
        # Filter on port number
        port_use_filter = port_use[port_use.port==port]
        # Get the last in time
        output = port_use_filter.sort_values('time', ascending=False).iloc[0].to_dict()
        return output
    else:
        return port_use.to_dict()
    
def free_port(info_file, port):
    """
    kill the process linked to the port

    info_file_path: str, path to the port use file.
    port: int, port number.

    """
    info = get_port_use(info_file, port)
    os.kill(info['pid'], signal.SIGTERM)