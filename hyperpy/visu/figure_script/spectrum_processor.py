import sys, pickle
import inspect
from bokeh.plotting import figure,   ColumnDataSource
from bokeh.layouts import column,  row
from bokeh.io import curdoc
from bokeh.models.widgets import Slider
from bokeh.models import  Select, Button, MultiSelect
from hyperpy.preprocessing import transformers
from sklearn.pipeline import Pipeline
import numpy as np

# Import spectral data
path_data = sys.argv[1]
with open(path_data, 'rb') as f:
    f.seek(0)
    spectral_data = pickle.load(f)
# Extract spectral data and wavelengths
specta_name = [k for k in spectral_data.keys() if k!="wavelengths"][0]
spectra = spectral_data[specta_name]
wavelengths = spectral_data["wavelengths"]

# Create list for multi_line plot
spectral_list = [spectra[i,:] for i in range(spectra.shape[0])]
wavelengths_list = [wavelengths for i in range(spectra.shape[0])]

# Get list of available transformers
transformer_class_list = [ class_module[0] for class_module in inspect.getmembers(transformers, inspect.isclass)]
transformer_class_list.remove('TransformerMixin')


transformer_dict = {}
transformers_name = []
for transformer_class in transformer_class_list:
    # Get class
    transformer = getattr(transformers, transformer_class)
    # Get an instance to have the name
    transformer_instance = transformer()
    transformers_name.append(transformer_instance.name)
    # Put the class object in dict
    transformer_dict[transformer_instance.name] = transformer

# Add widgets
select_processing = Select(title="Preprocessing:", value=transformers_name[0], options=transformers_name)
button_add = Button(label="Add", button_type="success")
button_remove = Button(label="Remove")
button_apply = Button(label="Apply")
multi_select = MultiSelect(title="Processing list:", value=[], options=[])
slider_window = Slider(start=3, end=66, value=7, step=2, title="Window Size Savitsky-Golay")
slider_polynomial = Slider(start=1, end=4, value=1, step=1, title="Polynomial Order Savitsky-Golay")
slider_derivation = Slider(start=0, end=3, value=0, step=1, title="Derivation Order Savitsky-Golay")

# Bokeh column data source for spectral plotting
s1 = ColumnDataSource(data=dict(xs= wavelengths_list,ys=spectral_list))
s2 = ColumnDataSource(data=dict(xs= wavelengths_list,ys=spectral_list))
# Left figure for standard ploting 
p1 = figure(plot_width=600, plot_height=400)
p1.multi_line(xs='xs',ys='ys', source=s1)
# Left figure for process ploting
p2 = figure(plot_width=600, plot_height=400)
p2.multi_line(xs='xs',ys='ys', source=s2)

# Add callback
def click_add():
    """
    When the button Add is clicked
    """
    mutli_select_append = multi_select.options
    # Add the selected processing in multi_select only if not present
    if select_processing.value not in mutli_select_append:
        mutli_select_append.append(select_processing.value)
        multi_select.options = mutli_select_append
# Remove callback
def click_rmv():
    """
    When the button Remove is clicked
    """
    mutli_select_list = multi_select.options
    for transformer_name in multi_select.value:
        mutli_select_list.remove(transformer_name)
    multi_select.options = mutli_select_list
# Apply callback
def click_apply():
    """
    When apply is clicked
    """
    # Initialize a list for pipeline
    pipeline_list = []
    # Get the transformer class for each in multi_select
    for transformer_name in multi_select.options:
        transformer = transformer_dict[transformer_name]
        if transformer_name == 'Savistky Golay filter':
            transformer_instance = transformer(window_size=slider_window.value, polynomial_order=slider_polynomial.value,derivation_order=slider_derivation.value)
            pipeline_list.append((transformer_name, transformer_instance))
        else:
            pipeline_list.append((transformer_name, transformer()))
    # Process the spectra if the pipeline is not empty
    if pipeline_list:
        pipe = Pipeline(pipeline_list)
        process_list = []
        spectra =  np.asarray(spectral_list)
        process_list = pipe.fit_transform(spectra).tolist()
        s2.data = dict(xs=wavelengths_list, ys=process_list)
    else:
        s2.data = dict(xs=wavelengths_list, ys=spectral_list)
    
# Add callbacks
button_add.on_click(click_add)
button_remove.on_click(click_rmv)
button_apply.on_click(click_apply)

# Layout
layout = row(
    column(p1, select_processing, button_add),
    column(p2, button_apply, multi_select, button_remove, slider_window, slider_polynomial, slider_derivation))

# Expose
curdoc().add_root(layout)
