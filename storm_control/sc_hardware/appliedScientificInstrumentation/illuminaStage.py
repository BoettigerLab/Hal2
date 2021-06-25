#!/usr/bin/python
#
## @file
#
# RS232 interface to a Applied Scientific Instrumentation MS2000 stage.
#
# Hazen 06/14
#

import sys
import time

import storm_control.sc_library.hdebug as hdebug

import storm_control.sc_hardware.serial.RS232 as RS232


## MS2000
#
# Applied Scientific Instrumentation MS2000 RS232 interface class.
#
class MS2000(object):

    ## __init__
    #
    # Connect to the MS2000 stage at the specified port.
    #
    # @param port The RS-232 port name (e.g. "COM1").
    # @param wait_time (Optional) How long (in seconds) for a response from the stage.
    #
    def __init__(self, port="COM3", timeout = None, baudrate = 115200, wait_time = 0.05, **kwds):
        super().__init__(**kwds)

        import storm_control.sc_hardware.serial.RS232 as RS232
        
        self.live = True
        self.unit_to_um = 0.1 # units are 1/10 microns according to doc 
        self.um_to_unit = 1.0/self.unit_to_um
        self.x = 1.0
        self.y = 1.0


        # RS232 stuff 
        # RS232.RS232.__init__(self, port, None, 115200, "\r", wait_time)
        self.connection = RS232.RS232(baudrate = baudrate,
                                      end_of_line = "\r",
                                      port = port,
                                      timeout = timeout,
                                      wait_time = wait_time)
                                      
        print('connecting to ASI...')
        isLive = self.connection.getStatus()
        self.connection.sendCommand("2HMC X+ Y+")  # initialize both axis
        
        '''
        print('current stage position')
        test = self.connection.commWithResp("2HW X Y")
        print(test)
        [testX, testY] = test.split(" ")[2:4]
        print(testX)
        print(testY)
        '''
        
        try:
            test = self.connection.commWithResp("2H/")
            if not test:
                self.live = False
        except:
            self.live = False
        if not self.live:
            print("ASI Stage is not connected? Stage is not on?")
        else:
            print("connected to ASI Stage on COM " + port) 

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
            X = x * self.um_to_unit
            Y = y * self.um_to_unit
            print('go absolute')
            print( "2HM X=" + str(X) + " Y=" + str(Y) )
            self.connection.commWithResp("2HM X=" + str(X) + " Y=" + str(Y))   # not sure these are working
            currPos = self.connection.commWithResp("2HW X Y")
            print(currPos)
        else:
            print('error. is stage connected?')

    ## goRelative
    #
    # @param x Amount to move the stage in x in um.
    # @param y Amount to move the stage in y in um.
    #
    def goRelative(self, x, y):
        if self.live:
            X = x * self.um_to_unit
            Y = y * self.um_to_unit
            print('go relative')
            print( "2HR X=" + str(X) + " Y=" + str(Y) )
            self.connection.commWithResp("2HR X=" + str(X) + " Y=" + str(Y)) # these work 
            currPos = self.connection.commWithResp("2HW X Y")
            print(currPos)
        else:
            print('error. is stage connected?')

    ## jog
    #
    # @param x_speed Speed to jog the stage in x in um/s.
    # @param y_speed Speed to jog the stage in y in um/s.
    #
    def jog(self, x_speed, y_speed):
        if self.live:
            vx = x_speed * 0.001
            vy = y_speed * 0.001
            self.connection.commWithResp("2HS X=" + str(vx) + " Y=" + str(vy))
    
    def isBusy(self):
        if self.live:
            isBusyReply = self.connection.commWithResp("2H/")
            # print(isBusyReply)
            return isBusyReply
    
    ## joystickOnOff
    #
    # @param on True/False enable/disable the joystick.
    #
    def joystickOnOff(self, on):
        pass
        #if self.live:
        #    if on:
        #        self.connection.commWithResp("!joy 2")
        #    else:
        #        self.connection.commWithResp("!joy 0")

    ## position
    #
    # @return [stage x (um), stage y (um), stage z (um)]
    #
    def position(self):
        if True:  #self.live
            try:
                pos = self.connection.commWithResp("2HW X Y")
                # print(pos)
                [posX, posY] = pos.split(" ")[1:3] # why the answer is only 1:3 here and 2:4 above I don't know
                self.x = float(posX)*self.unit_to_um
                self.y = float(posY)*self.unit_to_um
            except:
                print('error')
                hdebug.logText("  Warning: Bad position from ASI stage.")
            return {"x" : self.x,
                "y" : self.y}
                
            # return [self.x, self.y, 0.0]
        else:
            return {"x" : 0,
                "y" : 0}

    ## setVelocity
    #
    # @param x_vel Maximum velocity to move in x.
    # @param y_vel Maximum velocity to move in y.
    #
    def setVelocity(self, x_vel, y_vel):
        if self.live:
            vx = x_vel
            vy = y_vel
            self.connection.commWithResp("2HS X=" + str(vx) + " Y=" + str(vy))

    ## zero
    #
    # Set the current stage position as the stage zero.
    #
    def zero(self):
        if self.live:
            self.connection.commWithResp("2HZ")

    def shutDown(self):
        """
        Closes the RS-232 port.
        """
        if self.live:
            self.connection.shutDown()

#
# Testing
# 

if __name__ == "__main__":
    stage = MS2000("COM3")
    print(stage.position())

    #print stage.commWithResp("W X Y")
    #stage.goAbsolute(100.0, 100.0)
    #time.sleep(5)
    #print stage.position()
    #stage.goAbsolute(0.0, 0.0)
    #time.sleep(5)
    #print stage.position()

    #print "SN:", stage.serialNumber()
    #stage.zero()
    #print "Position:", stage.position()
    #stage.goAbsolute(100.0, 100.0)
    #print "Position:", stage.position()
    #stage.goRelative(100.0, 100.0)
    #print "Position:", stage.position()
    stage.shutDown()

#    for info in stage.info():
#        print info
#    stage.zero()
#    print stage.position()
#    stage.goAbsolute(100000,100000)
#    print stage.position()
#    stage.goAbsolute(0,0)
#    print stage.position()
#    stage.goRelative(-100000,-100000)
#    print stage.position()
#    stage.goAbsolute(0,0)
#    print stage.position()


#
# The MIT License
#
# Copyright (c) 2014 Zhuang Lab, Harvard University
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
