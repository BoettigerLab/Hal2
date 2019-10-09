#!/usr/bin/env python
"""
USB interface to a Thorlabs stage: BBD103 controller, MLS203 stage.

Hazen 04/17
"""
import traceback

# Because Python paths never work correctly for me because of stupidity, we are stuck with ugly hacks: 
import sys
sys.path.append(r'C:\Users\Scope3\Desktop\MicroscopeHardware\Thorlabs\ThirdPartyPython\PyAPT') # needed

# end ugly hack
from PyAPT import APTMotor

# import storm_control.sc_hardware.serial.RS232 as RS232 # not used
# import storm_control.sc_library.hdebug as hdebug
import time

class BBD103():
    """
    Thorlabs USB interface to BBD103 controller for a MLS203 stage
    """
    def __init__(self,sn_motor1=94832870,sn_motor2=94832869, **kwds):
        """
        Connect to the thorlabs stage at the specified port.
        """
        self.live = True
        self.unit_to_um = 1000.0  # units are mm
        self.um_to_unit = 1.0/self.unit_to_um
        self.x = 0.0
        self.y = 0.0
        
        # sn_motor1 = 94832870
        # sn_motor2 = 94832869
        self.Motor1 = APTMotor(sn_motor1, HWTYPE=44)  # initialize motor 1 "x"
        self.Motor2 = APTMotor(sn_motor2, HWTYPE=44) # initizalize motor 2 "y"

    ## getStatus
    #
    # @return True/False if we are actually connected to the stage.
    #
    def getStatus(self):
        return self.live


    def goAbsolute(self, x, y):
        x = x * self.um_to_unit
        y = y * self.um_to_unit
        self.Motor1.mAbs(x) # 
        self.Motor2.mAbs(y) # 

    def goRelative(self, x, y):
        x = x * self.um_to_unit
        y = y * self.um_to_unit
        self.Motor1.mRel(x) # 
        self.Motor2.mRel(y) # 

    def jog(self, x_speed, y_speed):  # shouldn't this also specify a relative position
        vx = x_speed * self.um_to_unit
        vy = y_speed * self.um_to_unit
        self.Motor1.setVel(x_speed)
        self.Motor2.setVel(y_speed)
        
    def joystickOnOff(self, on):
        if on:
            self.writeline("!joy 2")
        else:
            self.writeline("!joy 0")
            
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
            x0 = self.Motor1.getPos() # query single axis
            y0 = self.Motor2.getPos() # query single axis
            return {"x" : x0,
                "y" : y0}

    def serialNumber(self):
        """
        Return the stages serial number.
        """
        return self.Motor1.getHardwareInformation()

    def setVelocity(self, x_vel, y_vel):
        """
        x_vel - The maximum stage velocity allowed in x.
        y_vel - The maximum stage velocity allowed in y.
        I'm not sure this should be allowed to change the max velocity here. 
        """
        pass

    ## shutDown
    #
    # Disconnect from the stage.
    #
    def shutDown(self):
        # Disconnect from the stage (not sure this is correct)
        if self.live:
            self.Motor1.cleanUpAPT()
            self.Motor2.cleanUpAPT()
           

    def zero(self):
        pass


#
# Testing
#
if (__name__ == "__main__"):
    import time

    stage = BBD103(sn_motor1=94832870,sn_motor2=94832869)
    
    def comm(cmd, timeout):
        cmd()
        time.sleep(timeout)
        return stage.readline()
    
    if stage.getStatus():

        # Test communication.
        if False:
            print("SN:", comm(stage.serialNumber, 0.1))
            print("zero:", comm(stage.zero, 0.1))
            print("position:", comm(stage.position, 0.1))
            print("goAbsolute:", comm(lambda: stage.goAbsolute(100,100), 0.5))
            print("position:", comm(stage.position, 0.1))
            print("goRelative:", len(comm(lambda: stage.goRelative(100,100), 0.5)))
            print("position:", comm(stage.position, 0.1))

        # Test whether we can jam up stage communication.
        if True:
            reps = 20
            for i in range(reps):
                print(i)
                stage.position()
                stage.goAbsolute(i*10,0)
                stage.position()
                time.sleep(0.1)

            for i in range(3*reps + 4):
                responses = stage.readline()
                for resp in responses.split("\r"):
                    print(i, resp, len(resp))
            
        stage.shutDown()


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
