#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Connect to a PI stage using the E873 controller and the Q-545.140 translation stages

using Physik Instrumente (PI) GmbH & Co. KG
sc_hardware.physikInstrumente.E873.py

Alistair Boettiger, April 2019

V1.1
Functional connection to x-y axes of PI piezo stage

To do:
1. Calibrate stage step sizes
2. Provide instructions for installing the PIPython packages
3. Fix the python path stupidity
4. Pass serial numbers as a parameter from  the xml file [DONE]
"""


from __future__ import print_function

# Because Python paths never work correctly for me because of stupidity, we are stuck with ugly hacks: 
import sys
sys.path.append(r'C:\Users\Scope3\Desktop\MicroscopeHardware\PI\PIPython-1.5.1.7 for E-873.3QTU\PIPython-1.5.1.7')
# end ugly hack

from copy import deepcopy

import storm_control.sc_library.parameters as params

from pipython import GCSDevice, pitools

CONTROLLERNAME = 'E-873.3QTU'  # 'C-884' will also work
STAGES = ['Q-545.140', 'Q-545.140','Q-545.140']  # , 'Q-545.140',
REFMODES = 'FRF' # ['FNL', 'FRF']



class E873connect():

    ## __init__
    #
    # Connect to the PI E873 stage.
    #
    #
    def __init__(self, serialnum = '119006811'):   # should become a parameter, see other stages
        print(serialnum)
    
        # Connect to the PI E873 stage.
        # with GCSDevice(CONTROLLERNAME) as pidevice:    
        pidevice = GCSDevice(CONTROLLERNAME) 
        pidevice.ConnectUSB(serialnum) #   pidevice.ConnectUSB(serialnum='119006811')
        print('connected: {}'.format(pidevice.qIDN().strip()))

        # Show the version info which is helpful for PI support when there
        # are any issues.

        if pidevice.HasqVER():
            print('version info:\n{}'.format(pidevice.qVER().strip()))

        # In the module pipython.pitools there are some helper
        # functions to make using a PI device more convenient. The "startup"
        # function will initialize your system. There are controllers that
        # cannot discover the connected stages hence we set them with the
        # "stages" argument. The desired referencing method (see controller
        # user manual) is passed as "refmode" argument. All connected axes
        # will be stopped if they are moving and their servo will be enabled.

        print('initialize connected stages...')
        pitools.startup(pidevice, stages=STAGES, refmodes=REFMODES)
        # Now we query the allowed motion range and current position of all
        # connected stages. GCS commands often return an (ordered) dictionary
        # with axes/channels as "keys" and the according values as "values".

        self.pidevice = pidevice
        
        self.wait = 1 # move commands wait for motion to stop
        self.unit_to_um = 100.0 # needs calibration
        self.um_to_unit = 1.0/self.unit_to_um


        # Connect to the stage.
        self.live = True

        # get min and max range
        self.rangemin = pidevice.qTMN()
        self.rangemax = pidevice.qTMX()
        self.curpos = pidevice.qPOS()       
    #
    # Disconnect from the stage.
    #
    def shutDown(self):
        # Disconnect from the stage
        if self.live:
            self.pidevice.StopAll(noraise=True)
            pitools.waitonready(self.pidevice)  # there are controllers that need some time to halt all axes

