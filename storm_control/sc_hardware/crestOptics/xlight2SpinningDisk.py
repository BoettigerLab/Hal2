#!/usr/bin/env python
"""
A serial interface to the W1 Spinning Disk from Yokogawa/Andor.

Jeffrey Moffitt 5/16
Hazen Babcock 5/17
"""

import storm_control.sc_hardware.serial.RS232 as RS232


class XlightSpinningDisk(RS232.RS232):

    def __init__(self, **kwds):
        super().__init__(**kwds)

    def commandResponse(self, command, timeout = 0.1):

        # Clear buffer of old responses.
        self.tty.timeout = 0
        while (len(self.readline()) > 0):
            pass
        
        # Set timeout.
        self.tty.timeout = timeout

        # Send the command and wait timeout time for a response.
        self.writeline(command)
        response = self.readline()

        # Check that we got a message within the timeout.
        if (len(response) > 0):
			return response
                

        else:
			print("no response from disk, possible error here")
            return None


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
