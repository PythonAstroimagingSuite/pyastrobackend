import sys
import time
import logging

from pyastrobackend.RPCBackend import DeviceBackend as Backend
from pyastrobackend.RPC.Mount import Mount as RPC_Mount

if __name__ == '__main__':


    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'

    logging.basicConfig(filename='pyastrobackend_rpc_mount_tests.log',
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

    logging.info(f'pyastrobackend_rpc_mount_tests starting')

    logging.info('connecting to rpc server')
    backend = Backend()
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        logging.error('unable to connect to server')
        sys.exit(-1)

    # connect to focuser
    mount = RPC_Mount()

    logging.info('Connecting to Mount')
    #rc = mount.connect('Telescope Simulator')
    rc = mount.connect('RPCMount')
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

