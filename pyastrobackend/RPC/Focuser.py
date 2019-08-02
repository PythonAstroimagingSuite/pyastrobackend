""" RPC Camera solution """

import json
import time
import queue
import select
import socket
import logging

from ..BaseBackend import BaseFocuser

from pyastrobackend.RPC.RPCDeviceBase import RPCDeviceThread, RPCDevice

# 0 = none, higher shows more
LOG_SERVER_TRAFFIC = 1

class RPCFocuserThread(RPCDeviceThread):
    def __init__(self, port, user_data, *args, **kwargs):
        super().__init__(port, user_data, *args, **kwargs)


class Focuser(RPCDevice, BaseFocuser):
    def __init__(self, backend=None):
        super().__init__(backend)

        self.rpc_manager = RPCFocuserThread(8800, None)
        self.rpc_manager.event_callbacks.append(self.event_callback)

    def event_callback(self, event, *args):
#        logging.debug(f'Focsuer event_callback: {event} {args})')
        if event == 'Connection':
            self.connected = True
#        elif event == 'Response':
#            req_id = args[0]
#            logging.debug(f'event_callback: req_id = {req_id}')


    def get_absolute_position(self):
#        logging.debug(f'RPC:get_absolute_position image')

        rc = self.send_server_request('focuser_get_absolute_position', None)

        if not rc:
            logging.error('RPC:get_absolute_position - error')
            return False

        resp = self.wait_for_response(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC get_absolute_position status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:get_absolute_position() - error getting settings!')
            return False

        result = resp['result']
        abs_pos = result.get('absolute_position', None)
#        logging.debug(f'RPC:get_absolute_position() returns {abs_pos}')
        return abs_pos

    def get_max_absolute_position(self):
#        logging.debug(f'RPC:get_max_absolute_position image')

        rc = self.send_server_request('focuser_get_max_absolute_position', None)

        if not rc:
            logging.error('RPC:get_max_absolute_position - error')
            return False

        resp = self.wait_for_response(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.info(f'RPC get_max_absolute_position status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:get_max_absolute_position() - error getting settings!')
            return False

        result = resp['result']
        max_abs_pos = result.get('max_absolute_position', None)
#        logging.debug(f'RPC:get_max_absolute_position() returns {max_abs_pos}')
        return max_abs_pos

    def get_current_temperature(self):
#        logging.debug(f'RPC:get_current_temperature image')

        rc = self.send_server_request('focuser_get_current_temperature', None)

        if not rc:
            logging.error('RPC:get_current_temperature - error')
            return False

        resp = self.wait_for_response(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC get_current_temperature status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:get_current_temperature() - error getting settings!')
            return False

        result = resp['result']
        cur_temp = result.get('current_temperature', None)
#        logging.debug(f'RPC:get_current_temperature() returns {cur_temp}')
        return cur_temp

    def is_moving(self):
#        logging.debug(f'RPC:is_moving image')

        rc = self.send_server_request('focuser_is_moving', None)

        if not rc:
            logging.error('RPC:is_moving - error')
            return False

        resp = self.wait_for_response(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC is_moving status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:is_moving() - error getting settings!')
            return False

        result = resp['result']
        is_moving = result.get('is_moving', None)
#        logging.debug(f'RPC:is_moving() returns {is_moving}')
        return is_moving

    def stop(self):
#        logging.debug(f'RPC:focuser_stop')

        rc = self.send_server_request('focuser_stop', None)

        if not rc:
            logging.error('RPC:stop - error')
            return False

        resp = self.wait_for_response(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC focuser_stop status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:focuser_stop - error getting settings!')
            return False

        #FIXME need to look at result code
        return True

    def move_absolute_position(self, abspos):
#        logging.debug(f'RPC:move_absolute_position to {abspos} ')

        paramdict = {}
        paramdict['params'] = {}
        paramdict['params']['absolute_position'] = abspos
        rc = self.send_server_request('focuser_move_absolute_position', paramdict)

        if not rc:
            logging.error('RPC:move_absolute_position - error')
            return False

        resp = self.wait_for_response(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC move_absolute_position status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:move_absolute_position - error getting settings!')
            return False

        #FIXME need to look at result code
        return True
