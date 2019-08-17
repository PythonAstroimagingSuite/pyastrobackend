import os
import sys
import time
import logging
import astropy.io.fits as pyfits

from pyastrobackend.AlpacaBackend import DeviceBackend
from pyastrobackend.Alpaca.Camera import Camera

if __name__ == '__main__':

    logging.basicConfig(filename='alpaca_camera_test.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    log = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    logging.info('alpaca_camera_test Test Mode starting')

    backend = DeviceBackend('127.0.0.1', 11111)
    rc = backend.connect()
    if not rc:
        logging.error('Error connecting to Alpaca backend')
        sys.exit(1)

    cam = Camera(backend)
    rc = cam.connect('ALPACA:camera:0')
    if not rc:
        logging.error('Error connecting to camera')
        sys.exit(1)

    val = cam.is_connected()
    logging.info(f'cam.is_connected() returns {val}')

    logging.info('Taking image')
    rc = cam.start_exposure(5)
    if not rc:
        logging.error('Failed to start exposure - quitting')
        sys.exit(-1)

    while True:
        done = cam.check_exposure()
        logging.info(f'check_exposure = {done}')
        if done:
            break
        time.sleep(1)

    fileloc = os.path.join(os.getcwd(), 'pyastrobackend_alpaca_ccd_tests.fits')
    #logging.info(f'saving image to {fileloc}')
    #image_data = cam.get_image_data()
    #pyfits.writeto(fileloc, image_data, overwrite=True)
    download_url = "http://127.0.0.1:11111/api/v1/camera/0/imagearray?ClientID=1&ClientTransactionID=11"

    if False:
        import requests
        import shutil
        import time
        ts=time.time()
        with requests.get(download_url, stream=True) as r:
            with open(fileloc, 'wb') as f:
                shutil.copyfileobj(r.raw, f, -1)
        te=time.time()
        logging.info(f'Download took {te-ts} seconds')
    else:
        import sys
        import json
        import pycurl
        import numpy as np
        from io import BytesIO
        mts=time.time()
        ts=time.time()
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, download_url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        te=time.time()
        logging.info(f'Download took {te-ts} seconds')

        ts=time.time()
        resp = json.loads(body)
        te=time.time()
        logging.info(f'json.loads() took {te-ts} seconds')

        # check rank and type
        ts=time.time()
        logging.debug(f'ImageArray Rank = {resp.get("Rank")} Type = {resp.get("Type")}')
        if resp.get('Rank') != 2 or resp.get('Type') != 2:
            logging.error('ImageArray returned a Rank or Type != 2!')
            sys.exit(1)

        # get data and convert to desired type
        out_dtype = np.dtype(np.uint16)

        image_data = np.array(resp.get('Value')).astype(out_dtype)

        # reshape to 2D
        roi = cam.get_frame()
        if roi is None:
            logging.error('roi is None cannot reshape image!')
            sys.exit(1)

        logging.debug(f'reshaping to numy = {roi[3]} numx = {roi[2]}')

        # remember array has Y as first axis!!
        np.reshape(image_data, (roi[3], roi[2]))

        # then transpose so X is first
        image_data = image_data.T
        te=time.time()
        logging.info(f'convert to nparray took {te-ts} seconds')

        ts=time.time()
        logging.info(f'saving image to {fileloc}')
        pyfits.writeto(fileloc, image_data, overwrite=True)
        te=time.time()
        logging.info(f'saving FITS took {te-ts} seconds')

        mte=time.time()
        logging.info(f'Entire download took {mte-mts} seconds')
