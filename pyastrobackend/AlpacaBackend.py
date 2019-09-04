""" Pure Alpaca solution """

import json
import logging
import requests

# for base64/imagearray big transfers
import pycurl
from io import BytesIO

from pyastrobackend.BaseBackend import BaseDeviceBackend

from pyastrobackend.Alpaca.Camera import Camera
from pyastrobackend.Alpaca.Focuser import Focuser
from pyastrobackend.Alpaca.FilterWheel import FilterWheel
from pyastrobackend.Alpaca.Mount import Mount

class DeviceBackend(BaseDeviceBackend):

    def __init__(self, ip='127.0.0.1', port=11111):

        self.server_ip = ip
        self.server_port = port

        self.request_id = 1

        self.api_version = 1

        self.connected = False

    def name(self):
        return 'ALPACA'

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False
        return True

    def isConnected(self):
        return self.connected

    def newCamera(self):
        return Camera(self)

    def newFocuser(self):
        return Focuser(self)

    def newFilterWheel(self):
        return FilterWheel(self)

    def newMount(self):
        return Mount(self)

    def getDevicesByClass(self, device_class):
        # for now just return "0" to "3" for the device number on remote server
        # class should be 'camera', 'focuser', 'filterwheel', or 'telescope'
        # CASE MATTERS
        if device_class not in ['camera', 'ccd', 'focuser', 'filterwheel', 'mount', 'telescope']:
            logging.error(f'Alpaca getDevicesbyClass: device_class {device_class} ' + \
                          f'not "camera", "ccd", "focuser", "filterwheel", "mount" or "telescope"')
            return []

        # accept either 'ccd' or 'camera' for camera class
        # but alpaca wants 'camera'
        if device_class == 'ccd':
            device_class = 'camera'
        elif device_class == 'mount':
            device_class = 'telescope'

        vals = []
        for d in ["0", "1", "2", "3"]:
            vals.append(f'ALPACA:{device_class}:{d}')
        return vals

    def _base_url(self, device_type, device_number):
        return f'http://{self.server_ip}:{self.server_port}/' + \
               f'api/v{self.api_version}/' + \
               f'{device_type}/{device_number}/'

    # FIXME Do I really want to make this a static method?
    @staticmethod
    def _verify_response(resp):

        # test if request successful
        if resp.status_code != 200:
            logging.error('get_prop failed!')
            return False

        # check for successful API call
        resp_dict = resp.json()
        error_num = resp_dict.get('ErrorNumber', None)
        if error_num is None:
            logging.error('No error number returned for get_prop request!')
            return False

        if error_num != 0:
            error_msg = resp_dict.get('ErrorMessage', 'Unknown')
            logging.error(f'get_prop request returned error number {error_num} ' + \
                          f'error message "{error_msg}"')
            return False

        if 'Value' not in resp_dict:
            logging.error('get_prop request response had no Value!')
            return False

        return True

    def get_prop(self, device_type, device_number, prop, params={}, returndict=False):
        params['ClientID'] = 1
        params['ClientTransactionID'] = self.request_id
        self.request_id += 1
        req = self._base_url(device_type, device_number) + prop
#        logging.debug(f'Sending GET req {req} params {params}')
        resp = requests.get(url=req, params=params)
        try:
            resp_json = resp.json()
        except json.decoder.JSONDecodeError:
            logging.error('resp json parse error!')
            logging.debug(f'Sent GET req {req} params {params}')
            logging.debug(f'Response was {resp}')
            return None

#        logging.debug(f'Response was {resp}')
#        logging.debug(f'Response JSON = {repr(resp_json)[:200]}')

        if not DeviceBackend._verify_response(resp):
            return None

        if not returndict:
            return resp_json['Value']
        else:
            return resp_json

    def set_prop(self, device_type, device_number, prop, params={}):
        params['ClientID'] = 1
        params['ClientTransactionID'] = self.request_id
        self.request_id += 1
        req = self._base_url(device_type, device_number) + prop
        logging.debug(f'Sending POST req {req} params {params}')
        resp = requests.put(url=req, data=params)
        #logging.debug(f'Response was {resp} {resp.json()}')

        # test if request successful
        if resp.status_code != 200:
            logging.error('set_prop failed!')
            return False

        # check for successful API call
        resp_dict = resp.json()
        error_num = resp_dict.get('ErrorNumber', None)
        if error_num is None:
            logging.error('No error number returned for set_prop request!')
            return False

        if error_num != 0:
            error_msg = resp_dict.get('ErrorMessage', 'Unknown')
            logging.error(f'set_prop request returned error number {error_num} ' + \
                          f'error message "{error_msg}"')
            return False

        return True

    def get_base64(self, device_type, device_number, prop):
        buffer = BytesIO()
        c = pycurl.Curl()
        req = self._base_url(device_type, device_number) + prop
        ctype = 'Content-Type: image/tiff'
        #logging.debug(f'get_base64: req = {req}')
        #logging.debug('Using {ctype} for http header')
        c.setopt(c.URL, req)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [ctype])
        c.perform()
        c.close()

        body = buffer.getvalue()
        return body

    def get_request(self, device_type, device_number, prop, extraparams={},
                    extraheaders={}):
        params = {}
        params['ClientID'] = 1
        params['ClientTransactionID'] = self.request_id
        params = {**params, **extraparams}
        self.request_id += 1
        req = self._base_url(device_type, device_number) + prop
        #logging.debug(f'Sending GET req {req} params {params}')
        resp = requests.get(url=req, params=params, headers=extraheaders)
        try:
            resp_json = resp.json()
        except json.decoder.JSONDecodeError:
            logging.error('resp json parse error!')
            return None

        #logging.debug(f'Response was {resp}')
        #logging.debug(f'Response JSON = {repr(resp_json)[:200]}')

        return resp_json
