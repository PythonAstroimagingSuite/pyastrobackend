import sys
import time
import logging

from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
from pyastrobackend.ASCOM.Mount import Mount

if __name__ == '__main__':
    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'

    logging.basicConfig(filename='pyastrobackend_mount_tracking_test.log',
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

    logging.info(f'pyastrobackend_mount_tracking_test starting')

    logging.info('connecting to rpc server')
    backend = Backend()
    backend.connect()

    mount = Mount()
    mount.connect('AstrophysicsV2.Telescope')

    track = mount.get_tracking()
    logging.info(f'tracking state = {track}')

    while True:
        track = not track
        logging.info(f'Setting track to {track}')
        rc = mount.set_tracking(track)
        logging.info(f'rc = {rc}')
        time.sleep(5)


    logging.info('done')
