import os
import sys
import time
import logging
import argparse

import astropy.io.fits as pyfits

# FIXME should this be available via SimpleDeviceInterface API?
from pyastrobackend.BackendConfig import get_backend_choices

from pyastrobackend.SimpleDeviceInterface import SimpleDeviceInterface as SDI

if __name__ == '__main__':
#    FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'
    logging.basicConfig(filename='pyastrobackend_simpledevice_ccd_tests.log',
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

    logging.info(f'pyastrobackend_simpledevice_ccd_tests starting')

    parser = argparse.ArgumentParser()
    parser.add_argument('backend',
                        choices = get_backend_choices(),
                        help="Backend to use")
    parser.add_argument('driver', type=str, help="Driver name to use")
    parser.add_argument('--debug', action='store_true', help="Enable debug output")

    args = parser.parse_args()
    logging.info(f'command args = {args}')

    if args.driver is None:
        logging.error('Must supply name of driver to use!')
        sys.exit(1)

    if args.debug:
        CH.setLevel(logging.DEBUG)

    if args.backend is None:
        logging.info('connecting to default backend')
    else:
        logging.info(f'connecting to backend {args.backend}')

    sdi = SDI()
    rc = sdi.connect_backend(args.backend)

    logging.info(f'result of connect to backend = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to focuser
    logging.info(f'Connecting to camera driver {args.driver}')
    camera = sdi.connect_camera(args.driver)
    logging.info(f'connect result = {camera}')

    if not camera:
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

    logging.info('Getting cooler power')
    cool_power = camera.get_cooler_power()
    logging.info(f'cooler power = {cool_power}')

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

    logging.info('Taking image')
    rc = camera.start_exposure(5)
    if not rc:
        logging.error('Failed to start exposure - quitting')
        sys.exit(-1)

    while True:
        done = camera.check_exposure()
        logging.info(f'check_exposure = {done}')
        if done:
            break
        time.sleep(1)

    fileloc = os.path.join(os.getcwd(), 'pyastrobackend_simpledevice_ccd_tests.fits')

    logging.info(f'Writing image data to {fileloc}')

    roi = (100, 100, 100, 100)
    rc = sdi.take_exposure(camera, 5, fileloc, roi=roi)
    if rc is None:
        logging.error('Failed to take image!')
        sys.exit(1)


    logging.info('Done')
