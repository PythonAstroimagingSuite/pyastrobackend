import time
import logging
import numpy as np

from pyastrobackend.BaseBackend import BaseCamera
from pyastrobackend.Alpaca.AlpacaDevice import AlpacaDevice

class Camera(AlpacaDevice, BaseCamera):

    def __init__(self, backend):
        # FIXME call initializer for AlpacaDevice mixin) - is this sensible way
        self._initialize_device_attr()
        self.camera_has_progress = None
        self.backend = backend
        logging.info(f'alapaca camera setting backend to {backend}')

    def get_camera_name(self):
        return self.get_prop('name')

    def get_camera_description(self):
        return self.get_prop('description')

    def get_driver_info(self):
        return self.get_prop('driverinfo')

    def get_driver_version(self):
        return self.get_prop('driverversion')

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

    def get_state(self):
        return self.get_prop('camerastate')

    def start_exposure(self, expos):
        logging.debug(f'Exposing image for {expos} seconds')

        params = {'Duration' : expos, 'Light' : True}
        return self.set_prop('startexposure', params)

    def stop_exposure(self):
        return self.set_prop('stopexposure', {})

    def check_exposure(self):
        return self.get_prop('imageready')

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
        if not self.camera_has_progress:
            return -1

        return self.get_prop('percentcompleted')

    def get_image_data(self):
        """ Get image data from camera

        Returns
        -------
        image_data : numpy array
            Data is in row-major format!
        """
        # FIXME Is this best way to determine data type from camera??
        maxadu =  self.get_prop('maxadu')
        if maxadu == 65535:
            out_dtype = np.dtype(np.uint16)
        else:
            logging.error(f'Unknown MAXADU {maxadu} in getImageData!!')
            return None

        # Transpose to get into row-major
        #image_data = np.array(self.cam.ImageArray, dtype=out_dtype).T

        resp = self.get_prop('imagearray', returndict=True)
#        f=open('imagejson.json', 'w')
#        f.write(repr(resp))
#        f.close()

        # check rank and type
        logging.debug(f'ImageArray Rank = {resp.get("Rank")} Type = {resp.get("Type")}')
        if resp.get('Rank') != 2 or resp.get('Type') != 2:
            logging.error('ImageArray returned a Rank or Type != 2!')
            return None

        # get data and convert to desired type
        image_data = np.array(resp.get('Value')).astype(out_dtype)

        # reshape to 2D
        roi = self.get_frame()
        if roi is None:
            logging.error('roi is None cannot reshape image!')
            return None

        logging.debug(f'reshaping to numy = {roi[3]} numx = {roi[2]}')

        # remember array has Y as first axis!!
        np.reshape(image_data, (roi[3], roi[2]))

        # then transpose so X is first
        image_data = image_data.T

        return image_data

    def save_image_data(self, path, overwrite=False):
        logging.warning('camera.save_image_data() NOT IMPLEMENTED FOR Alpaca CAMERA!')
        return False

    def get_pixelsize(self):
        pix_x = self.get_prop('pixelsizex')
        pix_y = self.get_prop('pixelsizey')
        return pix_x, pix_y

    def get_egain(self):
        return self.get_prop('electronsperadu')

    def get_camera_gain(self):
        """ Looks for camera specific gain - only works for ASI afaik"""
        return self.get_prop('gain')

    def set_camera_gain(self, ccd_gain):
        """ Looks for camera specific gain - only works for ASI afaik"""

        logging.warning('!!!!!!!! ASCOM set_camera_gain DISABLED for now until !!!!!!!!!')
        logging.warning('!!!!!!!! discrepancy between dialog gain and API gain !!!!!!!!!')
        logging.warning('!!!!!!!! better understood.                           !!!!!!!!!')
        return False

        # proper code but disabled for now
        #return self.set_prop('gain', {'gain' : ccd_gain})

    def get_camera_offset(self):
        return None

    def get_camera_usbbandwidth(self):
        return None

    def get_current_temperature(self):
        return self.get_prop('ccdtemperature')

    def get_target_temperature(self):
        return self.get_prop('setccdtemperature')

    def set_target_temperature(self, temp_c):
        params = {'SetCCDTemperature' : temp_c}
        return self.set_prop('setccdtemperature', params)

    def set_cooler_state(self, onoff):
        params = {'CoolerOn' : onoff}
        return self.set_prop('cooleron', params)

    def get_cooler_state(self):
        return self.get_prop('cooleron')

    def get_binning(self):
        bin_x = self.get_prop('binx')
        bin_y = self.get_prop('biny')
        return bin_x, bin_y

    def get_cooler_power(self):
        power = self.get_prop('coolerpower')
        if power is None:
            power = 0
        return power

    def set_binning(self, binx, biny):
        param_x = {'binx' : binx}
        param_y = {'biny' : biny}
        rc = self.set_prop('binx', param_x)
        if not rc:
            return rc
        rc = self.set_prop('biny', param_y)
        return rc

    def get_max_binning(self):
        # FIXME Assumes max binning is same in X and Y!
        return self.get_prop('maxbinx')

    def get_size(self):
        cam_x = self.get_prop('cameraxsize')
        cam_y = self.get_prop('cameraysize')
        return cam_x, cam_y

    def get_frame(self):
        sx = self.get_prop('startx')
        sy = self.get_prop('starty')
        numx = self.get_prop('numx')
        numy = self.get_prop('numy')
        return(sx, sy, numx, numy)

    def set_frame(self, minx, miny, width, height):
        rc = self.set_prop('startx', {'StartX' : minx})
        if not rc:
            return rc
        rc = self.set_prop('starty', {'StartY' : miny})
        if not rc:
            return rc
        rc = self.set_prop('numx', {'NumX' : width})
        if not rc:
            return rc
        rc = self.set_prop('numy', {'NumY' : height})
        return rc

    def get_min_max_exposure(self):
        exp_min = self.get_prop('exposuremin')
        exp_max = self.get_prop('exposuremax')
        return exp_min, exp_max
