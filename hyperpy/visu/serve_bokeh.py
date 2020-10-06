import os 
import time
import subprocess
import webbrowser

from hyperpy.utils import serve
from hyperpy.visu import utils

## TO DO:
# Make the function serve a class. 
# Methods: open a new port. Connect to it. Close the port. (Close port when instance deleted ? )
# Attibute: path to data. Port number. Figure script.
# Write a readme.

def get_figure_script(figure_script):
    """
    get the script path from figure_script name
    """
    script_path = utils.check_figure_file(figure_script)
    return script_path



def serve_bokeh_figure(data, script_path, port=8080, max_server=10):
    """
    serve a bokeh figure based on figure_script using the data

    data: data to be pickle
    script_path: str, complete path to the figure script
    port: int, first port to test for connexion
    max_server: int, max number of port to test. 

    """
    figure_script = os.path.split(script_path)[1]
    figure_script = figure_script.replace('.py', '')
    # Create local temporary directory
    tmp_path = serve.create_tmp_dir('bokeh')
    # Temp file for bokeh serve
    serve_file_path = os.path.join(tmp_path, 'bokeh_serve_log.csv')
    # Get a hash from data data
    filename = str(hash(str(data)))
    # Save the data in the temporary dir
    data_path = serve.save_tmp(data, filename, tmp_path)
    print(data_path)
    # Command line to serve bokeh and give the tmp path for the data
    command_line = ['bokeh', 'serve', script_path, '--port', str(port),'--args', data_path]
    
    # Test if the current port is running
    port_used = serve.is_port_in_use(port)
    # If the default port is unussed
    if not(port_used):
        print(command_line)
        # Launch a subprocess to start the bokeh server
        subp = subprocess.Popen(command_line,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
        
        # Write the port used and its PID in the tmp file
        serve.update_port_use(port, subp.pid, data_path, serve_file_path)
        print(f'ID#1: Port {port} unused: launch bokeh server.')
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
        if info_port['look_file'] == data_path:
            # If same file, just re-open a web browser on the port
            # Wait before open the browser
            time.sleep(1)
            # Open the browser connected to the corresponding port
            webbrowser.open_new(f"http://localhost:{port}/{figure_script}")
            print(f'ID#2: Port {port} used with the same figure')
        else:
            print(f'ID#3: Port {port} used but we want to show another figure.')
            update_counter = 0
            while serve.is_port_in_use(port):
                port += 1
                update_counter +=1
                if update_counter > max_server:
                    print(f'Max number of bokeh serve has been reached ({max_server}). Try to shut down bokeh server. ')            
            
            print(f'Port {port} used instead.')
            # Command line to serve bokeh and give the tmp path for the data
            command_line = ['bokeh', 'serve', script_path, '--port', str(port),'--args', data_path]
            subp = subprocess.Popen(command_line,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
            # Write the port used and its PID in the tmp file
            serve.update_port_use(port, subp.pid, data_path, serve_file_path)
            
            # Wait before open the browser
            time.sleep(1)
            # Open the browser connected to the corresponding port
            webbrowser.open_new(f"http://localhost:{port}/{figure_script}")