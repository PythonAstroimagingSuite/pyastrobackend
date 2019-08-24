import sys
import time
import logging
import argparse

from pyastrobackend.BackendConfig import get_backend, get_backend_choices

if __name__ == '__main__':
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'

    logging.basicConfig(filename='pyastrobackend_mount_tests.log',
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

    logging.info(f'pyastrobackend_mount_tests starting')

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
    mount = backend.newMount()

    logging.info(f'Connecting to mount driver {args.driver}')
    rc = mount.connect(args.driver)
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {mount.is_connected()}')

    logging.info('Getting mount ra/dec position')
    (ra, dec) = mount.get_position_radec()
    logging.info(f'ra/dec pos = {ra} {dec}')

    logging.info('Getting mount alt/az position')
    (alt, az) = mount.get_position_altaz()
    logging.info(f'altaz pos = {alt} {az}')

    new_dec = dec + 30
    if new_dec > 90:
        new_dec = dec - 30

    logging.info(f'Slewing to {ra} {new_dec}')
    rc = mount.slew(ra, new_dec)
    logging.info(f'slew rc = {rc}')
    if not rc:
        logging.error('unable to slew')
        sys.exit(-1)

    while True:
        (ra, dec) = mount.get_position_radec()
        (alt, az) = mount.get_position_altaz()
        is_slewing = mount.is_slewing()
        logging.info(f'   ra/dec pos = {ra:5.2f} {dec:5.2f} altaz pos = {alt} {az} is_slewing = {is_slewing}')

        if is_slewing is False:
            logging.info('Slew end detected!')
            break

    time.sleep(1)

    new_dec = dec + 20
    stop_dec = dec + 10
    if new_dec > 90:
        new_dec = dec - 20
        stop_dec = dec - 10

    logging.info(f'Slewing to {ra} {new_dec}')
    rc = mount.slew(ra, new_dec)
    logging.info(f'slew rc = {rc}')
    if not rc:
        logging.error('unable to slew')
        sys.exit(-1)

    while True:
        (ra, dec) = mount.get_position_radec()
        (alt, az) = mount.get_position_altaz()
        is_slewing = mount.is_slewing()
        logging.info(f'   ra/dec pos = {ra:5.2f} {dec:5.2f} altaz pos = {alt} {az} is_slewing = {is_slewing}')

        if abs(dec - stop_dec) < 2:
            logging.info('Stopping mount!')
            rc = mount.abort_slew()
            logging.info(f'rc for abort_slew is {rc}')

        if is_slewing is False:
            logging.info('Slew end detected!')
            break

    time.sleep(1)

    logging.info('Getting mount ra/dec position')
    (ra, dec) = mount.get_position_radec()
    logging.info(f'ra/dec pos = {ra} {dec}')
    logging.info(f'Syncing to {ra} {dec-1}')
    rc = mount.sync(ra, new_dec-1)
    logging.info(f'slew rc = {rc}')
    logging.info('Getting mount ra/dec position')
    (ra, dec) = mount.get_position_radec()
    logging.info(f'ra/dec pos = {ra} {dec}')

    sys.exit(0)

