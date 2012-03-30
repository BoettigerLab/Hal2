#!/usr/bin/python
#
# Focus lock control specialized for STORM4.
#
# Hazen 03/12
#

# camera and stage.
import madCityLabs.mclController as mclController
import thorlabs.uc480Camera as uc480Cam

# focus lock control thread.
import focuslock.stageOffsetControl as stageOffsetControl

# ir laser control
import thorlabs.LDC210 as LDC210

# focus lock dialog.
import focuslock.focusLockZ as focusLockZ

#
# Focus Lock Dialog Box specialized for STORM4 with 
# USB offset detector and MCL objective Z positioner.
#
class AFocusLockZ(focusLockZ.FocusLockZCam):
    def __init__(self, parameters, tcp_control, parent = None):
        cam = uc480Cam.cameraQPD()
        stage = mclController.MCLStage("c:/Program Files/Mad City Labs/NanoDrive/")
        lock_fn = lambda (x): 0.005 * x
        control_thread = stageOffsetControl.stageCamThread(cam,
                                                           stage,
                                                           lock_fn,
                                                           50.0,
                                                           parameters.qpd_zcenter)
        ir_laser = LDC210.LDC210("PCI-6733", 7)
        focusLockZ.FocusLockZCam.__init__(self,
                                          parameters,
                                          tcp_control,
                                          control_thread,
                                          ir_laser,
                                          parent)

#
# The MIT License
#
# Copyright (c) 2012 Zhuang Lab, Harvard University
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