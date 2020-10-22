#!/usr/bin/env python
"""
Point Grey camera used in the context of a focus lock.

Hazen 09/19
"""
import numpy
import time
from PyQt5 import QtCore

import storm_control.sc_hardware.utility.af_lock_c as afLC
import storm_control.sc_hardware.utility.sa_lock_peak_finder as slpf

import storm_control.sc_hardware.pointGrey.spinnaker as spinnaker

import tifffile


class LockCamera(QtCore.QThread):
    """
    This class is used to control a Point Grey (Spinnaker) camera in the 
    context of a focus lock.
    """
    cameraUpdate = QtCore.pyqtSignal(dict)

    def __init__(self, camera_id = None, parameters = None, **kwds):
        super().__init__(**kwds)

        self.cur_offsetx = None
        self.cur_offsety = None        
        self.old_offsetx = None
        self.old_offsety = None
        self.max_offsetx = None
        self.max_offsety = None
        self.n_analyzed = 0
        self.n_dropped = 0
        self.start_time = None

        self.params_mutex = QtCore.QMutex()
        self.running = False
        
        self.zero_dist = parameters.get("zero_dist")

        # Initialize library.
        spinnaker.pySpinInitialize(verbose = False)

        # Get the camera & set some defaults.
        self.camera = spinnaker.getCamera(camera_id)

        # In order to turn off pixel defect correction the camera has
        # to be in video mode 0.
        self.camera.setProperty("VideoMode", "Mode0")
        self.camera.setProperty("pgrDefectPixelCorrectionEnable", False)
        
        # Set pixel format.
        self.camera.setProperty("PixelFormat", "Mono16")

        self.camera.setProperty("VideoMode", parameters.get("video_mode"))
                
        # We don't want any of these 'features'.
        self.camera.setProperty("AcquisitionFrameRateAuto", "Off")
        self.camera.setProperty("ExposureAuto", "Off")
        self.camera.setProperty("GainAuto", "Off")        

        if self.camera.hasProperty("pgrExposureCompensationAuto"):
            self.camera.setProperty("pgrExposureCompensationAuto", "Off")

        if self.camera.hasProperty("BlackLevelClampingEnable"):
            self.camera.setProperty("BlackLevelClampingEnable", False)

        if self.camera.hasProperty("SharpnessEnabled"):
            self.camera.setProperty("SharpnessEnabled", False)

        if self.camera.hasProperty("GammaEnabled"):
            self.camera.setProperty("GammaEnabled", False)

        #
        # No idea what this means in the context of a black and white
        # camera. We try and turn it off but that seems to be much
        # harder to do than one would hope.
        #
        self.camera.setProperty("OnBoardColorProcessEnabled", False)

        # Verify that we have turned off some of these 'features'.
        for feature in ["pgrDefectPixelCorrectionEnable",
                        "BlackLevelClampingEnable",
                        "SharpnessEnabled",
                        "GammaEnabled"]:
            if self.camera.hasProperty(feature):
                assert not self.camera.getProperty(feature).getValue()

        # Configure camera to not use triggering.
        #
        self.camera.setProperty("TriggerMode", "Off")

        # Configure acquisition parameters.
        #
        # Note: The order is important here.
        #
        for pname in ["BlackLevel", "Gain", "Height", "Width", "OffsetX", "OffsetY", "AcquisitionFrameRate"]:
            self.camera.setProperty(pname, parameters.get(pname))

        # Use maximum exposure time allowed by desired frame rate.
        #
        self.camera.setProperty("ExposureTime", self.camera.getProperty("ExposureTime").getMaximum())

        # Get current offsets.
        #
        self.cur_offsetx = self.camera.getProperty("OffsetX").getValue()
        self.cur_offsety = self.camera.getProperty("OffsetY").getValue()
        self.old_offsetx = self.cur_offsetx
        self.old_offsety = self.cur_offsety
        
        # Set maximum offsets.
        #
        self.max_offsetx = self.camera.getProperty("OffsetX").getMaximum()
        self.max_offsety = self.camera.getProperty("OffsetY").getMaximum()
        
    def adjustAOI(self, dx, dy):
        tmp_x = self.cur_offsetx + dx
        tmp_y = self.cur_offsety + dy

        tmp_x = max(0, tmp_x)
        tmp_x = min(self.max_offsetx, tmp_x)
                
        tmp_y = max(0, tmp_y)
        tmp_y = min(self.max_offsety, tmp_y)

        #
        # The thread loop will check for cur != old and update the camera values
        # as necessary.
        #
        self.params_mutex.lock()
        self.cur_offsetx = tmp_x
        self.cur_offsety = tmp_y
        self.params_mutex.unlock()    

    def adjustZeroDist(self, inc):
        pass

    def run(self):
        self.camera.startAcquisition()
        self.running = True
        while(self.running):
            [frames, frame_size] = self.camera.getFrames()
            self.analyze(frames, frame_size)

            # Check for AOI change.
            self.params_mutex.lock()
            if (self.old_offsetx != self.cur_offsetx) or (self.old_offsety != self.cur_offsety):
                self.camera.stopAcquisition()
                self.camera.setProperty("OffsetX", self.cur_offsetx)
                self.camera.setProperty("OffsetY", self.cur_offsety)
                self.camera.startAcquisition()
                self.old_offsetx = self.cur_offsetx
                self.old_offsety = self.cur_offsety                
            self.params_mutex.unlock()
            self.msleep(5)
            
        self.camera.stopAcquisition()

    def startCamera(self):
        self.start(QtCore.QThread.NormalPriority)
        self.start_time = time.time()
        
    def stopCamera(self, verbose = True):
        if verbose:
            fps = self.n_analyzed/(time.time() - self.start_time)
            print("    > AF: Analyzed {0:d}, Dropped {1:d}, {2:.3f} FPS".format(self.n_analyzed, self.n_dropped, fps))
            print("    > AF: OffsetX {0:d}, OffsetY {1:d}, ZeroD {2:.2f}".format(self.cur_offsetx, self.cur_offsety, self.zero_dist))

        self.running = False
        self.wait()
        self.camera.shutdown()


