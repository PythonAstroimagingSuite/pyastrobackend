import sys
import time
import logging

from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
from pyastrobackend.RPC.Focuser import Focuser as RPC_Focuser

if __name__ == '__main__':
    logging.basicConfig(filename='pyastrobackend_rpc_focuser_tests.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    LOG = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    CH = logging.StreamHandler()
    CH.setLevel(logging.DEBUG)
    CH.setFormatter(formatter)
    LOG.addHandler(CH)

    logging.info(f'pyastrobackend_rpc_focuser_tests starting')

    logging.info('connecting to rpc server')
    backend = Backend()
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to focuser
    #focuser = backend.newFocuser()
    focuser = RPC_Focuser()

    logging.info('Connecting to Focsuer')
    #rc = focuser.connect('Focuser Simulator')
    rc = focuser.connect('RPCFocuser')
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

    target = origpos + 1000
    if target > max_abspos:
        logging.error('Move test would move past max pos of {max_abspos}')
        sys.exit(1)

    logging.info(f'Moving to {target}')
    rc = focuser.move_absolute_position(target)
    logging.info(f'rc for move is {rc}')
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

    logging.info(f'moving back to original pos of {origpos}')
    rc = focuser.move_absolute_position(origpos)

    while True:
        logging.info('Getting focuser position')
        abspos = focuser.get_absolute_position()
        logging.info(f'abs pos = {abspos}')
        logging.info('Getting focuser temperature')
        focus_temp = focuser.get_current_temperature()
        logging.info(f'Current temp = {focus_temp} C')
        logging.info(f'is_moving = {focuser.is_moving()}')

        time.sleep(2)




