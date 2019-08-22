import os
import sys
import time
import logging
import astropy.io.fits as pyfits

from pyastrobackend.AlpacaBackend import DeviceBackend
from pyastrobackend.Alpaca.Camera import Camera

if __name__ == '__main__':

    logging.basicConfig(filename='alpaca_camera_base64_test.log',
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

    logging.info('alpaca_camera_base64_test Test Mode starting')

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

    if len(sys.argv) < 2:
        w, h = cam.get_size()
        cam.set_frame(0, 0, w, h)
    else:
        roi = int(sys.argv[1])
        logging.info(f'Image is {roi} x {roi} pixels')
        cam.set_frame(0, 0, roi, roi)

    logging.info('Taking image')
    rc = cam.start_exposure(1)
    if not rc:
        logging.error('Failed to start exposure - quitting')
        sys.exit(-1)

    while True:
        done = cam.check_exposure()
        logging.info(f'check_exposure = {done}')
        if done:
            break
        time.sleep(1)

    logging.info(f'ROI is {cam.get_frame()}')

    fileloc = os.path.join(os.getcwd(), 'pyastrobackend_alpaca_ccd_base64_tests.fits')

    # first grab image info
    import sys
    import ujson as json
    import pycurl
    import base64
    import numpy as np
    from io import BytesIO

    mts = time.time()

    buffer = BytesIO()
    c = pycurl.Curl()
    part1_url = "http://127.0.0.1:11111/api/v1/camera/0/imagearray?ClientID=1&ClientTransactionID=11"
    c.setopt(c.URL, part1_url)
    c.setopt(c.WRITEDATA, buffer)
#    c.setopt(c.HTTPHEADER, ['Content-Type: application/json', 'Base64Serialisation: true'])
    c.setopt(c.HTTPHEADER, [
                            'Content-Type: application/json',
                            'base64json: true'
#                            'base64handoff: true',
#                            'Accept-Encoding: gzip'
                           ])
    c.perform()
    c.close()

    body = buffer.getvalue()

#    f = open('test.dat', 'wb')
#    f.write(body)
#    f.close()

    ts = time.time()
    j = json.loads(body)
    print(len(j['Value']))

    for k, v in j.items():
        if k == 'Value':
            continue
        print(k, v)

    b64 = j['Value']
    te = time.time()
    print(f'json parsing took {te-ts} secs')


    ts=time.time()
    decoded = base64.b64decode(b64)
    read_img = np.frombuffer(decoded, dtype=np.int32)
    te=time.time()
    print(f'b64decode took {te-ts} seconds')
    print(len(read_img))
    print(type(read_img))

    # convert to int16
    out_dtype = np.dtype(np.uint16)

    image_data = read_img.astype(out_dtype)

    # reshape to 2D
    roi = cam.get_frame()
    if roi is None:
        logging.error('roi is None cannot reshape image!')
        sys.exit(1)

    logging.debug(f'image_data shape is {image_data.shape}')

    logging.debug(f'reshaping to numy = {roi[3]} numx = {roi[2]}')

    # remember array has Y as first axis!!
    #np.reshape(image_data, (roi[3], roi[2]))

    image_data = np.reshape(image_data, (roi[2], -1))

    logging.debug(f'image_data shape is {image_data.shape}')

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


    sys.exit(0)
