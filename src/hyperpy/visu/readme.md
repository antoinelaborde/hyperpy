# Visualization tools

## Requirements
hyperspectralpython needs to be installed in the global python environment.
The subprocess that launches the bokeh serve takes the global python environment and needs to know hyperspectralpython and its dependencies. 

Cube visualization provides an API for multiple figure scripts. The principle is to serve a bokeh script by passing some data to this script.

In the example below, the figure script cube_slice is served on a bokeh server and pass the data to the script.

```python
script_figure = 'cube_slice'
serve_bokeh_figure(data, script_figure)
```

For each call to the function serve_bokeh_figure, a new port is used (starting from port 8080 by default). For each new figure request, the function opens a new port unless the default one is free. 

## Close ports
In order to free the port, you can use the following function:

```python
free_port('/tmp/bokeh/bokeh_serve_log.csv', 8080)
```

The path to the bokeh_serve_log.csv file provides the log of the serve_bokeh_figure.

It may happen the port cannot be closed using this function. In this case, you need to follow the instructions:
```shell
# Look for the port of interest, here 8080
lsof -nPi :8080
# Get the PID from the resulting output and kill the process
kill -9 PID
```

### Cube slice
File name: cube_slice
