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
from copy import deepcopy
import storm_control.sc_library.parameters as params

class E873xy():
    ## __init__
    #
    # Connect to the PI E873 stage.
    #
    #
    def __init__(self,stage=None,serialnum = '119006811'):   # should become a parameter, see other stages
        # print('self')
        # print(self.__dict__)
        # print('stage')
        # print(stage.__dict__)
        if not stage.live:
            self = E873connect(serialnum)
        else:
            # self = stage; # this doesn't work
            # this slow process does work: 
            self.pidevice = stage.pidevice        
            self.wait = stage.wait
            self.unit_to_um = stage.unit_to_um
            self.um_to_unit = stage.um_to_unit
            self.live = stage.live
            self.rangemin = stage.rangemin
            self.rangemax = stage.rangemax
            self.curpos = stage.curpos      
            print('self2')
            print(self.__dict__)
            
        

    ## getStatus
    #
    # @return True/False if we are actually connected to the stage.
    #
    def getStatus(self):
        return self.live

    ## goAbsolute
    #
    # @param x Stage x position in um.
    # @param y Stage y position in um.
    #
    def goAbsolute(self, x, y):
        if self.live:
            # If the stage is currently moving due to a jog command
            # and then you try to do a positional move everything
            # will freeze, so we stop the stage first.
            # self.jog(0.0,0.0)
            X = x * self.um_to_unit
            Y = y * self.um_to_unit
            if X > self.rangemin['1'] and X < self.rangemax['1']:
                self.pidevice.MOV(1, X)
            else:
                print('requested move outside max range!')
            if Y > self.rangemin['2'] and Y < self.rangemax['2']:
                self.pidevice.MOV(2, Y)
            else:
                print('requested move outside max range!')

    ## goRelative
    #
    # @param dx Amount to displace the stage in x in um.
    # @param dy Amount to displace the stage in y in um.
    #
    def goRelative(self, dx, dy):
        if self.live:
            # self.jog(0.0,0.0)
            x0 = self.pidevice.qPOS(1)[1]  # query single axis [need to check units]
            y0 = self.pidevice.qPOS(2)[2]  # query single axis
                # position = pidevice.qPOS()[str(axis)] # query all axes
            X = x0 + dx * self.um_to_unit
            Y = y0 + dy * self.um_to_unit
            if X > self.rangemin['1'] and X < self.rangemax['1']:
                self.pidevice.MOV(1, X)
            else:
                print('requested move outside max range!')
            if Y > self.rangemin['2'] and Y < self.rangemax['2']:
                self.pidevice.MOV(2, Y)
            else:
                print('requested move outside max range!')
            # pitools.waitontarget(self.pidevice, axes=1) # actively hold on target
            # pitools.waitontarget(self.pidevice, axes=2) # actively hold on target
     
     

    ## jog
    #
    # @param x_speed Speed to jog the stage in x in um/s.
    # @param y_speed Speed to jog the stage in y in um/s.
    #
    def jog(self, x_speed, y_speed):
        pass

    ## joystickOnOff
    #
    # @param on True/False enable/disable the joystick.
    #
    def joystickOnOff(self, on):
        pass


    ## lockout
    #
    # Calls joystickOnOff.
    #
    # @param flag True/False.
    #
    def lockout(self, flag):
        self.joystickOnOff(not flag)

    ## position
    #
    # @return [stage x (um), stage y (um), stage z (um)]
    #
    def position(self):
        if self.live:
            x0 = self.pidevice.qPOS(1)[1]  # query single axis
            y0 = self.pidevice.qPOS(2)[2]  # query single axis
            return {"x" : x0,
                "y" : y0}

            

    ## setVelocity
    #
    # FIXME: figure out how to set velocity..
    #
    def setVelocity(self, x_vel, y_vel):
        pass

   