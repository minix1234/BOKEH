import math
import numpy as np

from bokeh.util.logconfig import bokeh_logger as lg

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models.widgets import Slider, TextInput, RangeSlider, Spinner,CheckboxGroup,DataTable, TableColumn, NumberFormatter
from bokeh.models import Range1d, RadioButtonGroup
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource

from bokeh.themes import Theme
curdoc().theme = Theme(filename='/app/openet/theme.yaml')

import fluids
from fluids import nearest_pipe, differential_pressure_meter_solver
from scipy.constants import psi, atm, inch,convert_temperature


from openet.conversions import mass_to_molar, mass_to_volume
from openet.dpmeter import dPMeterSolver


# Initialize a new dP meter solver class
dpm = dPMeterSolver()

    
for w in [dpm.text,dpm.density, dpm.Pi, dpm.viscosity, dpm.isentropic, dpm.DP_range,dpm.densitybase,dpm.molecular,dpm.orifice,dpm.pipe]:
    w.on_change('value', dpm.update_data)

for w in [dpm.radio_button_group]:
    w.on_change('active',dpm.update_selection)


# Set up layouts and add to document
# -----------------------------------
# Likely need to init this when we change
# from gas to liquid as we are trying to 
# update the data table layout and columns

row1 = row(dpm.density, dpm.densitybase)
row2 = row(dpm.Pi, dpm.viscosity)
row3 = row(dpm.isentropic,dpm.molecular)
row4 = row(dpm.orifice,dpm.pipe)

inputs = column(dpm.text,dpm.radio_button_group, dpm.DP_range, row1, row2, row3, row4)
upper = row(inputs, dpm.plot)
lower = row(dpm.gas_data_table,dpm.liquid_data_table)


layouts = column(upper,lower)

curdoc().add_root(layouts)

curdoc().title = "dP Meter Flow Rate Calculations"