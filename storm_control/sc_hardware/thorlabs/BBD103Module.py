#!/usr/bin/env python
"""
HAL module for controlling a Thorlabs stage: BBD103 controller, MLS203 stage.

Alistair 05/19
"""
import math
from PyQt5 import QtCore

import storm_control.hal4000.halLib.halMessage as halMessage

import storm_control.sc_hardware.baseClasses.stageModule as stageModule
import storm_control.sc_hardware.thorlabs.BBD103stagecontrol as BBD103stage



class BBD103StageFunctionality(stageModule.StageFunctionalityNF):

    def calculateMoveTime(self, dx, dy):
        """
        FIXME:  These should be updated for the particular stage.  Thse are just the values from the Ludl
        We assume that this stage can move at 10mm / second.  We add an extra 
        second as this seems to be how long it takes for the command to get to 
        the stage and for the stage to settle after the move.
        """
        time_estimate = math.sqrt(dx*dx + dy*dy)/10000.0 + 1.0
        print("> stage move time estimate is {0:.3f} seconds".format(time_estimate))
        return time_estimate
    


class BBD103Stage(stageModule.StageModule):

    def __init__(self, module_params = None, qt_settings = None, **kwds):  # this should probably take some parameters?
        super().__init__(**kwds)
        
        configuration = module_params.get("configuration")
        sn_motor1 = configuration.get("sn_motor1")
        sn_motor2 = configuration.get("sn_motor2")
        self.stage = BBD103stage.BBD103(sn_motor1,sn_motor2)
        print('connected to stage controller SN: ', sn_motor1, ' and ', sn_motor2)

        if self.stage.getStatus():
            # self.stage.setVelocity(10000,10000)
            self.stage_functionality = BBD103StageFunctionality(device_mutex = QtCore.QMutex(),
                                                              stage = self.stage,
                                                              update_interval = 500) # what is update_interval?
                                                              # is 'StageFunctionality necessary?
        else:
            self.stage = None