#!/usr/bin/env python
"""
HAL module for controlling a Marzhauser stage.
Hazen 04/17
"""
import re
import time

from PyQt5 import QtCore

import storm_control.hal4000.halLib.halMessage as halMessage

import storm_control.sc_hardware.baseClasses.stageModule as stageModule
import storm_control.sc_hardware.appliedScientificInstrumentation.illuminaStage as iStage


class AsiStageFunctionality(stageModule.StageFunctionality):
    """
    These stages are nice because they respond quickly to commands
    and they also provide feedback about whether or not they are
    moving.
    """
    def __init__(self, update_interval = None, **kwds):
        super().__init__(**kwds)
        # self.querying = False

        # Each time this timer fires we'll 'query' the stage for it's
        # current position.
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.setInterval(update_interval)
        self.updateTimer.setSingleShot(True)
        self.updateTimer.timeout.connect(self.handleUpdateTimer)
        self.updateTimer.start()

        # Connect to our own stagePosition signal in order to store
        # the current position.
        self.stagePosition.connect(self.handleStagePosition)
        
        self.pos_dict = self.stage.position()
        self.stagePosition.emit(self.pos_dict) # added 
        print('init stage position')
        print(self.pos_dict)
        
        # This thread will poll the serial port for responses from
        # the stage to the commands we're sending.
        self.polling_thread = AsiPollingThread(device_mutex = self.device_mutex,
                                                      is_moving_signal = self.isMoving,
                                                      sleep_time = 100,
                                                      stage = self.stage,
                                                      stage_position_signal = self.stagePosition)
        self.polling_thread.startPolling()

    def goAbsolute(self, x, y):
        #
        # Debugging all removal of stage position queries.  ??
        # (absolute moves are not working without this)
        super().goAbsolute(x,y)
        self.pos_dict["x"] = x
        self.pos_dict["y"] = y
        self.stagePosition.emit(self.pos_dict)
        
    def goRelative(self, dx, dy):  # added 1/26/21
        #
        # Debugging all removal of stage position queries.
        #
        super().goRelative(dx,dy)
        self.pos_dict["x"] = self.pos_dict["x"] + dx
        self.pos_dict["y"] = self.pos_dict["y"] + dy
        self.stagePosition.emit(self.pos_dict)

        
    def handleStagePosition(self, pos_dict):
        self.pos_dict = self.stage.position() # swapped
        # self.pos_dict = pos_dict
        #self.querying = False

    
    def handleUpdateTimer(self):
        """
        Query the stage for its current position.
        """
        #
        # The purpose of the self.querying flag is to prevent build up of
        # position update requests. If there is already one in process there
        # is no point in starting another one.
        #
        # if not self.querying:
        #     self.querying = True
        #     self.mustRun(task = self.stage.position)
        self.maybeRun(task = self.stage.position)

    def wait(self):
        self.updateTimer.stop()
        self.polling_thread.stopPolling()
        super().wait()


class AsiPollingThread(QtCore.QThread):
    """
    Handles polling the A stage for responses to 
    serial commands.
    """
    def __init__(self,
                 device_mutex = None,
                 is_moving_signal = None,
                 sleep_time = None,
                 stage = None,
                 stage_position_signal = None,
                 **kwds):
        super().__init__(**kwds)
        self.device_mutex = device_mutex
        self.is_moving_signal = is_moving_signal
        self.pos_dict = {}
        self.pos_regex = re.compile('([\d\-]+[\.][\d]+) ([\d\-]+[\.][\d]+)')
        self.sleep_time = sleep_time         
        self.stage = stage
        self.stage_position_signal = stage_position_signal

    def run(self):
        self.running = True
        while(self.running):
            self.device_mutex.lock()
            responses = self.stage.isBusy()
            self.device_mutex.unlock()
            if responses is None:
                continue
            
            # Parse response. The expectation is that it is one of two things:
            #
            # (1) A status string like "#@--" that indicates that the stage
            #     is or is not moving (statusaxis).
            #
            # (2) The current position "X.XX Y.YY ..".
            #

            time_str = str(time.time())
            for resp in responses.split("\r"):

                # The response was no response. Not sure where these come from.
                if (len(resp) == 0):
                    continue
                
                # Check for 'statusaxis' response form.
                if 'B' in resp :
                    self.is_moving_signal.emit(True)
                else:
                    self.is_moving_signal.emit(False)
                continue 
                
            # Sleep for ~ x milliseconds.
            self.msleep(self.sleep_time)

    def startPolling(self):
        self.start(QtCore.QThread.NormalPriority)

    def stopPolling(self):
        self.running = False
        self.wait()
        


class AsiStageRS232(stageModule.StageModule):

    def __init__(self, module_params = None, qt_settings = None, **kwds):
        super().__init__(**kwds)
        
        configuration = module_params.get("configuration")
        self.stage = iStage.MS2000(port = configuration.get("com_port"))

        if self.stage.getStatus():
            # self.stage.setVelocity(10000,10000)
            self.stage_functionality = AsiStageFunctionality(device_mutex = QtCore.QMutex(),
                                                              stage = self.stage,
                                                              update_interval = 500)
        else:
            self.stage = None