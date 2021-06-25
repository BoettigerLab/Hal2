#!/usr/bin/env python
"""
HAL module for controlling a ASI illumina stage.

Hazen 05/17
"""
import math
from PyQt5 import QtCore

import storm_control.hal4000.halLib.halMessage as halMessage

import storm_control.sc_hardware.baseClasses.stageModule as stageModule
import storm_control.sc_hardware.appliedScientificInstrumentation.illuminaStage as iStage


class AsiStageFunctionality(stageModule.StageFunctionalityNF):  # NF

    def calculateMoveTime(self, dx, dy):
        """
        We assume that this stage can move at 10mm / second.  We add an extra 
        second as this seems to be how long it takes for the command to get to 
        the stage and for the stage to settle after the move.
        """
        time_estimate = math.sqrt(dx*dx + dy*dy)/100.0 + 1.0
        print("> stage move time estimate is {0:.3f} seconds".format(time_estimate))
        return time_estimate
    

class AsiStageRS232(stageModule.StageModule):

    def __init__(self, module_params = None, qt_settings = None, **kwds):
        super().__init__(**kwds)
        
        configuration = module_params.get("configuration")
        self.stage = iStage.MS2000(port = configuration.get("com_port"))

        if self.stage.getStatus():
            # self.stage.setVelocity(10000,10000)
            self.stage_functionality = AsiStageFunctionality(device_mutex = QtCore.QMutex(),
                                                              stage = self.stage,
                                                              update_interval = 1000)
        else:
            self.stage = None