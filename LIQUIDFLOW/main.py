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


def mass_to_volume(m,den):
    """
    Convert a mass flow from 'Kg/s' to MBPD
    """
    
    mf = m*60*60*24 # Kg/s -> Kg/day
    mf = mf/den #Kg/day -> m3/day
    mf = mf*6.289811 #CMD -> BPD
    mf = mf/1000 #BPD -> MBPD
    
    #print(m,'Kg/s', MW,'g/mol', mf,'MMSCFD')
    
    return (mf)


#def make_document(doc):

# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y = np.sin(x)
z = y
kg = y

source = ColumnDataSource(data=dict(x=x, y=y, z=z, kg=kg))

#hover = HoverTool(tooltips=[("dP", "@x"),("Flow", "@y")])

# Set up plot
plot = figure(plot_height=600, plot_width=800, title="Flow Rate Calculations",
            tools="crosshair,box_zoom,pan,reset,save,wheel_zoom")#,
            #sizing_mode='scale_width')#,
            #x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])
plot.xaxis.axis_label = "Differential Pressure [inWC]"
plot.xaxis.major_label_text_font_size = "16pt"
plot.xaxis.axis_label_text_font_size = "22pt"
plot.xaxis.axis_label_text_font_style = 'normal'

plot.yaxis.axis_label = "Flow at Base conditions [MBPD]"
plot.yaxis.major_label_text_font_size = "16pt"
plot.yaxis.axis_label_text_font_size = "22pt"
plot.yaxis.axis_label_text_font_style = 'normal'

plot.sizing_mode='scale_both'
plot.line('x', 'z', source=source, line_width=3, line_alpha=0.6)

columns = [
TableColumn(field="x", title="dP [inWC]", formatter=NumberFormatter(format="0.00")),
TableColumn(field="kg", title="mass flow [kg/s]", formatter=NumberFormatter(format="0.000")),
TableColumn(field="y", title="Flow Rate [MSBPD]",formatter=NumberFormatter(format="0.000")),
TableColumn(field="z", title="Standard Flow Rate [MBPD]",formatter=NumberFormatter(format="0.000"))]

data_table = DataTable(source=source, columns=columns, width=600, height=800)


# Set up widgets
text = TextInput(title="title", value='#Enter Engineering Tag Name')

#density = Spinner(title="Density [Kg/M3]", low=1, high=1500, step=1, value=775, width=100)
density = TextInput(title="Density [Kg/M3]", value='775', width=100)

#Pi = Spinner(title="Upstream Pressure [PSIG]", low=1, high=5000, step=1, value=100, width=100)
Pi = TextInput(title="Upstream Pressure [PSIG]", value='100', width=100)

#viscosity = Spinner(title="viscosity [cP]", low=0.001, high=5000, step=0.001, value=1, width=100)
viscosity = TextInput(title="viscosity [cP]", value='1', width=100)

#isentropic = Spinner(title="Isentropic Exponent",low=0.1, high=2, step=0.1, value=1, width=100)
isentropic = TextInput(title="Isentropic Exponent", value='1', width=100)


DP_range = RangeSlider(start=1, end=1000, value=(1,250), step=1, title="dP Range [Inch H2O]")

#molecular = Spinner(title="Base Density",low=0.1, high=1500, step=1, value=875, width=100)
densitybase = TextInput(title="Base Density [kg/m3]", value='1000', width=100)

#orifice = Spinner(title="Orifice Size [inches]",low=0.1, high=10, step=0.01, value=0.759, width=100)
orifice = TextInput(title="Orifice Size [Inch]", value='0.75980', width=100)

#pipe = Spinner(title="Pipe Size [inches]",low=0.1, high=10, step=0.001, value=2.0661417322834645, width=100)
pipe = TextInput(title="Pipe ID [Inch]", value='2.066141', width=100)
#autoscale = CheckboxGroup(labels=["Auto-Scale"], active=[0])




def update_data(attrname, old, new):

    #Get Tesxt Inputs and do stuff
    plot.title.text = text.value


    # Get the current slider values
    P1 = (float(Pi.value) + 14.7)*psi
    rho = float(density.value)
    mu = float(viscosity.value)/1000
    k = float(isentropic.value)
    rhos = float(densitybase.value)
    Do = float(orifice.value)*inch
    Di = float(pipe.value)*inch
    
    
    slider_value=DP_range.value ##Getting slider value
    dp_min=slider_value[0]
    dp_max=slider_value[1]

    steps = 30
    
    Log_steps = 10**np.linspace(math.log10(dp_min),math.log10(dp_max),steps+1)

    DP = []
    MF = []
    SMF = []
    M = []

    for i,dP in enumerate(Log_steps):
        #   print(i,dP)
        DP.append(dP)

        #dP = i # differential in inches of water ("H2O) 
        P2 = P1 - (dP*248.84)
        #print(Di,Do,P1,dP,P2,rho,mu,k)
        m = differential_pressure_meter_solver(D=Di, D2=Do, P1=P1, P2=P2, rho=rho, mu=mu, k=k, meter_type='ISO 5167 orifice', taps='flange')
        mf = mass_to_volume(m, rho)
        M.append(m)
        MF.append(mf)
        SMF.append(mf*rho/rhos)

    
    source.data = dict(x=DP, y=MF, z=SMF, kg=M)
    #print(source.data['x'])
    
for w in [density, Pi, viscosity, isentropic, DP_range,densitybase,orifice,pipe,text]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = column(text, density, Pi, viscosity, isentropic, DP_range,densitybase,orifice,pipe)#,autoscale)
#upper = row(inputs, plot,data_table, width=1800)
upper = row(inputs, plot)
lower = row(data_table)
layouts = column(upper,lower)
curdoc().add_root(layouts)
curdoc.title = "Flowrates"
    
#apps = {'/': Application(FunctionHandler(make_document))}

#server = Server(apps, port=5010,allow_websocket_origin=['*'])
#server = Server(apps)
#server.start()