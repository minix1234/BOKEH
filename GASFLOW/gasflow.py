import math
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models.widgets import Slider, TextInput, RangeSlider, Spinner,CheckboxGroup,DataTable, TableColumn, NumberFormatter
from bokeh.models import Range1d
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource


import fluids
from fluids import nearest_pipe, differential_pressure_meter_solver
from scipy.constants import psi, atm, inch,convert_temperature
from thermo.chemical import Chemical, Mixture


def mass_to_molar(m,MW):
    """
    Convert a mass flow from 'Kg/s' to MMSCFD
    - 15 C
    - 1 ATM
    """
    
    mf = m*60*60 # Kg/s -> Kg/hr
    mf = mf/MW #Kg/hr -> Kgmole/hr
    mf = mf*22.414 #22.414 Nm3 per kmole Normal Volume occupies 22.414 [L/mol] [m3/kmol] [m3/kgmol]
    mf = mf*((273+15)/273) #STP = 15oC, NTP 0oC: conversion from normal (0 C) to standard (15 C)
    mf = mf*(3.282**3) # meters cubic to feet cubic
    mf = mf*24 # Scf/hr -> cf/day
    mf = mf/1e6 #SCFD -> MMSCFD
    
    #print(m,'Kg/s', MW,'g/mol', mf,'MMSCFD')
    
    return (mf)


#def make_document(doc):

# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))

#hover = HoverTool(tooltips=[("dP", "@x"),("Flow", "@y")])

# Set up plot
plot = figure(plot_height=600, plot_width=800, title="Flow Rate Calculations",
            tools="crosshair,box_zoom,pan,reset,save,wheel_zoom")#,
            #sizing_mode='scale_width')#,
            #x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])
plot.sizing_mode='scale_both'
plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

columns = [
TableColumn(field="x", title="dP", formatter=NumberFormatter(format="0.0")),
TableColumn(field="y", title="Flow Rate [MMSCFD]",formatter=NumberFormatter(format="0.00"))]

data_table = DataTable(source=source, columns=columns, width=300, height=800)


# Set up widgets
text = TextInput(title="title", value='#Enter Engineering Tag Name')
#density = Slider(title="density", value=0.0, start=-5.0, end=5.0, step=0.1)
#Pi = Slider(title="Upstream Pressure [PSIG]", value=1.0, start=-14, end=500, step=1)
#isentropic = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)
density = Spinner(title="Density [Kg/M3]", low=1, high=1500, step=0.25, value=2, width=100)
Pi = Spinner(title="Upstream Pressure [PSIG]", low=1, high=500, step=0.1, value=100, width=100)
viscosity = Spinner(title="viscosity [cP]", low=0.001, high=5000, step=0.001, value=0.01, width=100)
isentropic = Spinner(title="Isentropic Exponent",low=0.1, high=2, step=0.1, value=1, width=100)
DP_range = RangeSlider(start=1, end=1000, value=(1,250), step=1, title="dP Range [Inch H2O]")
molecular = Spinner(title="Molecular Weight",low=0.1, high=200, step=0.1, value=2, width=100)
orifice = Spinner(title="Orifice Size [inches]",low=0.1, high=20, step=0.001, value=1.0521, width=100)
pipe = Spinner(title="Pipe Size [inches]",low=0.1, high=20, step=0.001, value=2.0661417322834645, width=100)
#autoscale = CheckboxGroup(labels=["Auto-Scale"], active=[0])

# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value

#def update_scale(attrname, old, new):
#    #print(autoscale.active)
#    if autoscale.active == [0]:
#        #print('autoscale active')
#        plot.x_range=None
#        plot.y_range=None
#    else:
#        plot.x_range=Range1d(min(source.data['x']), max(source.data['x']))
#        plot.y_range=Range1d(min(source.data['y']), max(source.data['y']))
#        print(plot.x_range, plot.y_range)
    
text.on_change('value', update_title)

#autoscale.on_change('active', update_scale)



def update_data(attrname, old, new):

    # Get the current slider values
    P1 = (Pi.value + 14.7)*psi
    rho = density.value
    mu = viscosity.value/1000
    k = isentropic.value
    MW = molecular.value
    Do = orifice.value*inch
    Di = pipe.value*inch
    
    
    slider_value=DP_range.value ##Getting slider value
    dp_min=slider_value[0]
    dp_max=slider_value[1]

    steps = 20
    
    Log_steps = 10**np.linspace(math.log10(dp_min),math.log10(dp_max),steps+1)

    DP = []
    MF = []
    M = []

    for i,dP in enumerate(Log_steps):
        #   print(i,dP)
        DP.append(dP)

        #dP = i # differential in inches of water ("H2O) 
        P2 = P1 - (dP*248.84)
        #print(Di,Do,P1,P2,rho,mu,k)
        m = differential_pressure_meter_solver(D=Di, D2=Do, P1=P1, P2=P2, rho=rho, mu=mu, k=k, meter_type='ISO 5167 orifice', taps='D/2')
        mf = mass_to_molar(m, MW)
        M.append(m)
        MF.append(mf)


    source.data = dict(x=DP, y=MF)
    #print(source.data['x'])
    
for w in [density, Pi, viscosity, isentropic, DP_range,molecular,orifice,pipe]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = column(text, density, Pi, viscosity, isentropic, DP_range,molecular,orifice,pipe)#,autoscale)
upper = row(inputs, plot,data_table, width=1800)
curdoc().add_root(upper)
curdoc().title = "Flowrates"
    
#apps = {'/': Application(FunctionHandler(make_document))}

#server = Server(apps, port=5009,allow_websocket_origin=['*'])
#server.start()