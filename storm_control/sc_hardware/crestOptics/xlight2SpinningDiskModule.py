#!/usr/bin/env python
"""
HAL module to interface with the Crest spinning disk

Alistair Boettiger 6/2021
"""

import storm_control.hal4000.halLib.halMessage as halMessage

import storm_control.sc_hardware.baseClasses.hardwareModule as hardwareModule
import storm_control.sc_hardware.crestOptics.xlight2SpinningDisk as xlight2SpinningDisk

import storm_control.sc_library.halExceptions as halExceptions
import storm_control.sc_library.parameters as params


class ConfocalControl(object):
    """
    Control of the spinning disk confocal
	This should possibly be part of the xlight2Spinning disk -- 
	
    """
    def __init__(self, w1 = None, configuration = None, **kwds):
        super().__init__(**kwds)
        self.w1 = w1

        assert max_speed is not None

        # Create dictionaries for the configuration of the
        # filter wheels and two dichroic mirror sets.
        self.filter_wheel_1_config = {}
        values = configuration.get("filter_wheel_1")
        filter_names = values.split(",")
        for pos, filter_name in enumerate(filter_names):
            self.filter_wheel_1_config[filter_name] = pos + 1

        self.dichroic_mirror_config = {}
        values = configuration.get("dichroic_mirror")
        dichroic_names = values.split(",")
        for pos, dichroic_name in enumerate(dichroic_names):
            self.dichroic_mirror_config[dichroic_name] = pos + 1


        # Create parameters
        self.parameters = params.StormXMLObject()

        self.parameters.add(params.ParameterSetBoolean(description = "Bypass spinning disk for brightfield mode?",
                                                       name = "bright_field_bypass",
                                                       value = False))

        self.parameters.add(params.ParameterSetBoolean(description = "Spin the disk?",
                                                       name = "spin_disk",
                                                       value = True))
        
        # Disk properties
        self.parameters.add(params.ParameterSetString(description = "Disk pinhole size",
                                                      name = "disk",
                                                      value = "70-micron pinholes",
                                                      allowed = ["70-micron pinholes", "40-micron pinholes"]))

        # Dichroic mirror position
        values = sorted(self.dichroic_mirror_config.keys())
        self.parameters.add(params.ParameterSetString(description = "Dichroic mirror position (1-5)",
                                                      name = "dichroic_mirror",
                                                      value = values[0],
                                                      allowed = values))

        # Filter wheel positions
        values = sorted(self.filter_wheel_1_config.keys())
        self.parameters.add(params.ParameterSetString(description = "Camera 1 Filter Wheel Position (1-8)",
                                                      name = "filter_wheel_pos1",
                                                      value = values[0],
                                                      allowed = values))


        self.newParameters(self.parameters, initialization = True)

    def getParameters(self):
        return self.parameters
    
    def newParameters(self, parameters, initialization = False):

        if initialization:
            changed_p_names = parameters.getAttrs()
        else:
            changed_p_names = params.difference(parameters, self.parameters)

        p = parameters
        for pname in changed_p_names:
            print(pname)
            # Update our current parameters.
            self.parameters.setv(pname, p.get(pname))

            # Configure the W1.
            if (pname == "bright_field_bypass"):
                if p.get("bright_field_bypass"):
                    self.w1.commandResponse("D0", 3)
                else:
                    self.w1.commandResponse("D1", 3)

            elif (pname == "spin_disk"):
                if p.get("spin_disk"):
                    self.w1.commandResponse("N1", 1)
                else:
                    self.w1.commandResponse("N0", 1)
                    
            elif (pname == "disk"):
                if (p.get("disk") == "70-micron pinholes"):
                    r = self.w1.commandResponse("D1", 3)
                elif (p.get("disk") == "40-micron pinholes"):
                    r = self.w1.commandResponse("D2", 3)
                print("changing disk")
                print(r)

            elif (pname == "dichroic_mirror"):
                dichroic_num = self.dichroic_mirror_config[p.get("dichroic_mirror")]
                self.w1.commandResponse("D"+str(dichroic_num), 1)

            elif (pname == "filter_wheel_pos1"):
                filter1_num = self.filter_wheel_1_config[p.get("filter_wheel_pos1")]
                print("updating filter wheel position")
                self.w1.commandResponse("B" + str(filter1_num) , 1) 

            else:
                print(">> Warning", str(pname), " is not a valid parameter for the Confocal")


class Xlight2Module(hardwareModule.HardwareModule):

    def __init__(self, module_params = None, qt_settings = None, **kwds):
        super().__init__(**kwds)
        self.control = None
        self.w1 = None

        configuration = module_params.get("configuration")
        self.w1 = xlight2SpinningDisk.Xligh2SpinningDisk(baudrate = 9600,
                                                port = configuration.get("port"),
												end_of_line = "\r",
												encoding = 'utf-8')
        if self.w1.getStatus():
            self.control = ConfocalControl(w1 = self.w1,
                                     configuration = configuration)

    def cleanUp(self, qt_settings):
        if self.control is not None:
            self.w1.shutDown()

    def processMessage(self, message):
        if self.control is None:
            return
        if message.isType("configure1"):
            self.sendMessage(halMessage.HalMessage(m_type = "initial parameters",
                                                   data = {"parameters" : self.control.getParameters()}))

        #
        # FIXME? Maybe we want do this at 'update parameters' as we don't
        #        do any error checking.
        #
        elif message.isType("new parameters"):
            hardwareModule.runHardwareTask(self,
                                           message,
                                           lambda : self.updateParameters(message))

    def updateParameters(self, message):
        message.addResponse(halMessage.HalMessageResponse(source = self.module_name,
                                                          data = {"old parameters" : self.control.getParameters().copy()}))
        p = message.getData()["parameters"].get(self.module_name)
        self.control.newParameters(p)
        message.addResponse(halMessage.HalMessageResponse(source = self.module_name,
                                                          data = {"new parameters" : self.control.getParameters()}))

#
# The MIT License
#
# Copyright (c) 2017 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
