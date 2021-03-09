import numpy as np
import holoviews as hv
from holoviews import opts
from holoviews import streams
import pickle
hv.extension('bokeh')
import sys
import panel as pn

# path_data = sys.argv[1]
# with open(path_data, "rb") as f:
#     f.seek(0)
#     cube_data = pickle.load(f)
#
# cube_name = [k for k in cube_data.keys() if k != "wavelengths"][0]
# cube_show = cube_data[cube_name]
# wavelengths = cube_data["wavelengths"]

data = np.load("/Users/Antoine/twophoton.npz")
calcium_array = data['Calcium']
# ds = hv.Dataset((np.arange(cube_show.shape[0]), np.arange(cube_show.shape[1]), np.arange(cube_show.shape[2]),
#                  cube_show.reshape(cube_show.shape[2], cube_show.shape[1], cube_show.shape[0])), ['wavelengths', 'x', 'y'], 'Cube')
#
# print(ds)
# print(type(ds.data))
# print(list(ds.data.keys()))
# print(ds.data['Cube'])
# polys = hv.Polygons([])
# box_stream = streams.BoxEdit(source=polys)
#
# # def roi_curves(data):
# #     if not data or not any(len(d) for d in data.values()):
# #         return hv.NdOverlay({0: hv.Curve([], 'wavelengths', 'Reflectance')})
# #
# #     curves = {}
# #     data = zip(data['x0'], data['x1'], data['y0'], data['y1'])
# #     for i, (x0, x1, y0, y1) in enumerate(data):
# #         selection = ds.select(x=(x0, x1), y=(y0, y1))
# #         curves[i] = hv.Curve(selection.aggregate('wavelengths', np.mean))
# #     return hv.NdOverlay(curves)
#
# # hlines = hv.HoloMap({i: hv.VLine(i) for i in range(cube_show.shape[2])}, 'wavelengths')
# # dmap = hv.DynamicMap(roi_curves, streams=[box_stream])
#
# im = ds.to(hv.Image, ['x', 'y'], dynamic=True)
# # layout = (im * polys + dmap * hlines).opts(
# #     opts.Curve(width=400, framewise=True),
# #     opts.Polygons(fill_alpha=0.2, line_color='white'),
# #     opts.VLine(color='black'))
# layout = (im).opts()
# # opts.defaults(
# #     opts.GridSpace(shared_xaxis=True, shared_yaxis=True),
# #     opts.Image(cmap='viridis', width=400, height=400),
# #     opts.Labels(text_color='white', text_font_size='8pt', text_align='left', text_baseline='bottom'),
# #     opts.Path(color='white'),
# #     opts.Spread(width=600),
# #     opts.Overlay(show_legend=False))
#
# #im2 = ds.to(hv.Image, ['x','y'], dynamic=True).opts(opts.Image(cmap='viridis', width=400, height=400))
# print(type(layout))
# hv.renderer('bokeh').server_doc(layout)
# #pn.panel(layout).servable(title='babla')

ds = hv.Dataset((np.arange(50), np.arange(111), np.arange(62), calcium_array),
                ['Time', 'x', 'y'], 'Fluorescence')

polys = hv.Polygons([])
box_stream = streams.BoxEdit(source=polys)


def roi_curves(data):
    if not data or not any(len(d) for d in data.values()):
        return hv.NdOverlay({0: hv.Curve([], 'Time', 'Fluorescence')})

    curves = {}
    data = zip(data['x0'], data['x1'], data['y0'], data['y1'])
    for i, (x0, x1, y0, y1) in enumerate(data):
        selection = ds.select(x=(x0, x1), y=(y0, y1))
        curves[i] = hv.Curve(selection.aggregate('Time', np.mean))
    return hv.NdOverlay(curves)


hlines = hv.HoloMap({i: hv.VLine(i) for i in range(50)}, 'Time')
dmap = hv.DynamicMap(roi_curves, streams=[box_stream])

im = ds.to(hv.Image, ['x', 'y'], dynamic=True)
layout = (im * polys + dmap * hlines).opts(
    opts.Curve(width=400, framewise=True),
    opts.Polygons(fill_alpha=0.2, line_color='white'),
    opts.VLine(color='black'))

#hv.renderer('bokeh').server_doc(layout)
#pn.panel(layout).servable(title='babla')

server = pn.serve(layout, start=False, show=False)
server.start()