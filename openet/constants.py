'''
Reference: 
https://fluids.readthedocs.io/_modules/fluids/flow_meter.html,
https://fluids.readthedocs.io/fluids.flow_meter.html?highlight=eccentric%20orifice#orifice-plates-flow-nozzles-venturi-tubes-cone-and-wedge-meters-fluids-flow-meter

Good documentation on orifice types
https://www.deltafluid.fr/files/Produits/Documents/1573132745_orifice-plate-overview-rev5-jan-2016.pdf

'''

CONCENTRIC_ORIFICE = 'orifice' # normal
ECCENTRIC_ORIFICE = 'eccentric orifice'
CONICAL_ORIFICE = 'conical orifice'
SEGMENTAL_ORIFICE = 'segmental orifice'
QUARTER_CIRCLE_ORIFICE = 'quarter circle orifice'
CONDITIONING_4_HOLE_ORIFICE = 'Rosemount 4 hole self conditioing'

ORIFICE_HOLE_TYPES = [CONCENTRIC_ORIFICE, ECCENTRIC_ORIFICE, CONICAL_ORIFICE,
                      SEGMENTAL_ORIFICE, QUARTER_CIRCLE_ORIFICE]

ORIFICE_CORNER_TAPS = 'corner'
ORIFICE_FLANGE_TAPS = 'flange'
ORIFICE_D_AND_D_2_TAPS = 'D and D/2'
ORIFICE_PIPE_TAPS = 'pipe' # Not in ISO 5167
ORIFICE_VENA_CONTRACTA_TAPS = 'vena contracta' # Not in ISO 5167, normally segmental or eccentric orifices

# Used by miller; modifier on taps
TAPS_OPPOSITE = '180 degree'
TAPS_SIDE = '90 degree'


ISO_5167_ORIFICE = 'ISO 5167 orifice'
ISO_15377_ECCENTRIC_ORIFICE = 'ISO 15377 eccentric orifice'
ISO_15377_QUARTER_CIRCLE_ORIFICE = 'ISO 15377 quarter-circle orifice'
ISO_15377_CONICAL_ORIFICE = 'ISO 15377 conical orifice'

MILLER_ORIFICE = 'Miller orifice'
MILLER_ECCENTRIC_ORIFICE = 'Miller eccentric orifice'
MILLER_SEGMENTAL_ORIFICE = 'Miller segmental orifice'
MILLER_CONICAL_ORIFICE = 'Miller conical orifice'
MILLER_QUARTER_CIRCLE_ORIFICE = 'Miller quarter circle orifice'

UNSPECIFIED_METER = 'unspecified meter'


LONG_RADIUS_NOZZLE = 'long radius nozzle'
ISA_1932_NOZZLE = 'ISA 1932 nozzle'
VENTURI_NOZZLE = 'venuri nozzle'

AS_CAST_VENTURI_TUBE = 'as cast convergent venturi tube'
MACHINED_CONVERGENT_VENTURI_TUBE = 'machined convergent venturi tube'
ROUGH_WELDED_CONVERGENT_VENTURI_TUBE = 'rough welded convergent venturi tube'


HOLLINGSHEAD_ORIFICE = 'Hollingshead orifice'
HOLLINGSHEAD_VENTURI_SMOOTH = 'Hollingshead venturi smooth'
HOLLINGSHEAD_VENTURI_SHARP = 'Hollingshead venturi sharp'
HOLLINGSHEAD_CONE = 'Hollingshead v cone'
HOLLINGSHEAD_WEDGE = 'Hollingshead wedge'


CONE_METER = 'cone meter'
WEDGE_METER = 'wedge meter'

# __all__.extend(['ISO_5167_ORIFICE','ISO_15377_ECCENTRIC_ORIFICE', 'MILLER_ORIFICE',
#                 'MILLER_ECCENTRIC_ORIFICE', 'MILLER_SEGMENTAL_ORIFICE',
#                 'LONG_RADIUS_NOZZLE', 'ISA_1932_NOZZLE',
#                 'VENTURI_NOZZLE', 'AS_CAST_VENTURI_TUBE',
#                 'MACHINED_CONVERGENT_VENTURI_TUBE',
#                 'ROUGH_WELDED_CONVERGENT_VENTURI_TUBE', 'CONE_METER',
#                 'WEDGE_METER', 'ISO_15377_CONICAL_ORIFICE',
#                 'MILLER_CONICAL_ORIFICE',
#                 'MILLER_QUARTER_CIRCLE_ORIFICE',
#                 'ISO_15377_QUARTER_CIRCLE_ORIFICE', 'UNSPECIFIED_METER',
#                 'HOLLINGSHEAD_ORIFICE', 'HOLLINGSHEAD_CONE', 'HOLLINGSHEAD_WEDGE',
#                 'HOLLINGSHEAD_VENTURI_SMOOTH', 'HOLLINGSHEAD_VENTURI_SHARP'])

# __all__.extend(['ORIFICE_CORNER_TAPS', 'ORIFICE_FLANGE_TAPS',
#                 'ORIFICE_D_AND_D_2_TAPS', 'ORIFICE_PIPE_TAPS',
#                 'ORIFICE_VENA_CONTRACTA_TAPS', 'TAPS_OPPOSITE', 'TAPS_SIDE'])

# __all__.extend(['CONCENTRIC_ORIFICE', 'ECCENTRIC_ORIFICE',
#                 'CONICAL_ORIFICE', 'SEGMENTAL_ORIFICE',
#                 'QUARTER_CIRCLE_ORIFICE'])

# The below is specified at: https://fluids.readthedocs.io/fluids.flow_meter.html?highlight=eccentric%20orifice#flow-meter-solvers


Meter_Type = [  'conical orifice', 'orifice', 'machined convergent venturi tube', 
                'ISO 5167 orifice', 'Miller quarter circle orifice', 'Hollingshead venturi sharp', 
                'segmental orifice', 'Miller conical orifice', 'Miller segmental orifice', 
                'quarter circle orifice', 'Hollingshead v cone', 'wedge meter', 'eccentric orifice', 
                'venuri nozzle', 'rough welded convergent venturi tube', 'ISA 1932 nozzle', 
                'ISO 15377 quarter-circle orifice', 'Hollingshead venturi smooth', 
                'Hollingshead orifice', 'cone meter', 'Hollingshead wedge', 'Miller orifice', 
                'long radius nozzle', 'ISO 15377 conical orifice', 'unspecified meter', 
                'as cast convergent venturi tube', 'Miller eccentric orifice', 
                'ISO 15377 eccentric orifice'
            ]

Tap_Position = ['180 degree','90 degree']

Tap_Type = ['corner', 'flange', 'D', 'D/2']