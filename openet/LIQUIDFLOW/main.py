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


# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y = np.sin(x)
z = y
kg = y

# Set up data source
source = ColumnDataSource(data=dict(x=x, y=y, v=z, z=z, kg=kg))


# Selector Init

Selector = 0 # 0 is gas, 1 is liquid
gas_active = True
liquid_active = False


# Set up plot
plot = figure(plot_height=600, plot_width=800, title="Flow Rate Calculations",
            tools="crosshair,box_zoom,pan,reset,save,wheel_zoom")

plot.xaxis.axis_label = "Differential Pressure [inWC]"
plot.yaxis.axis_label = "Flow at Base conditions [MMSCFD]"
plot.line('x', 'y', source=source)


# Setup Gas Table Space
# ------------------------

columns_gas = [
TableColumn(field="x", title="dP [inWC]", formatter=NumberFormatter(format="0.0")),
TableColumn(field="y", title="Flow Rate [MMSCFD]",formatter=NumberFormatter(format="0.00"))]

tablewidth=300

gas_data_table = DataTable(source=source, columns=columns_gas, width=tablewidth, height=800)


# Setup Liquid Table Space
# ------------------------
# source.data = dict(x=DP, y=SVF, v=VF, z=MF, kg=M)

columns_liquid = [
TableColumn(field="x", title="dP [inWC]", formatter=NumberFormatter(format="0.00")),
TableColumn(field="kg", title="Mass Flow [Kg/s]", formatter=NumberFormatter(format="0.000")),
TableColumn(field="v", title="Flow Rate [MBPD]",formatter=NumberFormatter(format="0.000")),
TableColumn(field="y", title="Standard Flow Rate [MSBPD]",formatter=NumberFormatter(format="0.000"))]

tablewidth=600

liquid_data_table = DataTable(source=source, columns=columns_liquid, width=tablewidth, height=800)


# Set up widgets
## TextInputs
text = TextInput(title="title", value='#Enter Engineering Tag Name')
density = TextInput(title="Density [Kg/M3]", value='775', width=150)
Pi = TextInput(title="Pressure [PSIG]", value='100', width=150)
viscosity = TextInput(title="viscosity [cP]", value='1', width=150)
isentropic = TextInput(title="Isentropic Exponent", value='1', width=150)
densitybase = TextInput(title="Base Density [kg/m3]", value='1000', width=150)
orifice = TextInput(title="Orifice Size [Inch]", value='0.75980', width=150)
pipe = TextInput(title="Pipe ID [Inch]", value='2.066141', width=150)
molecular = TextInput(title="Molecular Weight", value='2', width=150)

molecular.disabled = liquid_active
densitybase.disabled = gas_active
gas_data_table.visible = gas_active
liquid_data_table.visible = liquid_active


## RangeSliders
DP_range = RangeSlider(start=1, end=1000, value=(1,250), step=1, title="dP Range [Inch H2O]")

#RadioGroups
LABELS = ["Gas", "Liquid"]
radio_button_group = RadioButtonGroup(labels=LABELS, active=0)


# Update Selection (Gas or Liquid)
# ---------------------------------
# Can we just have one Bokeh app that
# will allow for gas or liquid Selection


def update_selection(attrname, old, new):
    lg.info("Update Selection Called")

    Selector = int(radio_button_group.active)
    lg.info(Selector)

    if Selector == 0:
        gas_active = True
        liquid_active = False
    else:
        gas_active = False
        liquid_active = True

    
    molecular.disabled = liquid_active
    densitybase.disabled = gas_active

    gas_data_table.visible = gas_active
    liquid_data_table.visible = liquid_active

    if gas_active:
        plot.yaxis.axis_label = "Flow at Base conditions [MMSCFD]"

    else:
        plot.yaxis.axis_label = "Flow at Base conditions [MBPD]"

    update_data(attrname, old, new)




def update_data(attrname, old, new):

    #Get Tesxt Inputs and do stuff
    plot.title.text = text.value


    # Get the current slider values
    P1 = (float(Pi.value) + 14.7)*psi
    rho = float(density.value)
    mu = float(viscosity.value)/1000
    k = float(isentropic.value)
    rhos = float(densitybase.value)
    MW = float(molecular.value)
    Do = float(orifice.value)*inch
    Di = float(pipe.value)*inch
    

    # Selector Check
    # needed untill we build a class

    Selector = int(radio_button_group.active)

    if Selector == 0:
        gas_active = True
        liquid_active = False
    else:
        gas_active = False
        liquid_active = True

    # replace above with class

    slider_value=DP_range.value ##Getting slider value
    dp_min=slider_value[0]
    dp_max=slider_value[1]

    steps = 30
    
    Log_steps = 10**np.linspace(math.log10(dp_min),math.log10(dp_max),steps+1)

    DP = []
    MF = []
    VF = []
    SVF = []
    M = []

    for i,dP in enumerate(Log_steps):
        #   print(i,dP)
        DP.append(dP)

        P2 = P1 - (dP*248.84)
        
        m = differential_pressure_meter_solver(D=Di, D2=Do, P1=P1, P2=P2, rho=rho, mu=mu, k=k, meter_type='ISO 5167 orifice', taps='flange')
        
        M.append(m)

        #Calculate the standard molar gas flow
        mf = mass_to_molar(m, MW)
        MF.append(mf)
        
        #Calculate Volumetric Flow
        vf = mass_to_volume(m, rho)
        VF.append(vf)
        SVF.append(vf*rho/rhos)


    # Update Plotable Data
    # --------------------------------
    # if we can not init to change the 
    # table space then maybe we consider
    # that we understand how to flip y=[]
    # data around.
    if gas_active:
        lg.info("Gas Active: Logging Molar Flow")
        lg.info(MF)
        source.data = dict(x=DP, y=MF, v=VF, z=SVF, kg=M)

    else:
        lg.info("Liquid Active: Logging Volumetric Flow")
        lg.info(VF)
        lg.info(SVF)
        source.data = dict(x=DP, y=SVF, v=VF, z=MF, kg=M)

    
    


    
for w in [text,density, Pi, viscosity, isentropic, DP_range,densitybase,molecular,orifice,pipe]:
    w.on_change('value', update_data)

for w in [radio_button_group]:
    w.on_change('active',update_selection)


# Set up layouts and add to document
# -----------------------------------
# Likely need to init this when we change
# from gas to liquid as we are trying to 
# update the data table layout and columns

row1 = row(density, densitybase)
row2 = row(Pi, viscosity)
row3 = row(isentropic,molecular)
row4 = row(orifice,pipe)

inputs = column(text,radio_button_group, DP_range, row1, row2, row3, row4)
upper = row(inputs, plot)
lower = row(gas_data_table,liquid_data_table)


layouts = column(upper,lower)

curdoc().add_root(layouts)

curdoc().title = "Flowrates"
    