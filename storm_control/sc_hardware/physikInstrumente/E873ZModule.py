#!/usr/bin/env python
"""
HAL module for controlling a PI stage.
adapted from Ludl stage control
Alistair 10/19
"""
import math
from PyQt5 import QtCore

import storm_control.hal4000.halLib.halMessage as halMessage
import storm_control.sc_hardware.baseClasses.stageZModule as stageZModule
import storm_control.sc_hardware.physikInstrumente.E873Z as E873Z



class E873ZStageFunctionality(stageZModule.ZStageFunctionalityBuffered):  # should use the non NF version - this no feedback version SLOWS the stage!
    # This just inhereits directly 
    print('initializing Z-stage')

class E873ZStage(stageZModule.ZStage):

    def __init__(self, module_params = None, qt_settings = None, **kwds):  # this should probably take some parameters?    
        super().__init__(**kwds)
        configuration = module_params.get("configuration")
        serialnum = configuration.get("serialnum")
        print('searching for stage controller SN: ', serialnum)
        self.stage = E873Z.E873Z(serialnum)
        print('connected to stage controller SN: ', serialnum)

        if self.stage.getStatus():
            # self.stage.setVelocity(10000,10000)
            self.stage_functionality = E873ZStageFunctionality(self.stage,
                                                               device_mutex = QtCore.QMutex())
                                                              
        else:
            self.stage = None

            
                       
            