import os
import sys
import time
import logging

from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
from pyastrobackend.RPC.Camera import Camera as RPC_Camera

EXIT_ON_ERROR = False

if __name__ == '__main__':
#    FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'
    logging.basicConfig(filename='pyastrobackend_rpc_stress_test.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format=FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    LOG = logging.getLogger()
    formatter = logging.Formatter(FORMAT)
    CH = logging.StreamHandler()
    CH.setLevel(logging.INFO)
    CH.setFormatter(formatter)
    LOG.addHandler(CH)

    logging.info(f'pyastrobackend_rpc_stress_test starting')

    logging.info('connecting to rpc server')
    backend = Backend()
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to camera
    #camera = INDIBackend.Camera(backend.indiclient)
    #camera = backend.newCamera()
    camera = RPC_Camera()

    logging.info('Connecting to CCD')
    rc = camera.connect('CCD Simulator')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {camera.is_connected()}')

    logging.info('Getting pixel size')
    logging.info(f'pixel size = {camera.get_pixelsize()}')

    exposure_active = False

    while True:
        if not exposure_active:
            logging.info('Taking image')
            rc = camera.start_exposure(1)
            if not rc:
                logging.error('Failed to start exposure - quitting')
                if EXIT_ON_ERROR:
                    sys.exit(1)
            exposure_active = True
        else:
            done = camera.check_exposure()
            logging.info(f'check_exposure = {done}')
            if done:
                fileloc = os.path.join(os.getcwd(), 'pyastrobackend_rpc_stress_test.fits')
                logging.info(f'saving image to {fileloc}')
                rc = camera.save_image_data(fileloc, overwrite=True)
                if not rc:
                    logging.error('Error saving image')
                    if EXIT_ON_ERROR:
                        sys.exit(1)
                exposure_active = False

        logging.info('Getting current temp')
        ccd_temp = camera.get_current_temperature()
        logging.info(f'current temp = {ccd_temp}')
        if ccd_temp is None:
            logging.error('Error reading temperature')
            if EXIT_ON_ERROR:
                sys.exit(1)



