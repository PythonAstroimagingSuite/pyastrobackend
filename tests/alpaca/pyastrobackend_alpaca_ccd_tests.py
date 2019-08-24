import os
import sys
import time
import logging

import astropy.io.fits as pyfits

from pyastrobackend.AlpacaBackend import DeviceBackend as Backend
from pyastrobackend.Alpaca.Camera import Camera

if __name__ == '__main__':
#    FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'
    logging.basicConfig(filename='pyastrobackend_alpaca_ccd_tests.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format=FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    LOG = logging.getLogger()
    formatter = logging.Formatter(FORMAT)
    CH = logging.StreamHandler()
    CH.setLevel(logging.DEBUG)
    CH.setFormatter(formatter)
    LOG.addHandler(CH)

    logging.info(f'pyastrobackend_alpaca_ccd_tests starting')

    logging.info('connecting to alpaca server')
    backend = Backend('127.0.0.1', 11111)
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to camera
    #camera = INDIBackend.Camera(backend.indiclient)
    #camera = backend.newCamera()
    camera = Camera(backend)

    logging.info('Connecting to CCD')
    rc = camera.connect('ALPACA:camera:0')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {camera.is_connected()}')

    logging.info('Getting pixel size')
    logging.info(f'pixel size = {camera.get_pixelsize()}')

    logging.info('Getting current temp')
    ccd_temp = camera.get_current_temperature()
    logging.info(f'current temp = {ccd_temp}')

    logging.info('Getting cooler state')
    cool_state = camera.get_cooler_state()
    logging.info(f'cooler state = {cool_state}')

    logging.info('Turning off cooler')
    rc = camera.set_cooler_state(False)
    logging.info(f'set_cooler_state returns {rc}')

    i = 0
    while i < 5:
        logging.info('Getting current temp')
        ccd_temp = camera.get_current_temperature()
        logging.info(f'current temp = {ccd_temp}')
        time.sleep(0.5)
        i += 1

    logging.info('Turning on cooler')
    rc = camera.set_cooler_state(True)
    logging.info(f'set_cooler_state returns {rc}')

    logging.info('Setting temp to -10C')
    rc = camera.set_target_temperature(-10)
    logging.info(f'set_target_temperature returns {rc}')

    i = 0
    while i < 5:
        logging.info('Getting current temp')
        ccd_temp = camera.get_current_temperature()
        logging.info(f'current temp = {ccd_temp}')

        logging.info('Getting cooler power')
        cool_power = camera.get_cooler_power()
        logging.info(f'cooler power = {cool_power}')

        time.sleep(0.5)
        i += 1

    logging.info('Getting binning')
    binx, biny = camera.get_binning()
    logging.info(f'binx, biny = {binx}, {biny}')

    logging.info('Setting binning to 2x2')
    camera.set_binning(2, 2)

    logging.info('Getting sensor size')
    (w, h) = camera.get_size()
    logging.info(f'size = {w} x {h}')

    logging.info('Getting roi')
    (rx, ry, rw, rh) = camera.get_frame()
    logging.info(f'roi = {rx} {ry} {rw} {rh}')

    logging.info('Setting roi')
    camera.set_frame(100, 100, 100, 100)

    # uncomment to get full image at 1x1 bin
    camera.set_binning(1, 1)
    camera.set_frame(0, 0, w, h)

    logging.info('Taking image')
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

    fileloc = os.path.join(os.getcwd(), 'pyastrobackend_alpaca_ccd_tests.fits')
    logging.info(f'saving image to {fileloc}')
    image_data = camera.get_image_data()
    pyfits.writeto(fileloc, image_data, overwrite=True)

    logging.info('Done')





