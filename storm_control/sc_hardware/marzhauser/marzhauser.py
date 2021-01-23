#!/usr/bin/env python
"""
RS232 interface to a Marzhauser stage.

Hazen 04/17

2019 - Alistair
Added back Tango controller

"""
from ctypes import *
import sys, os
import time

import traceback
import storm_control.sc_library.hdebug as hdebug
import storm_control.sc_hardware.serial.RS232 as RS232

tango = 0

def loadTangoDLL():
    global tango
    if (tango == 0):
        tangoPath = r'C:\Users\Scope3\Desktop\MicroscopeHardware\Marzhauser'
        dllname = tangoPath + '\Tango_DLL.dll'
        if not os.path.exists(dllname):
            print("ERROR: DLL not found")
        tango = windll.LoadLibrary(dllname)     
instantiated = 0



class MarzhauserRS232(RS232.RS232):
    """
    Marzhauser RS232 interface class.
    """
    def __init__(self, **kwds):
        """
        Connect to the Marzhauser stage at the specified port.
        """
        self.live = True
        self.unit_to_um = .10 # 1/1000 (think this is mm)  1000.0 this is nm
        self.um_to_unit = 1.0/self.unit_to_um
        self.x = 0.0
        self.y = 0.0

        # RS232 stuff
        try:
            super().__init__(**kwds)
            test = self.commWithResp("?version")
            print('version: ' )
            print(test)
            if not test:
                self.live = False
            else:
                print("Connected to the Marzhauser stage at port", kwds["port"])

        except (AttributeError, AssertionError):
            print(traceback.format_exc())
            self.live = False
            print("Marzhauser Stage is not connected? Stage is not on?")
            print("Failed to connect to the Marzhauser stage at port", kwds["port"])

    def goAbsolute(self, x, y):
        x = x * self.um_to_unit
        y = y * self.um_to_unit
        self.writeline(" ".join(["!moa", str(x), str(y)])) 

    def goRelative(self, x, y):
        x = x * self.um_to_unit
        y = y * self.um_to_unit
        self.writeline(" ".join(["!mor", str(x), str(y)]))

    def jog(self, x_speed, y_speed):
        vx = x_speed * self.um_to_unit
        vy = y_speed * self.um_to_unit
        self.writeline(" ".join(["!speed ", str(vx), str(vy)]))
        
    def joystickOnOff(self, on):
        if on:
            self.writeline("!joy 2")
        else:
            self.writeline("!joy 0")

    def position(self):
        self.writeline("?pos") 


    def serialNumber(self):
        """
        Return the stages serial number.
        """
        return self.writeline("?readsn")

    def setVelocity(self, x_vel, y_vel):
        self.writeline(" ".join(["!vel",str(x_vel),str(y_vel)]))
    
    def setAcceleration(self, x_accel, y_accel):
        self.writeline(" ".join(["!accel",str(x_accel),str(y_accel)]))

    def zero(self):
        self.writeline("!pos 0 0")
        print('Re-zeroing the stage')


