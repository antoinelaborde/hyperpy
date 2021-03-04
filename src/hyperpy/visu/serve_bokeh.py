import os
import signal
import time
import subprocess
import sys
import webbrowser
from typing import Any, Optional

from hyperpy.utils import serve
from hyperpy.visu import utils

## TO DO:
# Make the function serve a class.
# Methods: open a new port. Connect to it. Close the port. (Close port when instance deleted ? )
# Attibute: path to data. Port number. Figure script.
# Write a readme.




class FigureServer:
    """
    A class that groups Figure served with Bokeh.
    """
    def __init__(self):
        self.figure_list = []

    def append(self, figure):
        self.figure_list.append(
            figure
        )

    def remove(self, figure):
        """
        Remove the figure from the server list
        :param figure:
        :return:
        """
        for figure_server in self.figure_list:
            if figure_server.id == figure.id:
                self.figure_list.remove(figure_server)

    def close_all(self):
        """
        Close all figures
        :return:
        """
        for figure in self.figure_list:
            os.kill(figure.sub_process.pid, signal.SIGTERM)


class HyperFig:
    def __init__(self, server: FigureServer, figure_script: str, data: Any, local_host_port: int=8080):
        # Comment: maybe problematic to do all of this in the init, should be done in a .compile() method ?

        self.server = server
        # Choose a free port for Bokeh serve
        self.local_host_port = self._choose_port(local_host_port)
        # Find the figure script
        self.figure_script = figure_script
        self.figure_name = os.path.split(self.figure_script)[1].replace(".py", "")
        # Create a tmp directory bokeh
        self.tmp_path = serve.create_tmp_dir("bokeh")
        # Set the data
        self.set_data(data)
        # Serve log file path
        self.log_serve_file = os.path.join(self.tmp_path, "bokeh_serve_log.csv")
        # Make ID
        self.id = f"{self.figure_name}-{self.data_filename}"

    def set_data(self, data: Any):
        """
        Set the data attribute and save the data in bokeh tmp folder
        :param data:
        :return:
        """
        self.data = data
        self.data_filename = str(hash(str(self.data)) % ((sys.maxsize + 1) * 2))
        self.data_path = serve.save_tmp(self.data, self.data_filename, self.tmp_path)

    def _check_port_in_use(self, port: Optional[int]) -> bool:
        """
        Check if port is in used
        :param port: port number (optional)
        :return:
        """
        port = port or self.local_host_port
        return serve.is_port_in_use(port)

    def _choose_port(self, port: int) -> int:
        """
        Check if the current port is in used and change it if needed.
        :param port: port number
        :return:
        """
        while self._check_port_in_use(port):
            port += 1
        return port

    def _set_command_line(self):
        """
        Set the command line for the subprocess
        :return:
        """
        self.command_line = [
            "bokeh",
            "serve",
            self.figure_script,
            "--port",
            str(self.local_host_port),
            "--args",
            self.data_path,
        ]

    def _check_already_served(self) -> bool:
        """
        Returns True if the figure id is already served.
        :return:
        """
        for figure in self.server.figure_list:
            if figure.id == self.id:
                return True
        return False

    def serve(self):
        """
        Launch the subprocess
        :return:
        """
        if not(self._check_already_served()):
            self._set_command_line()
            sub_process = subprocess.Popen(
                self.command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            self.sub_process = sub_process
            self.add_to_server()
        else:
            print(f"{self.id} is not served because the server already serves it.")

    def add_to_server(self):
        """
        Add the figure to the server list
        :return:
        """
        self.server.append(self)

    def open(self):
        """
        Open the web browser with the figure
        :return:
        """
        webbrowser.open_new(f"http://localhost:{self.local_host_port}/{self.figure_name}")

    def close(self):
        """
        Kill the subprocess
        :return:
        """
        os.kill(self.sub_process.pid, signal.SIGTERM)
        self.server.remove(self)

    def serve_open(self):
        """
        Serve and open the browser
        :return:
        """
        self.serve()
        time.sleep(1)
        self.open()







def serve_bokeh_figure(data, script_path, port=8080, max_server=10):
    """
    serve a bokeh figure based on figure_script using the data

    data: data to be pickle
    script_path: str, complete path to the figure script
    port: int, first port to test for connexion
    max_server: int, max number of port to test.

    """
    figure_script = os.path.split(script_path)[1]
    figure_script = figure_script.replace(".py", "")
    # Create local temporary directory
    tmp_path = serve.create_tmp_dir("bokeh")
    # Temp file for bokeh serve
    serve_file_path = os.path.join(tmp_path, "bokeh_serve_log.csv")
    # Get a hash from data data
    filename = str(hash(str(data)))
    # Save the data in the temporary dir
    data_path = serve.save_tmp(data, filename, tmp_path)
    print(data_path)
    # Command line to serve bokeh and give the tmp path for the data
    command_line = [
        "bokeh",
        "serve",
        script_path,
        "--port",
        str(port),
        "--args",
        data_path,
    ]

    # Test if the current port is running
    port_used = serve.is_port_in_use(port)
    # If the default port is unussed
    if not (port_used):
        print(command_line)
        # Launch a subprocess to start the bokeh server
        subp = subprocess.Popen(
            command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        # Write the port used and its PID in the tmp file
        serve.update_port_use(port, subp.pid, data_path, serve_file_path)
        print(f"ID#1: Port {port} unused: launch bokeh server.")
        # Wait before open the browser
        time.sleep(1)
        # Open the browser connected to the corresponding port
        webbrowser.open_new(f"http://localhost:{port}/{figure_script}")
    # If the default port already in use
    else:
        # get info about the port use
        info_port = serve.get_port_use(serve_file_path, port=port)
        # if no info: the port may be used by another process !

        # Test if the file looked on the port is the same as here
        if info_port["look_file"] == data_path:
            # If same file, just re-open a web browser on the port
            # Wait before open the browser
            time.sleep(1)
            # Open the browser connected to the corresponding port
            webbrowser.open_new(f"http://localhost:{port}/{figure_script}")
            print(f"ID#2: Port {port} used with the same figure")
        else:
            print(f"ID#3: Port {port} used but we want to show another figure.")
            update_counter = 0
            while serve.is_port_in_use(port):
                port += 1
                update_counter += 1
                if update_counter > max_server:
                    print(
                        f"Max number of bokeh serve has been reached ({max_server}). Try to shut down bokeh server. "
                    )

            print(f"Port {port} used instead.")
            # Command line to serve bokeh and give the tmp path for the data
            command_line = [
                "bokeh",
                "serve",
                script_path,
                "--port",
                str(port),
                "--args",
                data_path,
            ]
            subp = subprocess.Popen(
                command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            # Write the port used and its PID in the tmp file
            serve.update_port_use(port, subp.pid, data_path, serve_file_path)

            # Wait before open the browser
            time.sleep(1)
            # Open the browser connected to the corresponding port
            webbrowser.open_new(f"http://localhost:{port}/{figure_script}")
