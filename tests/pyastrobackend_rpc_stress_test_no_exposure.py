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
    logging.basicConfig(level=logging.DEBUG,
                        format=FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    # LOG = logging.getLogger()
    # formatter = logging.Formatter(FORMAT)
    # CH = logging.StreamHandler()
    # CH.setLevel(logging.INFO)
    # CH.setFormatter(formatter)
    # LOG.addHandler(CH)

    logging.info(f'pyastrobackend_rpc_stress_test_no_exposure starting')

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

    while True:
        logging.info('Getting current temp')
        ccd_temp = camera.get_current_temperature()
        logging.info(f'current temp = {ccd_temp}')
        if ccd_temp is None:
            logging.error('Error reading temperature')
            if EXIT_ON_ERROR:
                sys.exit(1)



