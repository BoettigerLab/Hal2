#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Connect to a PI stage using the E873 controller and the Q-545.140 translation stages

Not working yet

using Physik Instrumente (PI) GmbH & Co. KG
sc_hardware.physikInstrumente.E873.py

Alistair Boettiger, April 2019

V1.1
Functional connection to x-y axes of PI piezo stage

To do:
1. Calibrate stage step sizes
2. Provide instructions for installing the PIPython packages
3. Fix the python path stupidity
4. Pass serial numbers as a parameter from  the xml file
"""

from __future__ import print_function
from copy import deepcopy
import storm_control.sc_library.parameters as params

class E873Z():

    ## __init__
    #
    # Connect to the PI E873 stage.
    #
    #
    def __init__(self,z_stage=None, serialnum = '119006811'):   # should become a parameter, see other stages
        # print('self')
        # print(self.__dict__)
        # print('z_stage')
        # print(z_stage.__dict__)
        if not z_stage.live:
            self = E873connect(serialnum)
        else:
            # self = stage; # this doesn't work
            # this slow process does work: 
            self.pidevice = z_stage.pidevice        
            self.wait = z_stage.wait
            self.unit_to_um = z_stage.unit_to_um
            self.um_to_unit = z_stage.um_to_unit
            self.live = z_stage.live
            self.rangemin = z_stage.rangemin
            self.rangemax = z_stage.rangemax
            self.curpos = z_stage.curpos      
            print('self2')
            print(self.__dict__)

    ## getStatus
    #
    # @return True/False if we are actually connected to the stage.
    #
    def getStatus(self):
        return self.live
 
    def goAbsolute(self, z):
        if self.live:
            z0 = self.pidevice.qPOS(3)[3]  # query single axis [need to check units]
                # position = pidevice.qPOS()[str(axis)] # query all axes
            Z = z * self.um_to_unit
            if Z > self.rangemin['3'] and Z < self.rangemax['3']:
                self.pidevice.MOV(3, Z)
            else:
                print('requested move outside max range!')
     
    def goRelative(self, dz):
        if self.live:
            z0 = self.pidevice.qPOS(3)[3]  # query single axis [need to check units]
                # position = pidevice.qPOS()[str(axis)] # query all axes
            Z = z0 + dz * self.um_to_unit
            if Z > self.rangemin['3'] and Z < self.rangemax['3']:
                self.pidevice.MOV(3, Z)
            else:
                print('requested move outside max range!')
         

    ## position
    #
    # @return [stage x (um), stage y (um), stage z (um)]
    #
    def position(self):
        if self.live:
            z0 = self.pidevice.qPOS(3)[3]  # query single axis
            print('current position')
            print(z0)
            return z0# {"z" : z0}
            
    def getMinimum(self):
        return self.rangemin
        
    def getMaximum(self):
        return self.rangemax
            

   