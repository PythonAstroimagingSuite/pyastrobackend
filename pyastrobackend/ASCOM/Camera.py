#
# ASCOM camera device
#
# Copyright 2020 Michael Fulbright
#
#
#    pyastrobackend is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import time
import logging
import numpy as np
from comtypes.client import CreateObject
from comtypes.safearray import safearray_as_ndarray

from pyastrobackend.BaseBackend import BaseCamera

class Camera(BaseCamera):
    def __init__(self, backend=None):
        self.cam = None
        self.camera_has_progress = None
        # backend is ignored for ASCOM

    def has_chooser(self):
        return True

    def show_chooser(self, last_choice):
        chooser = CreateObject("ASCOM.Utilities.Chooser")
        chooser.DeviceType = "Camera"
        camera = chooser.Choose(last_choice)
        logging.debug(f'choice = {camera}')
        return camera

    def connect(self, name):
        logging.debug(f'connect camera {name}')
        self.cam = CreateObject(name)
        logging.debug(f'{self.cam}')
        try:
            self.cam.Connected = True
        except Exception:
            logging.error('ASCOMBackend:camera:connect() Exception ->', exc_info=True)
            return False

        # see if camera supports progress
        # supports_progess() can throw tracebacks so don't want to
        # have it continually doing this so we cache result
        if self.cam.Connected:
            self.camera_has_progress = self.supports_progress()
            logging.debug('camera:connect camera_has_progress='
                          f'{self.camera_has_progress}')

            #logging.debug(f'ASCOM GAINS = {self.cam.Gains}')
            # FIXME Gain with ASCOM has been somewhat troublesome
            #       Need to revisit with newer drivers as it is
            #       probably better behaved now and this can be cleaned up
            try:
                logging.debug(f'ASCOM GAINMAX = {self.cam.GainMax}')
                logging.debug(f'ASCOM GAINMIN = {self.cam.GainMin}')
            except:
                logging.warning('Unable to read ASCOM GainMin/GainMax', exc_info=True)

        return self.cam.Connected

    def disconnect(self):
        if self.cam:
            if self.cam.Connected:
                self.cam.Connected = False
                self.cam = None
                self.camera_has_progress = None

    def is_connected(self):
        if self.cam:
            return self.cam.Connected
        else:
            return False

    def get_camera_name(self):
        if self.cam:
            return self.cam.Name

    def get_camera_description(self):
        if self.cam:
            return self.cam.Description

    def get_driver_info(self):
        if self.cam:
            return self.cam.DriverInfo

    def get_driver_version(self):
        if self.cam:
            return self.cam.DriverVersion

    def get_settings(self):
        setdict = {}
        setdict['binning'] = self.get_binning()
        setdict['framesize'] = self.get_size()
        setdict['pixelsize'] = self.get_pixelsize()
        setdict['egain'] = self.get_egain()
        setdict['camera_gain'] = self.get_camera_gain()
        setdict['camera_offset'] = self.get_camera_offset()
        setdict['camera_usbbandwidth'] = self.get_camera_usbbandwidth()
        setdict['camera_current_temperature'] = self.get_current_temperature()
        setdict['camera_target_temperature'] = self.get_target_temperature()
        setdict['cooler_state'] = self.get_cooler_state()
        setdict['cooler_power'] = self.get_cooler_power()
        setdict['roi'] = self.get_frame()

        return setdict

# This is ASCOM specific
#    def get_driver_interface_version(self):
#        if self.cam:
#            return self.cam.InterfaceVersion

    def get_state(self):
        if self.cam:
            return self.cam.CameraState

    def start_exposure(self, expos):
        logging.debug(f'Exposing image for {expos} seconds')

        # FIXME currently always requesting a light frame
        if self.cam:
            self.cam.StartExposure(expos, 1)
            return True
        else:
            return False

    def stop_exposure(self):
        if self.cam:
            self.cam.StopExposure()

    def check_exposure(self):
        if not self.cam:
            return False

        return self.cam.ImageReady

    def check_exposure_success(self):
        # return True if exposure successful
        # only valid if check_exposure() returns True
        # FIXME Need to handle errors and set a success flag
        return True

    def supports_progress(self):
#        logging.info(f'ascomcamera: supports_progress {self.camera_has_progress}')
        if self.camera_has_progress is None:
            self.camera_has_progress = self.get_exposure_progress() != -1
#        logging.info(f'ascomcamera: supports_progress return  {self.camera_has_progress}')
        return self.camera_has_progress

