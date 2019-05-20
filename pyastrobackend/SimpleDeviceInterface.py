import os
import time
import logging

def get_backend_for_os():
    import os
    # chose an implementation, depending on os
    if os.name == 'nt': #sys.platform == 'win32':
        return 'ASCOM'
    elif os.name == 'posix':
        return 'INDI'
    else:
        raise Exception("Sorry: no implementation for your platform ('%s') available" % os.name)

if 'PYASTROBACKEND' in os.environ:
    BACKEND = os.environ['PYASTROBACKEND']
else:
    BACKEND = get_backend_for_os()

#print(f'SimpleDeviceInterface: BACKEND = {BACKEND}')

# debugging override with simulator
#BACKEND = 'SIMULATOR'

if BACKEND == 'ASCOM':
    from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
elif BACKEND == 'INDI':
    from pyastrobackend.INDIBackend import DeviceBackend as Backend
elif BACKEND == 'SIMULATOR':
    from pyastrobackend.SimpleSimulator.SimpleSimulatorDrivers import DeviceBackend as Backend
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')


if BACKEND == 'ASCOM':
    from pyastrobackend.ASCOM.Focuser import Focuser
elif BACKEND == 'INDI':
    from pyastrobackend.INDIBackend import Focuser
elif BACKEND == 'SIMULATOR':
    from pyastrobackend.SimpleSimulator.SimpleSimulatorDrivers import Focuser
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')


if BACKEND == 'ASCOM':
    from pyastrobackend.MaximDL.Camera import Camera as MaximDL_Camera
elif BACKEND == 'INDI':
    from pyastrobackend.INDIBackend import Camera as INDI_Camera
elif BACKEND == 'SIMULATOR':
    from pyastrobackend.SimpleSimulator.SimpleSimulatorDrivers import Camera as Sim_Camera
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')

class SimpleDeviceInterface:
    def __init__(self):
        self.backend = Backend()

    def connect_backend(self):
        rc = self.backend.connect()
        if not rc:
            logging.error('Failed to connect to backend!')

        return rc

    def connect_focuser(self, driver):
        rc = None
        if BACKEND == 'ASCOM':
            focuser = Focuser()
            rc = focuser.connect(driver)
        elif BACKEND == 'INDI':
            focuser = Focuser(self.backend)
            rc = focuser.connect(driver)
        elif BACKEND == 'SIMULATOR':
            focuser = Focuser()
            rc = True

        if rc:
            return focuser
        else:
            return None

    def wait_on_focuser_move(self, focuser, timeout=60):
        ts = time.time()
        while (time.time()-ts) < timeout:
            logging.info(f'waiting on focuser move - curpos = {focuser.get_absolute_position()}')
            if not focuser.is_moving():
                break
            time.sleep(0.5)
        time.sleep(0.5) # just be sure its done

    # FIXME INDI stuff is broken!!!!
    def connect_camera(self, camera_driver):
        if BACKEND == 'ASCOM':
            #driver = 'MaximDL'
            cam = MaximDL_Camera()
        elif BACKEND == 'INDI':
            #driver = 'INDICamera'
            cam = INDI_Camera(self.backend)
        elif BACKEND == 'SIMULATOR':
            #driver = 'Simulator'
            cam = Sim_Camera()

        logging.info(f'connect_camera: driver =  {camera_driver}')

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
    def take_exposure(self, cam, focus_expos, output_filename):

        focus_expos = 1

        # reset frame to full sensor
        cam.set_binning(1, 1)
        width, height = cam.get_size()
        cam.set_frame(0, 0, width, height)
        cam.start_exposure(focus_expos)

        # give things time to happen (?) I get Maxim not ready errors so slowing it down
        time.sleep(0.25)

        elapsed = 0
        while not cam.check_exposure():
            logging.info(f"Taking image with camera {elapsed} of {focus_expos} seconds")
            time.sleep(0.5)
            elapsed += 0.5
            if elapsed > focus_expos:
                elapsed = focus_expos

        logging.info('Exposure complete')
        # give it some time seems like Maxim isnt ready if we hit it too fast
        time.sleep(0.5)

        ff = os.path.join(os.getcwd(), output_filename)

        retries = 0
        while True:
            logging.info(f"Going to save {ff}")

            # FIXME we only call this because the
            # MaximDL backend needs it to save to disk
            # RPC backend already has saved it to disk by now
            if BACKEND == 'INDI':
                # FIXME need better way to handle saving image to file!
                image_data = cam.get_image_data()
                # this is an hdulist
                image_data.writeto(ff, overwrite=True)
                result = True
            else:
                result = cam.save_image_data(ff)

            if result is True:
                logging.info("Save successful")
                break

            retries += 1
            if retries > 3:
                logging.error(f"Failed to save {ff}!! Aborting!")
                return False

            logging.error(f"Failed to save {ff}!! Trying again")
            time.sleep(1)

        return True
