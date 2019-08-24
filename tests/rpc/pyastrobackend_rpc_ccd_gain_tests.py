import os
import sys
import time
import logging

from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
from pyastrobackend.RPC.Camera import Camera as RPC_Camera

if __name__ == '__main__':
#    FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'
    logging.basicConfig(filename='pyastrobackend_rpc_ccd_tests.log',
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

    logging.info(f'pyastrobackend_rpc_ccd_tests starting')

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

    gain = 200
    logging.info(f'gain = {gain}')
    camera.set_camera_gain(gain)


    for i in range(0, 2):

        logging.info(f'Taking image # {i}')
        rc = camera.start_exposure(1)
        if not rc:
            logging.error('Failed to start exposure - quitting')
            sys.exit(-1)

        while True:
            done = camera.check_exposure()
            logging.info(f'check_exposure = {done}')
            if done:
                break
            time.sleep(1)

        fileloc = os.path.join(os.getcwd(), f'pyastrobackend_rpc_ccd_gain_test_gain_{gain}_{i}.fits')
        logging.info(f'saving image to {fileloc}')
        camera.save_image_data(fileloc, overwrite=True)
        #logging.info(f'hdulist = {hdulist}')

    logging.info('Done')