# FIXME returns -1 to indicate progress is not available
# FIXME shold use cached value to know if progress is supported
    def get_exposure_progress(self):
        if not self.cam:
            return -1

        if not self.camera_has_progress:
            return -1

        try:
            return self.cam.PercentCompleted
        except Exception:
            logging.warning('camera.get_exposure_progress() failed!')
            logging.error('Exception ->', exc_info=True)
            return -1

    def get_image_data(self):
        """ Get image data from camera

        Returns
        -------
        image_data : numpy array
            Data is in row-major format!
        """
        # FIXME Is this best way to determine data type from camera??
        maxadu = self.cam.MaxADU
        if maxadu == 65535:
            out_dtype = np.dtype(np.uint16)
        else:
            logging.error(f'Unknown MAXADU {maxadu} in getImageData!!')
            return None

        # Transpose to get into row-major
        #image_data = np.array(self.cam.ImageArray, dtype=out_dtype).T

        # FIXME this doesnt work with Python 3.7!
        #       slower workaround below if necessary
        if True:
            with safearray_as_ndarray:
                image_data = self.cam.ImageArray

            image_data = image_data.astype(out_dtype, copy=False)

            # get it into row/col orientation we want
            image_data = image_data.T
        else:
            logging.warning('Using slow ImageArrayVariant workaround in Camera.py')
            w = self.cam.Numx
            h = self.cam.Numy
            logging.debug(f'subframe is {w} x {h}')
            ts = time.time()
            image_data = np.array(self.cam.ImageArray, dtype=out_dtype)
            image_data.reshape(h, w)
            image_data = image_data.T
            logging.debug(f'Frame readout took {time.time() - ts} seconds')
#        logging.info(f'in backend image shape is {image_data.shape}')

        return image_data

    def supports_saveimage(self):
        return False

    def save_image_data(self, path, overwrite=False):
        logging.warning('camera.save_image_data() NOT IMPLEMENTED FOR ASCOM CAMERA!')
        return False

    def get_pixelsize(self):
        return self.cam.PixelSizeX, self.cam.PixelSizeY

    def get_egain(self):
        return self.cam.ElectronsPerADU

    def get_camera_gain(self):
        """ Looks for camera specific gain - only works for ASI afaik"""
        ccd_gain = None
        if self.cam:
            try:
                ccd_gain = self.cam.Gain
                logging.debug(f'camera gain = {ccd_gain}')
            except:
                # FIXME Need to tighten up this exception
                logging.error('Unable to read camera gain!', exc_info=True)

        return ccd_gain

    def set_camera_gain(self, ccd_gain):
        """ Looks for camera specific gain - only works for ASI afaik"""

        logging.warning('!!!!!!!! ASCOM set_camera_gain DISABLED for now until !!!!!!!!!')
        logging.warning('!!!!!!!! discrepancy between dialog gain and API gain !!!!!!!!!')
        logging.warning('!!!!!!!! better understood.                           !!!!!!!!!')
        return

        # OLD CODE to implement gain changes
        # if self.cam:
        #     try:
        #         self.cam.Gain = int(ccd_gain)
        #         logging.debug(f'set camera gain = {ccd_gain}')
        #         return True
        #     except:
        #         # FIXME Need to tighten up this exception
        #         logging.error(f'Unable to set camera gain!', exc_info=True)

        return False

    def get_camera_offset(self):
        return None

    def get_camera_usbbandwidth(self):
        return None

    def get_current_temperature(self):
        return self.cam.CCDTemperature

    def get_target_temperature(self):
        return self.cam.SetCCDTemperature

    def set_target_temperature(self, temp_c):
        try:
            self.cam.SetCCDTemperature = temp_c
        except:
            # FIXME Need to tighten up this exception
            logging.warning('camera.set_target_temperature() failed!')

    def set_cooler_state(self, onoff):
        try:
            self.cam.CoolerOn = onoff
        except:
            # FIXME Need to tighten up this exception
            logging.warning('camera.set_cooler_state() failed!')

    def get_cooler_state(self):
        return self.cam.CoolerOn

    def get_binning(self):
        return (self.cam.BinX, self.cam.BinY)

    def get_cooler_power(self):
        try:
            return self.cam.CoolerPower
        except Exception:
            # FIXME Need to tighten up this exception
            logging.warning('camera.get_cooler_power() failed!')
            logging.error('Exception ->', exc_info=True)
            return 0

    def set_binning(self, binx, biny):
        self.cam.BinX = binx
        self.cam.BinY = biny
        return True

    def get_max_binning(self):
        if self.cam is None:
            return None
        return self.cam.MaxBinX

    def get_size(self):
        return (self.cam.CameraXSize, self.cam.CameraYSize)

    def get_frame(self):
        return(self.cam.StartX, self.cam.StartY, self.cam.NumX, self.cam.NumY)

    def set_frame(self, minx, miny, width, height):
        self.cam.StartX = minx
        self.cam.StartY = miny
        self.cam.NumX = width
        self.cam.NumY = height

        return True

    def get_min_max_exposure(self):
        if self.cam:
            try:
                exp_min = self.cam.ExposureMin
                exp_max = self.cam.ExposureMax
            except:
                # FIXME Need to tighten up this exception
                logging.error('Unable to get min/max exposure allowed', exc_info=True)
                return None
            return (exp_min, exp_max)
        else:
            return None
