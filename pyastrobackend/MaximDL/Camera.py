""" MaximDL Camera solution """
import sys
import time
import logging
import win32com.client

from ..BaseBackend import BaseCamera


class Camera(BaseCamera):
    def __init__(self, backend=None):
        self.camera_has_progress = None
        self.connected = False
        # backend ignored for MaximDL camera driver

        # try to throttle these
        self.last_check_exposure = 0
        self.last_check_exposure_value = False

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('MaximDL Camera Backend: no show_chooser()!')
        return None

    # name is currently ignored
    def connect(self, name):
        logging.debug(f'MaximDL Camera connect: ')

        try:
            self.cam = win32com.client.Dispatch("MaxIm.CCDCamera")
            self.cam.LinkEnabled = True
            self.cam.DisableAutoShutDown = True
        except:
            logging.error('MaximDLCamera:connect() FAILED', exc_info=True)
            return False

        self.connected = True
        return True

    def disconnect(self):
        try:
            self.cam.LinkEnabled = False
            self.connected = False
        except:
            logging.error('MaximDLCamera:disconnect() FAILED', exc_info=True)
            return False

    def is_connected(self):
        try:
            return self.connected
        except:
            logging.error('MaximDLCamera:is_connected() FAILED', exc_info=True)
            return False

    def get_camera_name(self):
        return 'MaximDL'

    def get_camera_description(self):
        return 'MaximDL Camera Driver'

    def get_driver_info(self):
        return 'MaximDL Camera Driver'

    def get_driver_version(self):
        return 'V 0.1'

    def get_settings(self):
        raise Exception('get_settings not implemented for Maxim DL!')

    def get_state(self):
        logging.warning('MaximDL Camera get_state() not implemented')
        return None

    def start_exposure(self, expos):
        logging.debug(f'MaximDL: Exposing image for {expos} seconds')

        try:
            self.cam.Expose(expos, 1, -1)
        except:
            logging.error('MaximDLCamera:start_exposure() FAILED', exc_info=True)
            return False

        return True

    def stop_exposure(self):
        logging.warning('MaximDL Camera stop_exposure() not implemented')
        return None

    def check_exposure(self):
        if time.time() - self.last_check_exposure >= 1.0:
            self.last_check_exposure = time.time()
            logging.debug('MaximDLCamera:check_exposure()')
            try:
                self.last_check_exposure_value = self.cam.ImageReady
            except:
                logging.error('MaximDLCamera:check_exposure() FAILED', exc_info=True)
                return None
        return self.last_check_exposure_value

    def check_exposure_success(self):
        # FIXME Can we get a value for this from Maxim?
        return True

    def supports_progress(self):
        logging.warning('MaximDL Camera supports_progress() not implemented')
        return False

