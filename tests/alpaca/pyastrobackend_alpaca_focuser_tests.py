import os
import sys
import time
import logging

import astropy.io.fits as pyfits

from pyastrobackend.AlpacaBackend import DeviceBackend as Backend
from pyastrobackend.Alpaca.Focuser import Focuser

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

    logging.info(f'pyastrobackend_alpaca_focuser_tests starting')

    logging.info('connecting to alpaca server')
    backend = Backend('127.0.0.1', 11111)
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to focuser
    focuser = Focuser(backend)

    logging.info('Connecting to Focuser')
    rc = focuser.connect('ALPACA:focuser:0')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    iscon = focuser.is_connected()
    logging.info(f'is_connected() returns {iscon}')
    if not iscon:
        logging.error('Not connected!')
        sys.exit(1)

    logging.info('Getting max position')
    maxstep = focuser.get_max_absolute_position()
    logging.info(f'maximum position = {maxstep}')

    logging.info('Getting focuser temperature')
    temp = focuser.get_current_temperature()
    logging.info(f'Temperature = {temp}')

    logging.info('Getting current absolute position')
    abspos = focuser.get_absolute_position()
    logging.info(f'Absolute position = {abspos}')

    if abspos > maxstep/2:
        moveto = 0
    else:
        moveto = maxstep-1

    logging.info(f'Moving to absolute pos {moveto}')
    rc = focuser.move_absolute_position(moveto)
    if not rc:
        logging.error('Move command failed!')
        sys.exit(-1)

    i = 0
    while i < 5:
        ism = focuser.is_moving()
        abspos = focuser.get_absolute_position()
        logging.info(f'ismoving = {ism} abspos = {abspos}')
        time.sleep(0.5)
        i += 1

    logging.info('Stopping focuser')
    rc = focuser.stop()
    if not rc:
        logging.error('Stop command failed!')
        sys.exit(-1)

    ism = focuser.is_moving()
    abspos = focuser.get_absolute_position()
    logging.info(f'ismoving = {ism} abspos = {abspos}')
