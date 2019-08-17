""" Pure Alpaca solution """

import logging
import requests

from pyastrobackend.BaseBackend import BaseDeviceBackend

from pyastrobackend.Alpaca.Camera import Camera
#from pyastrobackend.ASCOM.Focuser import Focuser as ASCOM_Focuser
#from pyastrobackend.ASCOM.FilterWheel import FilterWheel
#from pyastrobackend.ASCOM.Mount import Mount

# messy but we'll roll MaximDL camera support under ASCOM
#from pyastrobackend.MaximDL.Camera import Camera as MaximDL_Camera
#from pyastrobackend.RPC.Camera import Camera as RPC_Camera
#from pyastrobackend.RPC.Focuser import Focuser as RPC_Focuser

#warnings.filterwarnings('always', category=DeprecationWarning)

class DeviceBackend(BaseDeviceBackend):

    def __init__(self, ip, port):

        self.server_ip = ip
        self.server_port = port

        self.request_id = 1

        self.api_version = 1

        self.connected = False

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
        logging.debug(f'Sending GET req {req} params {params}')
        resp = requests.get(url=req, params=params)
        logging.debug(f'Response was {resp} {repr(resp.json())[:255]}')

        if not DeviceBackend._verify_response(resp):
            return None

        if not returndict:
            return resp.json()['Value']
        else:
            return resp.json()

    def set_prop(self, device_type, device_number, prop, params={}):
        params['ClientID'] = 1
        params['ClientTransactionID'] = self.request_id
        self.request_id += 1
        req = self._base_url(device_type, device_number) + prop
        logging.debug(f'Sending POST req {req} params {params}')
        resp = requests.put(url=req, data=params)
        logging.debug(f'Response was {resp} {resp.json()}')

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