class AFLockCamera(LockCamera):
    """
    This class works with the auto-focus hardware configuration.

    In this configuration there are two spots that move horizontally
    as the focus changes. The spots are shifted vertically so that
    they don't overlap with each other.
    """
    def __init__(self, parameters = None, **kwds):
        kwds["parameters"] = parameters
        super().__init__(**kwds)

        self.cnt = 0
        self.max_backlog = 20
        self.min_good = parameters.get("min_good")
        self.reps = parameters.get("reps")
        self.sum_scale = parameters.get("sum_scale")
        self.sum_zero = parameters.get("sum_zero")

        self.good = numpy.zeros(self.reps, dtype = numpy.bool)
        self.mag = numpy.zeros(self.reps)
        self.x_off = numpy.zeros(self.reps)
        self.y_off = numpy.zeros(self.reps)

        # Create slices for selecting the appropriate regions from the camera.
        t1 = list(map(int, parameters.get("roi1").split(",")))
        self.roi1 = (slice(t1[0], t1[1]), slice(t1[2], t1[3]))

        t2 = list(map(int, parameters.get("roi2").split(",")))
        self.roi2 = (slice(t2[0], t2[1]), slice(t2[2], t2[3]))

        self.afc = afLC.AFLockC(offset = parameters.get("background"),
                                downsample = parameters.get("downsample"))

        assert (self.reps >= self.min_good), "'reps' must be >= 'min_good'."

    def adjustZeroDist(self, inc):
        self.params_mutex.lock()
        self.zero_dist += 0.001*inc
        self.params_mutex.unlock()

    def analyze(self, frames, frame_size):

        # Only keep the last max_backlog frames if we are falling behind.
        lf = len(frames)
        if (lf>self.max_backlog):
            self.n_dropped += lf - self.max_backlog
            frames = frames[-self.max_backlog:]
            
        for elt in frames:
            self.n_analyzed += 1

            frame = elt.getData().reshape(frame_size)
            image1 = frame[self.roi1]
            image2 = frame[self.roi2]
            [x_off, y_off, success, mag] = self.afc.findOffsetU16NM(image1, image2, verbose = False)

            #self.bg_est[self.cnt] = frame[0,0]
            self.good[self.cnt] = success
            self.mag[self.cnt] = mag
            self.x_off[self.cnt] = x_off
            self.y_off[self.cnt] = y_off

            # Check if we have all the samples we need.
            self.cnt += 1
            if (self.cnt == self.reps):

                # Convert current frame to 8 bit image.
                image = numpy.right_shift(frame, 3).astype(numpy.uint8)
                
                qpd_dict = {"is_good" : True,
                            "image" : image,
                            "offset" : 0.0,
                            "sum" : 0.0,
                            "x_off" : 0.0,
                            "y_off" : 0.0}
                            
                if (numpy.count_nonzero(self.good) < self.min_good):
                    qpd_dict["is_good"] = False
                    self.cameraUpdate.emit(qpd_dict)
                else:
                    mag = numpy.mean(self.mag[self.good])
                    y_off = numpy.mean(self.y_off[self.good]) - self.zero_dist

                    qpd_dict["offset"] = y_off
                    qpd_dict["sum"] = self.sum_scale*mag - self.sum_zero
                    qpd_dict["x_off"] = numpy.mean(self.x_off[self.good])
                    qpd_dict["y_off"] = y_off
                    
                    self.cameraUpdate.emit(qpd_dict)

                self.cnt = 0

        
    def stopCamera(self):
        super().stopCamera()
        self.afc.cleanup()


