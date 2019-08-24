import os
import sys
import re
import glob
import math
import argparse
import logging

import numpy as np

import astropy.io.fits as pyfits



def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str, help='Basename of files to analyze')
    parser.add_argument('--debug', action='store_true', help='Set log level DEBUG')

    args = parser.parse_args()
    logging.debug(f'cmd args = {args}')
    return args

if __name__ == '__main__':
    LONG_FORMAT = '%(asctime)s.%(msecs)03d [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'
    SHORT_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s'
    logging.basicConfig(filename='analyze_ptc.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format=LONG_FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S')

    # add to screen as well
    LOG = logging.getLogger()

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

    #logging.info(f'analyze_ptc starting')

    files = glob.glob(args.name + '*.fits')

    # parse out exposure
    data = {}
    s = re.compile('^.*_gain_(\d*)_(\d*\.\d*)s-(\d*).*fits$')
    for f in files:
        m = s.match(f)
        gain = int(m.group(1))
        exposure = float(m.group(2))
        idx = int(m.group(3))
        #logging.info(f'{f} {gain} {exposure} {idx}')

        if exposure in data:
            data[exposure].append(f)
        else:
            data[exposure] = [f]

    #logging.info(f'{data}')

    for e in sorted(data.keys()):

        img1 = pyfits.getdata(data[e][0])
        img2 = pyfits.getdata(data[e][1])

        med1 = np.median(img1)
        med2 = np.median(img2)
        dif = (img1+1000) - img2
        std = np.std(dif)

        sys.stdout.write(f'{e}, {med1}, {med2}, {std/(math.sqrt(2.0)/2.0)}\n')







