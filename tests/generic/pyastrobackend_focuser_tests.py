import sys
import time
import logging
import argparse

from pyastrobackend.BackendConfig import get_backend, get_backend_choices

if __name__ == '__main__':
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'

    logging.basicConfig(filename='pyastrobackend_focuser_tests.log',
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

    logging.info(f'pyastrobackend_focuser_tests starting')

    parser = argparse.ArgumentParser()
    parser.add_argument('backend',
                        choices = get_backend_choices(),
                        help="Backend to use")
    parser.add_argument('driver', type=str, help="Driver name to use")
    parser.add_argument('--debug', action='store_true', help="Enable debug output")

    args = parser.parse_args()
    logging.info(f'command args = {args}')

    if args.backend is None:
        logging.error('Must supply name of backend to use!')
        sys.exit(1)

    if args.driver is None:
        logging.error('Must supply name of driver to use!')
        sys.exit(1)

    if args.debug:
        CH.setLevel(logging.DEBUG)

    logging.info(f'connecting to backend {args.backend}')
    backend = get_backend(args.backend)
    rc = backend.connect()

    logging.info(f'result of connect to backend = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to focuser
    focuser = backend.newFocuser()

    logging.info(f'Connecting to focuser driver {args.driver}')
    rc = focuser.connect(args.driver)
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {focuser.is_connected()}')

    logging.info('Getting focuser max position')
    max_abspos = focuser.get_max_absolute_position()
    logging.info(f'max abs pos = {max_abspos}')

    if max_abspos is None:
        sys.exit(1)

    logging.info('Getting focuser position')
    origpos = focuser.get_absolute_position()
    logging.info(f'abs pos = {origpos}')

    if origpos is None:
        sys.exit(1)

    if origpos > max_abspos/2:
        target = int(max_abspos*0.1)
    else:
        target = int(max_abspos*0.9)

    logging.info(f'target = {target}')

    if target > max_abspos:
        logging.error(f'Move test would move past max pos of {max_abspos}')
        sys.exit(1)

    logging.info(f'Moving to {target}')
    rc = focuser.move_absolute_position(target)
    logging.info(f'rc for move is {rc}')

    if not rc:
        logging.error('Failed to move - quitting')
        sys.exit(-1)

    i = 0
    while i < 4:
        logging.info('Getting focuser position')
        abspos = focuser.get_absolute_position()
        logging.info(f'abs pos = {abspos}')
        logging.info(f'is_moving = {focuser.is_moving()}')
        time.sleep(0.5)
        i += 1

    logging.info('stopping focuser!')
    rc = focuser.stop()
    logging.info(f'rc for stop is {rc}')

    if not rc:
        logging.error('Failed to stop - quitting')
        sys.exit(-1)

    logging.info(f'moving back to original pos of {origpos}')
    rc = focuser.move_absolute_position(origpos)

    if not rc:
        logging.error('Failed to move - quitting')
        sys.exit(-1)

    while True:
        logging.info('Getting focuser position')
        abspos = focuser.get_absolute_position()
        logging.info(f'abs pos = {abspos}')
        logging.info('Getting focuser temperature')
        focus_temp = focuser.get_current_temperature()
        logging.info(f'Current temp = {focus_temp} C')
        logging.info(f'is_moving = {focuser.is_moving()}')

        if abspos == origpos:
            logging.info(f'Reached {origpos}, test over!')
            break

        time.sleep(2)