class SSLockCamera(LockCamera):
    """
    This class works with the standard IR laser focus lock configuration.

    In this configuration there is a single spot that movies horizontally
    as the focus changes.
    """
    def __init__(self, parameters = None, **kwds):
        kwds["parameters"] = parameters
        super().__init__(**kwds)

        self.cnt = 0
        self.max_backlog = 20
        self.min_good = parameters.get("min_good")
        self.offset = parameters.get("offset")
        self.reps = parameters.get("reps")
        self.sum_scale = parameters.get("sum_scale")
        self.sum_zero = parameters.get("sum_zero")

        self.good = numpy.zeros(self.reps, dtype = numpy.bool)
        self.mag = numpy.zeros(self.reps)
        self.x_off = numpy.zeros(self.reps)
        self.y_off = numpy.zeros(self.reps)

        self.lpf = slpf.LockPeakFinder(offset = 0,
                                       sigma = parameters.get("sigma"),
                                       threshold = parameters.get("threshold"))

        assert (self.reps >= self.min_good), "'reps' must be >= 'min_good'."

    def adjustZeroDist(self, inc):
        self.params_mutex.lock()
        self.zero_dist += 0.1*inc
        self.params_mutex.unlock()
        
    def analyze(self, frames, frame_size):

        # Only keep the last max_backlog frames if we are falling behind.
        lf = len(frames)
        if (lf>self.max_backlog):
            self.n_dropped += lf - self.max_backlog
            frames = frames[-self.max_backlog:]
            
        for elt in frames:
            self.n_analyzed += 1

            frame = elt.getData().reshape(frame_size)

            # self.offset is slightly below what the camera reads with no
            # signal. We'll be doing MLE fitting so we can't tolerate
            # negative values in 'frame'.
            frame = frame - self.offset

            # Magnitude calculation.
            mag = numpy.max(frame) - numpy.mean(frame)
            
            # Fit peak X/Y location.
            [x_off, y_off, success] = self.lpf.findFitPeak(frame)

            self.good[self.cnt] = success
            self.mag[self.cnt] = mag
            self.x_off[self.cnt] = x_off
            self.y_off[self.cnt] = y_off

            # Check if we have all the samples we need.
            self.cnt += 1
            if (self.cnt == self.reps):

                # Convert current frame to 8 bit image.
                image = numpy.right_shift(frame.astype(numpy.uint16), 3).astype(numpy.uint8)

                mag = numpy.mean(self.mag)
                qpd_dict = {"is_good" : True,
                            "image" : image,
                            "offset" : 0.0,
                            "sum" : self.sum_scale*mag - self.sum_zero,
                            "x_off" : 0.0,
                            "y_off" : 0.0}
                            
                if (numpy.count_nonzero(self.good) < self.min_good):
                    qpd_dict["is_good"] = False
                    self.cameraUpdate.emit(qpd_dict)
                else:
                    y_off = numpy.mean(self.y_off[self.good]) - self.zero_dist

                    qpd_dict["offset"] = y_off
                    qpd_dict["x_off"] = numpy.mean(self.x_off[self.good])
                    qpd_dict["y_off"] = y_off
                    
                    self.cameraUpdate.emit(qpd_dict)

                self.cnt = 0

        
    def stopCamera(self):
        super().stopCamera()
        self.lpf.cleanup()
        

#
# The MIT License
#
# Copyright (c) 2020 Babcock Lab, Harvard University
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

