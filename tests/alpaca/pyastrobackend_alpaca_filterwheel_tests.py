import os
import sys
import time
import logging

import astropy.io.fits as pyfits

from pyastrobackend.AlpacaBackend import DeviceBackend as Backend
from pyastrobackend.Alpaca.FilterWheel import FilterWheel

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
    CH.setLevel(logging.INFO)
    CH.setFormatter(formatter)
    LOG.addHandler(CH)

    logging.info(f'pyastrobackend_alpaca_filterwheel_tests starting')

    logging.info('connecting to alpaca server')
    backend = Backend('127.0.0.1', 11111)
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to filterwheel
    filterwheel = FilterWheel(backend)

    logging.info('Connecting to FilterWheel')
    rc = filterwheel.connect('ALPACA:filterwheel:0')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    iscon = filterwheel.is_connected()
    logging.info(f'is_connected() returns {iscon}')
    if not iscon:
        logging.error('Not connected!')
        sys.exit(1)


    logging.info('Getting position')
    pos = filterwheel.get_position()
    logging.info(f'position = {pos}')

    logging.info('Getting pos by name')
    posname = filterwheel.get_position_name()
    logging.info(f'position name = {posname}')

    logging.info('Getting number positions')
    numpos = filterwheel.get_num_positions()
    logging.info(f'Number positions = {numpos}')

    logging.info('Getting position names')
    names = filterwheel.get_names()
    logging.info(f'Position names = {names}')

    logging.info('Moving to position 0')
    rc = filterwheel.set_position(0)
    if not rc:
        logging.error('Error setting position!')
        sys.exit(1)

    while filterwheel.is_moving():
        logging.info('Moving...')
        time.sleep(0.5)

    logging.info('Getting position')
    pos = filterwheel.get_position()
    logging.info(f'position = {pos}')

    logging.info('Getting pos by name')
    posname = filterwheel.get_position_name()
    logging.info(f'position name = {posname}')

    logging.info(f'Moving to position {numpos-1}')
    rc = filterwheel.set_position(numpos-1)
    if not rc:
        logging.error('Error setting position!')
        sys.exit(1)

    while filterwheel.is_moving():
        logging.info('Moving...')
        time.sleep(0.5)

    logging.info('Getting position')
    pos = filterwheel.get_position()
    logging.info(f'position = {pos}')

    logging.info('Getting pos by name')
    posname = filterwheel.get_position_name()
    logging.info(f'position name = {posname}')
