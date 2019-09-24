import os
import time
import logging

import astropy.io.fits as pyfits

from pyastrobackend.BackendConfig import get_backend_for_os, get_backend, get_backend_choices

#def get_backend_for_os():
#    import os
#    # chose an implementation, depending on os
#    if os.name == 'nt': #sys.platform == 'win32':
#        return 'ASCOM'
#    elif os.name == 'posix':
#        return 'INDI'
#    else:
#        raise Exception("Sorry: no implementation for your platform ('%s') available" % os.name)
#
#if 'PYASTROBACKEND' in os.environ:
#    BACKEND = os.environ['PYASTROBACKEND']
#else:
#    BACKEND = get_backend_for_os()
#
##print(f'SimpleDeviceInterface: BACKEND = {BACKEND}')
#
## debugging override with simulator
##BACKEND = 'SIMULATOR'
#
#if BACKEND == 'ASCOM':
#    from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
#elif BACKEND == 'INDI':
#    from pyastrobackend.INDIBackend import DeviceBackend as Backend
#elif BACKEND == 'SIMULATOR':
#    from pyastrobackend.SimpleSimulator.SimpleSimulatorDrivers import DeviceBackend as Backend
#else:
#    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')
#
#if BACKEND == 'ASCOM':
#    from pyastrobackend.ASCOM.Focuser import Focuser as ASCOM_Focuser
#    from pyastrobackend.RPC.Focuser import Focuser as RPC_Focuser
#elif BACKEND == 'INDI':
#    from pyastrobackend.INDIBackend import Focuser
#elif BACKEND == 'SIMULATOR':
#    from pyastrobackend.SimpleSimulator.SimpleSimulatorDrivers import Focuser
#else:
#    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')
#
#if BACKEND == 'ASCOM':
#    from pyastrobackend.ASCOM.FilterWheel import FilterWheel
#elif BACKEND == 'INDI':
#    from pyastrobackend.INDIBackend import FilterWheel
#elif BACKEND == 'SIMULATOR':
#    raise Exception('SIMULATOR driver not supported for FilterWheel')
#else:
#    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')
#
#if BACKEND == 'ASCOM':
#    from pyastrobackend.MaximDL.Camera import Camera as MaximDL_Camera
#    from pyastrobackend.RPC.Camera import Camera as RPC_Camera
#elif BACKEND == 'INDI':
#    from pyastrobackend.INDIBackend import Camera as INDI_Camera
#elif BACKEND == 'SIMULATOR':
#    from pyastrobackend.SimpleSimulator.SimpleSimulatorDrivers import Camera as Sim_Camera
#else:
#    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')

class SimpleDeviceInterface:
    def __init__(self):
        pass
        #def_backend = get_backend_for_os()
        #self.backend = get_backend(def_backend)

    def connect_backend(self, backend_name=None):
        if backend_name is None:
            backend_name = get_backend_for_os()

        logging.info(f'SDI:connect_backend: backend={backend_name}')

        self.backend = get_backend(backend_name)

        rc = self.backend.connect()
        if not rc:
            logging.error('Failed to connect to backend!')

        return rc

    def connect_focuser(self, driver):
        rc = None

#        if BACKEND == 'ASCOM':
#            if driver == 'RPC':
#                focuser = RPC_Focuser()
#            else:
#                focuser = Focuser()
#            rc = focuser.connect(driver)
#        elif BACKEND == 'INDI':
#            focuser = Focuser(self.backend)
#            rc = focuser.connect(driver)
#        elif BACKEND == 'SIMULATOR':
#            focuser = Focuser()
#            rc = True

        focuser = self.backend.newFocuser()
        rc = focuser.connect(driver)

        if rc:
            return focuser
        else:
            return None

    def connect_filterwheel(self, driver):
        rc = None

#        if BACKEND == 'ASCOM':
#            wheel = FilterWheel()
#            rc = wheel.connect(driver)
#        elif BACKEND == 'INDI':
#            wheel = FilterWheel(self.backend)
#            rc = wheel.connect(driver)
#        elif BACKEND == 'SIMULATOR':
#            wheel = FilterWheel()
#            rc = True

        wheel = self.backend.newFilterWheel()
        rc = wheel.connect(driver)

        if rc:
            return wheel
        else:
            return None

    def wait_on_focuser_move(self, focuser, timeout=60):
        ts = time.time()
        lastpos = focuser.get_absolute_position()
        ntimes = 0
        while (time.time()-ts) < timeout:
            logging.debug(f'waiting on focuser move - curpos = {focuser.get_absolute_position()}')

            curpos = focuser.get_absolute_position()
            if abs(curpos - lastpos) < 1:
                ntimes = 3
                break

#            if abs(curpos - lastpos) < 1:
#                ntimes += 1
#
#            if ntimes > 2:
#                break

            lastpos = curpos

#   FIXME This doesn't seem to work in pyastro37 env under windows????
#            if not focuser.is_moving():
#                break

            time.sleep(0.5)

        #time.sleep(0.5) # just be sure its done

        return ntimes > 2

    # FIXME INDI stuff is broken!!!!
    def connect_camera(self, camera_driver):
#        if BACKEND == 'ASCOM':
#            #driver = 'MaximDL'
#            if camera_driver == 'MaximDL':
#                cam = MaximDL_Camera()
#            elif camera_driver == 'RPC':
#                cam = RPC_Camera()
#        elif BACKEND == 'INDI':
#            #driver = 'INDICamera'
#            cam = INDI_Camera(self.backend)
#        elif BACKEND == 'SIMULATOR':
#            #driver = 'Simulator'
#            cam = Sim_Camera()

        logging.debug(f'connect_camera: driver =  {camera_driver}')
        cam = self.backend.newCamera()
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
        return cam

    # take exposure
    # roi is (xleft, ytop, width, height)
    def take_exposure(self, cam, focus_expos, output_filename, roi=None):

        # reset frame to desired roi
        cam.set_binning(1, 1)

        if roi is None:
            width, height = cam.get_size()
            cam.set_frame(0, 0, width, height)
        else:
            cam.set_frame(roi[0], roi[1], roi[2], roi[3])

        cam.start_exposure(focus_expos)

        # give things time to happen (?) I get Maxim not ready errors so slowing it down
        time.sleep(0.25)

        elapsed = 0
        while (focus_expos-elapsed > 2) or not cam.check_exposure():
            logging.debug(f"Taking image with camera {elapsed} of {focus_expos} seconds")
            time.sleep(0.25)
            elapsed += 0.25
            if elapsed > focus_expos:
                elapsed = focus_expos

        logging.debug('Exposure complete')
        # give it some time seems like Maxim isnt ready if we hit it too fast
        #time.sleep(1)

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
