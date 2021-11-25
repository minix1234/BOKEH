import math
import numpy as np

from bokeh.util.logconfig import bokeh_logger as lg

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models.widgets import Slider, TextInput, RangeSlider, Spinner,CheckboxGroup,DataTable, TableColumn, NumberFormatter, Select
from bokeh.models import Range1d, RadioButtonGroup
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource

#from bokeh.themes import Theme
#curdoc().theme = Theme(filename='/app/openet/theme.yaml')

import fluids
from fluids import nearest_pipe, differential_pressure_meter_solver
from scipy.constants import psi, atm, inch,convert_temperature


from openet.conversions import mass_to_molar, mass_to_volume
from openet.constants import Meter_Type, Tap_Position, Tap_Type

# Class Definition
# ---------------------------------
# Used for tracking various items
# by passing in "self"


class dPMeterSolver():
    """Class to control the dP meter solver results for
    the diplay on the Bokeh server"""

    def __init__(self):
        """Initialize the opcua nodeid sensor."""

        lg.info("Initializing the dPMeterSolver")

        self.ga = True
        self._name = "Name"
        self._plotpoint = 25
        self._plotx = None
        self._ploty = None
        self._plotheight = 600
        self._plotwidth = 800
        self._widgetwidth = 150

        self._columns_gas = None
        self._columns_liquid = None
        self.gas_data_table = None
        self.liquid_data_table = None

        self.source = None
        self.plot = None

        self.data_init()

        self.plotsetup()

        self.tablesetup()

        self.setupwidgets()


    def data_init(
        self,
    ):

        # Set up data
        lg.info("Initializing the dPMeterSolver data")

        self._plotx = np.linspace(0, 4*np.pi, self._plotpoint)
        self._ploty = np.sin(self._plotx)
        self._dataz = self._ploty
        self._datakg = self._ploty
        self._datav = self._ploty

        # Set up data source
        self.source = ColumnDataSource(data=dict(x=self._plotx, y=self._ploty, v=self._datav, z=self._dataz, kg=self._datakg))

    def plotsetup(
        self,
    ):
        """Setup the main dP vs Flowrate Plot"""

        # Set up plot
        self.plot = figure(plot_height=self._plotheight, plot_width=self._plotwidth, title="Flow Rate Calculations",
                    tools="crosshair,box_zoom,pan,reset,save,wheel_zoom")

        self.plot.xaxis.axis_label = "Differential Pressure [inWC]"
        self.plot.yaxis.axis_label = "Flow at Base conditions [MMSCFD]"
        self.plot.line('x', 'y', source=self.source)

    
    def tablesetup(
        self,
    ):
        """Setup the main TableColumns for the liquid and gas data tables"""
        # Setup Gas Table Space
        # ------------------------

        self._columns_gas = [
            TableColumn(field="x", title="dP [inWC]", formatter=NumberFormatter(format="0.0")),
            TableColumn(field="kg", title="Mass Flow [Kg/s]", formatter=NumberFormatter(format="0.000")),
            TableColumn(field="y", title="Flow Rate [MMSCFD]",formatter=NumberFormatter(format="0.00"))
            ]

        tablewidth=450

        self.gas_data_table = DataTable(source=self.source, columns=self._columns_gas, width=tablewidth, height=800)


        # Setup Liquid Table Space
        # ------------------------
        # source.data = dict(x=DP, y=SVF, v=VF, z=MF, kg=M)

        self._columns_liquid = [
            TableColumn(field="x", title="dP [inWC]", formatter=NumberFormatter(format="0.00")),
            TableColumn(field="kg", title="Mass Flow [Kg/s]", formatter=NumberFormatter(format="0.000")),
            TableColumn(field="v", title="Flow Rate [MBPD]",formatter=NumberFormatter(format="0.000")),
            TableColumn(field="y", title="Standard Flow Rate [MSBPD]",formatter=NumberFormatter(format="0.000"))
            ]

        tablewidth=600

        self.liquid_data_table = DataTable(source=self.source, columns=self._columns_liquid, width=tablewidth, height=800)


    def setupwidgets(self):
        # Set up widgets
        ## TextInputs
        self.text       = TextInput(title="title", value='#Enter Engineering Tag Name')
        self.density    = TextInput(title="Density [Kg/M3]", value='775', width=self._widgetwidth)
        self.Pi         = TextInput(title="Pressure [PSIG]", value='100', width=self._widgetwidth)
        self.viscosity  = TextInput(title="viscosity [cP]", value='1', width=self._widgetwidth)
        self.isentropic = TextInput(title="Isentropic Exponent", value='1.1', width=self._widgetwidth)
        self.densitybase= TextInput(title="Base Density [kg/m3]", value='1000', width=self._widgetwidth)
        self.orifice    = TextInput(title="Orifice Size [Inch]", value='0.75980', width=self._widgetwidth)
        self.pipe       = TextInput(title="Pipe ID [Inch]", value='2.066141', width=self._widgetwidth)
        self.molecular  = TextInput(title="Molecular Weight", value='2', width=self._widgetwidth)

        # Disable test widgets for current gas/liquid mode. (self.ga)
        self.molecular.disabled         = not(self.ga)
        self.densitybase.disabled       = self.ga
        self.gas_data_table.visible     = self.ga
        self.liquid_data_table.visible  = not(self.ga)


        ## RangeSliders
        self.DP_range = RangeSlider(start=1, end=1000, value=(1,250), step=1, title="dP Range [Inch H2O]")

        #RadioGroups
        labels = ["Gas", "Liquid"]
        self.radio_button_group = RadioButtonGroup(labels=labels, active=0) 
        #self.ga inits to true. "gas active", which is the first index, or 0, which is active

        # Selection Options
        self.meter_select = Select(title="Meter Type:", value="ISO 5167 orifice", options=Meter_Type)
        self.tap_select = Select(title="Tap Location:", value="flange", options=Tap_Type, width=self._widgetwidth)
        self.tap_position = Select(title="Tap Position:", value="180 degree", options=Tap_Position, width=self._widgetwidth)

    def update_data(self, attr, old, new):


        #Get Text Input and update plot title
        self.plot.title.text = self.text.value


        # Get the current input widget values
        P1 = (float(self.Pi.value) + 14.7)*psi
        rho = float(self.density.value)
        mu = float(self.viscosity.value)/1000
        k = float(self.isentropic.value)
        rhos = float(self.densitybase.value)
        MW = float(self.molecular.value)
        Do = float(self.orifice.value)*inch
        Di = float(self.pipe.value)*inch

        meter = self.meter_select.value
        tap = self.tap_select.value
    
        #lg.info('meter selected')
        #lg.info(meter)
        eccentric_test = ['Miller eccentric orifice','eccentric orifice','ISO 15377 eccentric orifice']

        if meter in eccentric_test:
            self.tap_position.disabled = False
            tap_position = self.tap_position.value
        else:
            self.tap_position.disabled = True
            tap_position = None

        slider_value=self.DP_range.value ##Getting slider value
        dp_min=slider_value[0]
        dp_max=slider_value[1]


        steps = self._plotpoint        
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
            
            m = differential_pressure_meter_solver(D=Di, D2=Do, P1=P1, P2=P2, rho=rho, mu=mu, k=k, meter_type=meter, taps='flange', tap_position=tap_position)
            
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
        if self.ga:

            self.source.data = dict(x=DP, y=MF, v=VF, z=SVF, kg=M)

        else:

            self.source.data = dict(x=DP, y=SVF, v=VF, z=MF, kg=M)

    
    def update_selection(self, attr, old, new):
        lg.info("Update Selection Called")

        Selector = int(self.radio_button_group.active)
        lg.info(Selector)

        if Selector == 0:
            self.ga = True

        else:
            self.ga = False


        self.molecular.disabled = not(self.ga)
        self.densitybase.disabled = self.ga


        self.gas_data_table.visible = self.ga
        self.liquid_data_table.visible = not(self.ga)


        if self.ga:
            
            self.plot.yaxis.axis_label = "Flow at Base conditions [MMSCFD]"

        else:

            self.plot.yaxis.axis_label = "Flow at Base conditions [MBPD]"

        self.update_data(attr, old, new)