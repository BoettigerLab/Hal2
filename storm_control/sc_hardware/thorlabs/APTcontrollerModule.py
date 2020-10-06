#!/usr/bin/env python
"""
HAL module for controlling a Thorlabs KDC101 controlled stage stage.

Alistair, Sept 2020
lifted from marzhauser controller that was working for scope3

SeeL https://github.com/qpit/thorlabs_apt/blob/master/thorlabs_apt/core.py
Not currently working
"""

from PyQt5 import QtCore
import storm_control.hal4000.halLib.halMessage as halMessage
import storm_control.sc_hardware.baseClasses.stageModule as stageModule
import storm_control.sc_hardware.thorlabs.APTcontroller as APTcontroller # was marzhauser 


class APTcontrollerStageFunctionality(stageModule.StageFunctionalityNF):  # note the "NF" module (no feedback), unlike the Marzhauser

    def calculateMoveTime(self, dx, dy):
        """
        We assume that this stage can move at 10mm / second.  We add an extra 
        second as this seems to be how long it takes for the command to get to 
        the stage and for the stage to settle after the move.
		
		We should be able to poll this stage directly with feedback (requires)
		motor.is_in_motion
        """
        time_estimate = math.sqrt(dx*dx + dy*dy)/10000.0 + 1.0
        print("> stage move time estimate is {0:.3f} seconds".format(time_estimate))
        return time_estimate
    

class APTcontrollerStage(stageModule.StageModule):
    """
    USB connection through KDC101Stage
    """
    def __init__(self, module_params = None, qt_settings = None, **kwds):
        super().__init__(**kwds)

        configuration = module_params.get("configuration")
        self.stage = APTcontroller.APTcontroller(xStageSN = configuration.get("xStageSN"),
                                                yStageSN = configuration.get("yStageSN"))  #  RS232 stage 
                                                                                         
        if self.stage.getStatus():
            # # Set (maximum) stage velocity.
            # velocity = configuration.get("velocity")  [let's use Thorlabs defaults for now]. 
            # self.stage.setVelocity(velocity, velocity)
            self.stage_functionality = APTcontrollerStageFunctionality(device_mutex = QtCore.QMutex(),
                                                                    stage = self.stage,
                                                                    update_interval = 10)  # update interval dropped to 10

        else:
            self.stage = None


