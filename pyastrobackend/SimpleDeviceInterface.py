import os
import time
import logging

import astropy.io.fits as pyfits

from pyastrobackend.BackendConfig import get_backend_for_os, get_backend


class SimpleDeviceInterface:
    def __init__(self):
        pass
        #def_backend = get_backend_for_os()
        #self.backend = get_backend(def_backend)

    def connect_backend(self, backend_name=None):
        """
        Connect to the driver backend. If none is specified then a
        default value for the given platform will be guessed.

        :param backend_name: Name of backend, defaults to None
        :type backend_name: str, optional
        :return: True on success.
        :rtype: bool

        """
        if backend_name is None:
            backend_name = get_backend_for_os()

        logging.info(f'SDI:connect_backend: backend={backend_name}')

        self.backend = get_backend(backend_name)

        rc = self.backend.connect()
        if not rc:
            logging.error('Failed to connect to backend!')

        # set all backends
        self.camera_backend = self.backend
        self.focuser_backend = self.backend
        self.filterwheel_backend = self.backend

        return rc

    def connect_focuser(self, driver, backend_name=None):
        """
        Connect to the focuser driver.  A backend can be specified so that
        the focuser uses a different backend than other device classes, for
        example.

        :param driver: Name of focuser driver.
        :type driver: str
        :param backend_name: Name of backend to use for focuser, defaults to None
        :type backend_name: str, optional
        :return: Focuser object or None if connection fails.
        :rtype: Focuser object

        """
        rc = None

        # if backend_name is None we assume they connected with connect_backend
        # and all devices share the same backend
        if backend_name is not None:
            logging.info(f'SDI:connect_focuser: focuser_backend={backend_name}')

            self.focuser_backend = get_backend(backend_name)

            rc = self.focuser_backend.connect()
            if not rc:
                logging.error('Failed to connect to backend!')
                return None
        else:
            if self.focuser_backend is not None:
                backend_name = self.focuser_backend.name()
            else:
                backend_name = None

        if backend_name is None:
            logging.error('No backend specified! Cannot connect focuser!')
            return None

        focuser = self.focuser_backend.newFocuser()
        rc = focuser.connect(driver)

        if rc:
            return focuser
        else:
            return None

    def connect_filterwheel(self, driver, backend_name=None):
        """
        Connect to the filterwheel driver.  A backend can be specified so that
        the filterwheel uses a different backend than other device classes, for
        example.

        :param driver: Name of filterwheel driver.
        :type driver: str
        :param backend_name: Name of backend to use for filterwheel, defaults to None
        :type backend_name: str, optional
        :return: FilterWheel object or None if connection fails.
        :rtype: FilterWheel object

        """
        rc = None

        # if backend_name is None we assume they connected with connect_backend
        # and all devices share the same backend
        if backend_name is not None:
            logging.info('SDI:connect_filterwheel: '
                         f'filterwheel_backend={backend_name}')

            self.filterwheel_backend = get_backend(backend_name)

            rc = self.filterwheel_backend.connect()
            if not rc:
                logging.error('Failed to connect to backend!')
                return None
        else:
            if self.filterwheel_backend is not None:
                backend_name = self.filterwheel_backend.name()
            else:
                backend_name = None

        if backend_name is None:
            logging.error('No backend specified! Cannot connect filter wheel!')
            return None

        wheel = self.filterwheel_backend.newFilterWheel()
        rc = wheel.connect(driver)

        if rc:
            return wheel
        else:
            return None

    def wait_on_focuser_move(self, focuser, timeout=60):
        """
        Wait for any focuser move to complete up to a timeout value.

        :param focuser: Focuser object
        :type focuser: Focuser object
        :param timeout: Timeout for wait for motion to stop, defaults to 60
        :type timeout: int, optional
        :return: True on success.
        :rtype: bool

        """
        ts = time.time()
        lastpos = focuser.get_absolute_position()
        ntimes = 0
        while (time.time() - ts) < timeout:
            logging.debug(f'waiting on focuser move - curpos = '
                          f'{focuser.get_absolute_position()}')

            curpos = focuser.get_absolute_position()
            if abs(curpos - lastpos) < 1:
                ntimes = 3
                break

            lastpos = curpos

