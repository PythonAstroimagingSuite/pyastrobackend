import sys
import time
import argparse
import logging

from pyastrobackend.BackendConfig import get_backend

if __name__ == '__main__':
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'

    logging.basicConfig(filename='pyastrobackend_filterwheel_tests.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format=FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    LOG = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    CH = logging.StreamHandler()
    CH.setLevel(logging.INFO)
    CH.setFormatter(formatter)
    LOG.addHandler(CH)

    logging.info(f'pyastrobackend_filterwheel_tests starting')

    parser = argparse.ArgumentParser()
    parser.add_argument('backend',
                        choices = ['ASCOM', 'RPC', 'ALPACA', 'INDI'],
                        help="Backend to use")
    parser.add_argument('driver', type=str, help="Driver name to use")

    args = parser.parse_args()
    logging.info(f'command args = {args}')

    if args.backend is None:
        logging.error('Must supply name of backend to use!')
        sys.exit(1)

    if args.driver is None:
        logging.error('Must supply name of driver to use!')
        sys.exit(1)

    logging.info(f'connecting to backend {args.backend}')
    backend = get_backend(args.backend)
    rc = backend.connect()

    logging.info(f'result of connect to backend = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to focuser
    wheel = backend.newFilterWheel()

    logging.info(f'Connecting to FilterWheel driver {args.driver}')
    rc = wheel.connect(args.driver)
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {wheel.is_connected()}')

    logging.info('Getting wheel current position')
    origpos = wheel.get_position()
    logging.info(f'cur pos = {origpos}')

    if origpos is None:
        sys.exit(1)

    logging.info('Getting wheel current position name')
    origpos_name = wheel.get_position_name()
    logging.info(f'cur pos name = {origpos_name}')

    if origpos_name is None:
        sys.exit(1)

    logging.info('Getting number positions')
    numpos = wheel.get_num_positions()
    logging.info(f'num pos = {numpos}')

    if numpos is None:
        sys.exit(1)

    logging.info('Getting wheel names')
    names = wheel.get_names()
    logging.info(f'names = {names}')

    if names is None:
        sys.exit(1)

    if origpos > numpos/2:
        target = 0
    else:
        target = numpos-1

    logging.info(f'target pos = {target}')

    logging.info(f'Moving to {target}')
    rc = wheel.set_position(target)
    logging.info(f'rc for move is {rc}')

    if not rc:
        logging.error('Failed to move - quitting')
        sys.exit(-1)

    while True:
        logging.info('Getting wheel position')
        curpos = wheel.get_position()
        logging.info(f'cur pos = {curpos}')
        logging.info(f'is_moving = {wheel.is_moving()}')
        if curpos != -1:
            break
        time.sleep(0.5)

    logging.info(f'moving back to original pos name of {origpos_name}')
    rc = wheel.set_position_name(origpos_name)

    if not rc:
        logging.error('Failed to move - quitting')
        sys.exit(-1)

    while True:
        logging.info('Getting wheel position')
        curpos = wheel.get_position()
        logging.info(f'cur pos = {curpos}')
        logging.info(f'is_moving = {wheel.is_moving()}')
        if curpos != -1:
            break
        time.sleep(0.5)

    logging.info('Done!')
