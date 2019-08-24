import os
import sys
import time
import logging

import astropy.io.fits as pyfits

from pyastrobackend.AlpacaBackend import DeviceBackend as Backend
from pyastrobackend.Alpaca.Mount import Mount

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

    logging.info(f'pyastrobackend_alpaca_mount_tests starting')

    logging.info('connecting to alpaca server')
    backend = Backend('127.0.0.1', 11111)
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to mount
    mount = Mount(backend)

    logging.info('Connecting to Mount')
    rc = mount.connect('ALPACA:telescope:0')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    iscon = mount.is_connected()
    logging.info(f'is_connected() returns {iscon}')
    if not iscon:
        logging.error('Not connected!')
        sys.exit(1)

    logging.info('Getting CanPark')
    canpark = mount.can_park()
    logging.info(f'CanPark = {canpark}')

    logging.info('Getting IsParked')
    isparked = mount.is_parked()
    logging.info(f'IsParked = {isparked}')

    logging.info('Getting alt/az position')
    alt, az = mount.get_position_altaz()
    logging.info(f'alt/az = {alt} {az}')

    logging.info('Getting ra/dec position')
    ra, dec = mount.get_position_radec()
    logging.info(f'ra/dec = {ra} {dec}')

    logging.info('Getting pier side')
    side = mount.get_pier_side()
    logging.info(f'pier side = {side}')

    logging.info('Getting tracking')
    track = mount.get_tracking()
    logging.info(f'tracking = {track}')

    newtrack = not track
    logging.info(f'Setting tracking to {newtrack}')
    rc = mount.set_tracking(newtrack)
    if not rc:
        logging.error('Error setting tracking!')
        sys.exit(1)

    logging.info('Getting tracking')
    track = mount.get_tracking()
    logging.info(f'tracking = {track}')
