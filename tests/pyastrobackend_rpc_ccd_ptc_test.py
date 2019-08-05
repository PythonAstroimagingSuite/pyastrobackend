import os
import sys
import time
import logging
import argparse

from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
from pyastrobackend.RPC.Camera import Camera as RPC_Camera

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str, help='Identifier for run - used in output filename')
    parser.add_argument('--gain', type=int, help='Gain to use (if not given uses default)')
    parser.add_argument('--window', type=int, default=100, help='Take centered ROI window X window pixels')
    parser.add_argument('--exposures', type=float, nargs='+', default=None, help='List of exposures to use')
    parser.add_argument('--debug', action='store_true', help='Set log level DEBUG')

    args = parser.parse_args()
    logging.debug(f'cmd args = {args}')
    return args

if __name__ == '__main__':
    LONG_FORMAT = '%(asctime)s.%(msecs)03d [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'
    SHORT_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s'
    logging.basicConfig(filename='pyastrobackend_rpc_ccd_ptc_test.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format=LONG_FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    LOG = logging.getLogger()
#    formatter = logging.Formatter(FORMAT)
#    CH = logging.StreamHandler()
#    CH.setLevel(logging.INFO)
#    CH.setFormatter(formatter)
#    LOG.addHandler(CH)

    args = parse_command_line()

    CH = logging.StreamHandler()

    if args.debug:
        formatter = logging.Formatter(LONG_FORMAT)
        CH.setLevel(logging.DEBUG)
        CH.setFormatter(formatter)
    else:
        formatter = logging.Formatter(SHORT_FORMAT)
        CH.setLevel(logging.INFO)
        CH.setFormatter(formatter)
    LOG.addHandler(CH)

    logging.info(f'pyastrobackend_rpc_ccd_tests starting')

    if args.exposures is None:
        logging.error('Must provide list of exposures to use with --exposures')
        sys.exit(1)

    logging.info('connecting to rpc server')
    backend = Backend()
    rc = backend.connect()

    logging.info(f'result of connect to server = {rc}')
    if not rc:
        sys.exit(-1)

    # connect to camera
    camera = RPC_Camera()

    logging.info('Connecting to CCD')
    rc = camera.connect('RPCCamera')
    logging.info(f'connect result = {rc}')

    if not rc:
        logging.error('Failed to connect - quitting')
        sys.exit(-1)

    logging.info(f'is_connected() returns {camera.is_connected()}')

    if args.gain is not None:
        logging.info(f'Using gain = {args.gain}')
        camera.set_camera_gain(args.gain)
        gain = args.gain
    else:
        gain = camera.get_camera_gain()
        if gain is None:
            logging.error('No gain specified and unable to read default gain!')
            sys.exit(1)
        logging.info(f'Using default gain of {gain}')

    # figure out ROI
    w, h = camera.get_size()
    logging.info(f'Sensor is {w} x {h} pixels')
    logging.info(f'Window is {args.window} x {args.window}')
    lx = int((w-args.window)/2)
    uy = int((h-args.window)/2)
    roi = (lx, uy, args.window, args.window)
    logging.info(f'ROI is {roi}')
    camera.set_frame(*roi)

    #
    # exposure sequence:
    #
    #   If start is < 1 then
    #

    for e in args.exposures:
        logging.info(f'Exposure = {e}')

        for i in range(0, 2):
            logging.info(f'Taking image # {i}')
            rc = camera.start_exposure(e)
            if not rc:
                logging.error('Failed to start exposure - quitting')
                sys.exit(-1)

            while True:
                done = camera.check_exposure()
                logging.info(f'check_exposure = {done}')
                if done:
                    break
                time.sleep(1)

            fileloc = os.path.join(os.getcwd(), f'{args.name}_ptc_test_gain_{gain}_{e}s-{i:03d}.fits')
            logging.info(f'saving image to {fileloc}')
            camera.save_image_data(fileloc, overwrite=True)
        #logging.info(f'hdulist = {hdulist}')

    logging.info('Done')