class MarzhauserTango():

    ## __init__
    #
    # Connect to the Marzhuaser stage using the tango library.
    #
    # @param port A RS-232 com port name such as "COM1".
    #
    def __init__(self, port):
        self.wait = 1 # move commands wait for motion to stop
        self.unit_to_um = 1000  # 10000
        self.um_to_unit = 1.0/self.unit_to_um


        # Load the Tango library.
        loadTangoDLL()
        
        # Check that this class has not already been instantiated.
        global instantiated
        assert instantiated == 0, "Attempt to instantiate two Marzhauser stage classes."
        instantiated = 1

        # Connect to the stage.
        self.good = 1
        temp = c_int(-1)
        tango.LSX_CreateLSID(byref(temp))
        self.LSID = temp.value
        print('attempting to connect to Marzhuaser stage on '+ port)
        byte_port = bytes(port, 'utf-8') # This works in Python27 and not Python3. Possible a byte string error, maybe this fixes it. 
        error = tango.LSX_ConnectSimple(self.LSID, 1, byte_port, 57600, 0)
        if error:
            print("Marzhauser error", error)
            self.good = 0
        else:
            print('connected to Marzhauser stage on '+port)

    ## getStatus
    #
    # @return True/False if we are actually connected to the stage.
    #
    def getStatus(self):
        return self.good

    ## goAbsolute
    #
    # @param x Stage x position in um.
    # @param y Stage y position in um.
    #
    def goAbsolute(self, x, y):
        if self.good:
            # If the stage is currently moving due to a jog command
            # and then you try to do a positional move everything
            # will freeze, so we stop the stage first.
            self.jog(0.0,0.0)
            X = c_double(x * self.um_to_unit)
            Y = c_double(y * self.um_to_unit)
            ZA = c_double(0.0)
            tango.LSX_MoveAbs(self.LSID, X, Y, ZA, ZA, self.wait)

    ## goRelative
    #
    # @param dx Amount to displace the stage in x in um.
    # @param dy Amount to displace the stage in y in um.
    #
    def goRelative(self, dx, dy):
        if self.good:
            self.jog(0.0,0.0)
            dX = c_double(dx * self.um_to_unit)
            dY = c_double(dy * self.um_to_unit)
            dZA = c_double(0.0)
            tango.LSX_MoveRel(self.LSID, dX, dY, dZA, dZA, self.wait)

    ## jog
    #
    # @param x_speed Speed to jog the stage in x in um/s.
    # @param y_speed Speed to jog the stage in y in um/s.
    #
    def jog(self, x_speed, y_speed):
        if self.good:
            c_xs = c_double(x_speed * self.um_to_unit)
            c_ys = c_double(y_speed * self.um_to_unit)
            c_zr = c_double(0.0)
            tango.LSX_SetDigJoySpeed(self.LSID, c_xs, c_ys, c_zr, c_zr)

    ## joystickOnOff
    #
    # @param on True/False enable/disable the joystick.
    #
    def joystickOnOff(self, on):
        if self.good:
            if on:
                tango.LSX_SetJoystickOn(self.LSID, 1, 1)
            else:
                tango.LSX_SetJoystickOff(self.LSID)

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
        if self.good:
            pdX = c_double()
            pdY = c_double()
            pdZ = c_double()
            pdA = c_double()
            tango.LSX_GetPos(self.LSID, byref(pdX), byref(pdY), byref(pdZ), byref(pdA))
            return [pdX.value * self.unit_to_um, 
                    pdY.value * self.unit_to_um,
                    pdZ.value * self.unit_to_um]
            print('position')
        else:
            return [0.0, 0.0, 0.0]


    ## serialNumber
    #
    # @return The stage serial number.
    #
    def serialNumber(self):
        # Get stage serial number
        if self.good:
            serial_number = create_string_buffer(256)
            tango.LSX_GetSerialNr(self.LSID, serial_number, 256)
            return repr(serial_number.value)
        else:
            return "NA"

    ## setVelocity
    #
    # FIXME: figure out how to set velocity..
    #
    def setVelocity(self, x_vel, y_vel):
        pass

    ## shutDown
    #
    # Disconnect from the stage.
    #
    def shutDown(self):
        # Disconnect from the stage
        if self.good:
            tango.LSX_Disconnect(self.LSID)
        tango.LSX_FreeLSID(self.LSID)

        global instantiated
        instantiated = 0

    ## zero
    #
    # Set the current position as the new zero position.
    #
    def zero(self):
        if self.good:
            self.jog(0.0,0.0)
            x = c_double(0)
            tango.LSX_SetPos(self.LSID, x, x, x, x)




#
# Testing
#
if (__name__ == "__main__"):
    import time

    stage = MarzhauserRS232(port = "COM1", baudrate = 57600)
    
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