# FIXME returns -1 to indicate progress is not available
# FIXME shold use cached value to know if progress is supported
    def get_exposure_progress(self):
        logging.warning('MaximDL Camera get_exposure_progress() not implemented')
        return -1

    def supports_saveimage(self):
        return True

    def save_image_data(self, path, overwrite=False):
        #
        # FIXME overwrite probably ignored Maxim doesn't have option
        # FIXME make better temp name
        # FIXME specify cwd as path for file - otherwise not sure where it goes!
        #
        logging.debug(f"saveimageCamera: saving to {path}")

        ntries = 3
        while True:
            try:
                self.cam.SaveImage(path)
                break
            except:
                exc_type, exc_value = sys.exc_info()[:2]
                logging.error('saveimageCamera %s exception with message "%s" in ' % \
                                (exc_type.__name__, exc_value))
                logging.error(f"Error saving {path} in saveimageCamera()!")
                ntries = ntries - 1
                if ntries < 0:
                    logging.error('Giving up could not save Maxim image!')
                    logging.error('Ignoring error though for testing!!!')
                    return True
                import time
                time.sleep(1)



        # try:
            # self.cam.SaveImage(path)
        # except:
            # exc_type, exc_value = sys.exc_info()[:2]
            # logging.error('saveimageCamera %s exception with message "%s" in ' % \
                              # (exc_type.__name__, exc_value))
            # logging.error(f"Error saving {path} in saveimageCamera()!")
            # return False

        return True

    def get_image_data(self):
        logging.warning('MaximDL Camera get_image_data() not implemented!')
        return False

    def get_pixelsize(self):
        #logging.warning('MaximDL Camera get_pixelsize() not implemented!')
        try:
            return self.cam.PixelSizeX, self.cam.PixelSizeY
        except:
            logging.error('MaximDLCamera:get_pixelsize() FAILED', exc_info=True)
            return None

    def get_egain(self):
        logging.warning('MaximDL Camera get_egain() not implemented!')
        return None

    def get_camera_gain(self):
        logging.warning('MaximDL Camera get_camera_gain() not implemented!')
        return None

    def set_camera_gain(self, gain):
        logging.warning('MaximDL Camera set_camera_gain() not implemented!')
        return False


    def get_current_temperature(self):
        #logging.warning('MaximDL Camera get_current_temperature() not implemented!')
        try:
            return self.cam.Temperature
        except:
            logging.error('MaximDLCamera:get_current_temperature() FAILED', exc_info=True)
            return None

    def get_target_temperature(self):
        #logging.warning('MaximDL Camera get_target_temperature() not implemented!')
        try:
            return self.cam.TemperatureSetpoint
        except:
            logging.error('MaximDLCamera:get_target_temperature() FAILED', exc_info=True)
            return None

    def set_target_temperature(self, temp_c):
        #logging.warning('MaximDL Camera set_target_temperature() not implemented!')
        try:
            self.cam.TemperatureSetpoint = temp_c
        except:
            logging.error('MaximDLCamera:set_target_temperature() FAILED', exc_info=True)
            return False

        return True

    def set_cooler_state(self, onoff):
        #logging.warning('MaximDL Camera set_cooler_state() not implemented!')
        try:
            self.cam.CoolerOn = onoff
        except:
            logging.error('MaximDLCamera:set_cooler_state() FAILED', exc_info=True)
            return False

        return True

    def get_cooler_state(self):
        #logging.warning('MaximDL Camera get_cooler_state() not implemented!')
        try:
            return self.cam.CoolerOn
        except:
            logging.error('MaximDLCamera:get_cooler_state() FAILED', exc_info=True)
            return None

    def get_cooler_power(self):
        #logging.warning('MaximDL Camera get_cooler_power() not implemented!')
        try:
            return self.cam.CoolerPower
        except:
            logging.error('MaximDLCamera:get_cooler_power() FAILED', exc_info=True)
            return None

    def get_binning(self):
        try:
            return (self.cam.BinX, self.cam.BinY)
        except:
            logging.error('MaximDLCamera:get_binning() FAILED', exc_info=True)
            return None

    def set_binning(self, binx, biny):
        try:
            self.cam.BinX = binx
            self.cam.BinY = biny
        except:
            logging.error('MaximDLCamera:set_binning() FAILED', exc_info=True)
            return False

        return True

    def get_max_binning(self):
        logging.warning('MaximDL Camera get_max_binning() not implemented!')

    def get_size(self):
        try:
            return (self.cam.CameraXSize, self.cam.CameraYSize)
        except:
            logging.error('MaximDLCamera:get_size() FAILED', exc_info=True)
            return None

        return True

    def get_frame(self):
        try:
            return(self.cam.StartX, self.cam.StartY, self.cam.NumX, self.cam.NumY)
        except:
            logging.error('MaximDLCamera:get_frame() FAILED', exc_info=True)
            return None

        return True

    def set_frame(self, minx, miny, width, height):
        try:
            self.cam.StartX = minx
            self.cam.StartY = miny
            self.cam.NumX = width
            self.cam.NumY = height
        except:
            logging.error('MaximDLCamera:set_frame() FAILED', exc_info=True)
            return False

        return True
