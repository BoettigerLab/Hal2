#!/usr/bin/env python
"""
HAL module for controlling a PI stage.
adapted from Ludl stage control Module by Hazen
Alistair 10/19
"""
import math
from PyQt5 import QtCore

# this was from the original xy only version of the code:
import storm_control.hal4000.halLib.halMessage as halMessage
import storm_control.sc_hardware.baseClasses.stageModule as stageModule
import storm_control.sc_hardware.physikInstrumente.E873 as E873  # creates connection and handles move commands

# these are just for separating the xy and z functions and trying to share the controller
import storm_control.sc_hardware.baseClasses.stageZModule as stageZModule
import storm_control.sc_hardware.physikInstrumente.E873connect as E873connect # separate connection
import storm_control.sc_hardware.physikInstrumente.E873xy as E873xy # takes connection object and handles move commands in xy
import storm_control.sc_hardware.physikInstrumente.E873Z as E873Z # takes connection object and handles move commands in z

# This is supposed to be a shared variable, but it doesn't work.
PISTAGE = False  

class E873StageFunctionality(stageModule.StageFunctionalityNF):  
    """
    Tried non-NF version. Stage moves, but does not report stage position 
    This works with the E873Stage function below for connecting to an xy stage
    whyen not using a z-stage.
    """
    def calculateMoveTime(self, dx, dy):
        """
        FIXME:  I think this whole def can be removed
        We assume that this stage can move at 10mm / second.  We add an extra 
        second as this seems to be how long it takes for the command to get to 
        the stage and for the stage to settle after the move.
        """
        time_estimate = math.sqrt(dx*dx + dy*dy)/10000.0 + 1.0
        print("> stage move time estimate is {0:.3f} seconds".format(time_estimate))
        return time_estimate
    


class E873Stage(stageModule.StageModule):
    """ this works to connect the xy stage """
    def __init__(self, module_params = None, qt_settings = None, **kwds):  # this should probably take some parameters?
        super().__init__(**kwds)
        print('xy stage')
        print(module_params)
        configuration = module_params.get("configuration")
        serialnum = configuration.get("serialnum")
        print('searching for stage controller SN: ', serialnum)
        self.stage = E873.E873(serialnum)
        print('connected to stage controller SN: ', serialnum)

        if self.stage.getStatus():
            self.stage_functionality = E873StageFunctionality(device_mutex = QtCore.QMutex(),
                                                              stage = self.stage,
                                                              update_interval = 500) 
                                                             
        else:
            self.stage = None

  

class E873StageXY(stageModule.StageModule):
    """ 
    This class is supposed to connect the xy when the same controller is also used for the z-stage
    If the computer/hal has already connected to the stage (i.e. when the z-stage initiated), this class
    needs to be passed that object (called below "PISTAGE" though this version is not functional). 
    If the stage is not connected yet, it calls the E873connect function (that does work).
    """
    def __init__(self, module_params = None, qt_settings = None, **kwds):  # this should probably take some parameters?
        super().__init__(**kwds)
        if PISTAGE == None:
            configuration = module_params.get("configuration")
            serialnum = configuration.get("serialnum")
            print('searching for stage controller SN: ', serialnum)
            PISTAGE = E873connect.E873connect(serialnum)
        print(self.stage)
        self.stage = E873xy.E873xy(stage = PISTAGE)

        if self.stage.getStatus():
            self.stage_functionality = E873StageFunctionality(device_mutex = QtCore.QMutex(),
                                                              stage = self.stage,
                                                              update_interval = 500) 
                                                              
        else:
            self.stage = None
          
                       

class E873ZStageFunctionality(stageZModule.ZStageFunctionalityBuffered):  
    # This just inherits directly 
    print('initializing Z-stage')

class E873ZStage(stageZModule.ZStage):
    """ 
    This class is supposed to connect the z stage when the same controller is also used for the xy-stage
    I believe Z-stage initiates before XY, and this needs to pass its connection "PISTAGE" forward to the
    xy-stage (that isn't working yet).
    If I remove the conditional statements here, this doesn't give errors, but also doesn't connect.
    """
    def __init__(self, module_params = None, qt_settings = None, **kwds):  # this should probably take some parameters?    
        super().__init__(**kwds)
        """
        if PISTAGE == None:
            configuration = module_params.get("configuration")
            serialnum = configuration.get("serialnum")
            print('searching for stage controller SN: ', serialnum)
            PISTAGE = E873connect.E873connect(serialnum)
        """ 
        configuration = module_params.get("configuration")
        serialnum = configuration.get("serialnum")
        print('searching for stage controller SN: ', serialnum)
        PISTAGE = E873connect.E873connect(serialnum)
        self.z_stage = E873Z.E873Z(z_stage = PISTAGE)

        if self.z_stage.getStatus():
            self.stage_functionality = E873ZStageFunctionality(self.z_stage,
                                                               device_mutex = QtCore.QMutex())
                                                              
        else:
            self.stage = None            