import os
import sys
import pickle
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.layouts import column, layout, widgetbox, row
from bokeh.io import curdoc, output_notebook
from bokeh.models.widgets import Slider
from bokeh.models import Div

path_data = sys.argv[1]
with open(path_data, "rb") as f:
    f.seek(0)
    cube_data = pickle.load(f)

cube_name = [k for k in cube_data.keys() if k != "wavelengths"][0]
cube_show = cube_data[cube_name]
wavelengths = cube_data["wavelengths"]

max_figure_width = 1200
max_figure_height = 700
image_ratio = cube_show.shape[0] / cube_show.shape[1]
if cube_show.shape[0] > cube_show.shape[1]:
    figure_width = max_figure_width
    figure_height = int(max_figure_width / image_ratio)
    if figure_height > max_figure_height:
        figure_height = max_figure_height
        figure_width = int(max_figure_height * image_ratio)
elif cube_show.shape[0] <= cube_show.shape[1]:
    figure_height = max_figure_height
    figure_width = int(max_figure_height * image_ratio)
    if figure_width > max_figure_width:
        figure_width = max_figure_width
        figure_height = int(max_figure_height / image_ratio)

init_slice = int(cube_show.shape[2] / 2)
source = ColumnDataSource(data=dict(image=[cube_show[:, :, init_slice]]))

#p = figure(title=cube_name, plot_width=max_figure_width, plot_height=max_figure_height)
p = figure(title=cube_name)

p.x_range.range_padding = p.y_range.range_padding = 0
p.image(
    image="image",
    source=source,
    x=0,
    y=0,
    dw=cube_show.shape[1],
    dh=cube_show.shape[0],
    dilate=True,
    palette="Spectral11",
    level="image",
)
p.grid.grid_line_width = 0.5

slider = Slider(
    start=0, end=cube_show.shape[2] - 1, step=1, value=init_slice, title="Index"
)
div = Div(text=f"Wavelength: {wavelengths[init_slice]} nm")


def update(attr, old, new):
    source.data = dict(image=[cube_show[:, :, slider.value]])
    div.text = f"Wavelength: {wavelengths[slider.value]} nm"


slider.on_change("value", update)
curdoc().add_root(column(p, slider, div))