#   FIXME This doesn't seem to work in pyastro37 env under windows????
#            if not focuser.is_moving():
#                break

            time.sleep(0.5)

        #time.sleep(0.5) # just be sure its done

        return ntimes > 2

    # FIXME INDI stuff is broken!!!!
    def connect_camera(self, camera_driver, backend_name=None):
        """
        Connect to the camera driver.  A backend can be specified so that
        the camera uses a different backend than other device classes, for
        example.

        :param driver: Name of camera driver.
        :type driver: str
        :param backend_name: Name of backend to use for camera, defaults to None
        :type backend_name: str, optional
        :return: Camera object or None if connection fails.
        :rtype: Camera object

        """
        # if backend_name is None we assume they connected with connect_backend
        # and all devices share the same backend
        if backend_name is not None:

            logging.info(f'SDI:connect_camera: camera_backend={backend_name}')

            self.camera_backend = get_backend(backend_name)

            rc = self.camera_backend.connect()
            if not rc:
                logging.error('Failed to connect to backend!')
                return None
        else:
            if self.camera_backend is not None:
                backend_name = self.camera_backend.name()
            else:
                backend_name = None

        logging.info(f'connect_camera: backend_name = {backend_name}')

        if backend_name is None:
            logging.error('No backend specified! Cannot connect camera!')
            return None

        logging.debug(f'connect_camera: driver =  {camera_driver}')

        cam = self.camera_backend.newCamera()

        rc = cam.connect(camera_driver)

    #    if driver == 'INDICamera':
    #        rc = cam.connect(camera_driver)
    #
    ##        if ':' in camera_driver:
    ##            indi_cam_driver = camera_driver.split(':')[1]
    ##            rc = cam.connect(indi_cam_driver)
    ##        else:
    ##            logging.error('connect_camera(): Must configure INDI camera driver first!')
    ##            return None
    #    else:
    #        rc = cam.connect(driver)

        if not rc:
            logging.error('connect_camera(): Unable to connect to camera!')
            return None

        self.camera_driver = camera_driver
        return cam

    # take exposure
    # roi is (xleft, ytop, width, height)
    def take_exposure(self, cam, exposure, output_filename, roi=None):
        """
        Start an exposure with specified camera and wait until it completes.

        The ROI is specified by a tuple/list with the following values:
            (upper x, leftmost y, width, height)

        :param cam: Camera object
        :type cam: Camera object
        :param exposure: Length of exposure.
        :type exposure: float
        :param output_filename: Filename for output image.
        :type output_filename: str
        :param roi: Region of interest, defaults to None
        :type roi: list, optional
        :return: DESCRIPTION
        :rtype: TYPE

        """

        # reset frame to desired roi
        cam.set_binning(1, 1)

        if roi is None:
            width, height = cam.get_size()
            cam.set_frame(0, 0, width, height)
        else:
            cam.set_frame(roi[0], roi[1], roi[2], roi[3])

        cam.start_exposure(exposure)

        elapsed = 0
        while (exposure - elapsed > 2) or not cam.check_exposure():
            logging.debug(f"Taking image with camera {elapsed} of {exposure} seconds")
            time.sleep(0.25)
            elapsed += 0.25
            if elapsed > exposure:
                elapsed = exposure

        logging.debug('Exposure complete')

        ff = os.path.join(os.getcwd(), output_filename)

        retries = 0
        while True:
            logging.debug(f"Going to save {ff}")

            # FIXME we only call this because the
            # MaximDL backend needs it to save to disk
            # RPC backend already has saved it to disk by now
            #if BACKEND == 'INDI':
            if not cam.supports_saveimage():
                # FIXME need better way to handle saving image to file!
                image_data = cam.get_image_data()

                #
                # FIXME INDIBackend returns a FITS image
                #       ASCOMBackend returns a numpy array
                #       This is a temporary HACK to address this
                #       but needs to be better handled!
                #
                try:
                    pri_header = image_data[0].header
                    image_data = image_data[0].data
                except:
                    pass

                pyfits.writeto(ff, image_data, overwrite=True)

                result = True
            else:
                result = cam.save_image_data(ff)

            if result is True:
                logging.debug("Save successful")
                break

            retries += 1
            if retries > 3:
                logging.error(f"Failed to save {ff}!! Aborting!")
                return False

            logging.error(f"Failed to save {ff}!! Trying again")
            time.sleep(2)

        return True
