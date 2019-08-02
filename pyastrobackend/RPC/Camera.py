""" RPC Camera solution """
import sys
import json
import time
import queue
import select
import socket
import logging
import weakref

from ..BaseBackend import BaseCamera

from pyastrobackend.RPC.RPCDeviceBase import RPCDeviceThread, RPCDevice


# not sure we need to do this but leaving it as be for now
class RPCCameraThread(RPCDeviceThread):
    def __init__(self, port, user_data, *args, **kwargs):
        super().__init__(port, user_data, *args, **kwargs)

class Camera(RPCDevice, BaseCamera):
    def __init__(self, backend=None):
        super().__init__(backend)

        self.camera_has_progress = None

        # set when exposure it going on
        self.exposure_reqid = None
        self.exposure_complete = False

        self.roi = None
        self.binning = 1
        self.frame_width = None
        self.frame_height = None

        self.rpc_manager = RPCCameraThread(8800, None)
        self.rpc_manager.event_callbacks.append(self.event_callback)

    def event_callback(self, event, *args):
#        logging.debug(f'Camera event_callback: {event} {args})')
        if event == 'Connection':
            self.connected = True
        elif event == 'Response':
            req_id = args[0]
#            logging.debug(f'event_callback: req_id = {req_id} exposure_reqid = {self.exposure_reqid}')
            if req_id == self.exposure_reqid:
#                logging.debug(f'exposure reqid = {self.exposure_reqid} response recvd!')
                resp = self.rpc_manager.check_rpc_command_status(req_id)
#                logging.debug(f'resp = {resp}')
                result = resp.get('result', None)
#                logging.debug(f'result {result}')
                if result is None:
                    logging.error('exposure response has no result!')
                    sys.exit(1)
                status = result.get('complete', None)
#                logging.debug(f'status {status}')
                if status is None:
                    logging.error('exposure completion status is None!')
                    sys.exit(1)
#                logging.debug(f'setting exposure_complete to {status}')
                self.exposure_complete = status

    def get_camera_name(self):
        return 'RPC'

    def get_camera_description(self):
        return 'RPC Camera Driver'

    def get_driver_info(self):
        return 'RPC Camera Driver'

    def get_driver_version(self):
        return 'V 0.1'

    def get_state(self):
        logging.warning('RPC Camera get_state() not implemented')
        return None

    def start_exposure(self, expos):
#        logging.debug(f'RPC:Exposing image for {expos} seconds')

        paramdict = {}
        paramdict['params'] = {}
        paramdict['params']['exposure'] = expos
        paramdict['params']['binning'] = self.binning
        paramdict['params']['roi'] = self.roi
        rc = self.send_server_request('take_image', paramdict)

        if not rc:
            logging.error('RPC:start_exposure - error')
            return False

        reqid = rc

        # FIXME this is clunky
        self.exposure_reqid = reqid
        self.exposure_complete = False

        return True

    def stop_exposure(self):
        logging.warning('RPC Camera stop_exposure() not implemented')
        return None

    def check_exposure(self):
        # connect to response from RPC server in process()
        # FIXME this could break so many ways as it doesnt
        # link up to the actual id expected for method result
        return self.exposure_complete

    def supports_progress(self):
        logging.warning('RPC Camera supports_progress() not implemented')
        return False

# FIXME returns -1 to indicate progress is not available
# FIXME shold use cached value to know if progress is supported
    def get_exposure_progress(self):
        logging.warning('RPC Camera get_exposure_progress() not implemented')
        return -1

    def save_image_data(self, path, overwrite=False):
#        logging.debug(f'RPC:Saving image to {path}')

        paramdict = {}
        paramdict = {}
        paramdict['params'] = {}
        paramdict['params']['filename'] = path
        rc = self.send_server_request('save_image', paramdict)

        if not rc:
            logging.error('RPC:saveimageCamera - error')
            return False

        reqid = rc

#        logging.debug(f'save_image: reqid = {reqid}')

        resp = None
        while True:
            resp = self.rpc_manager.check_rpc_command_status(reqid)
            if resp is not None:
                break
            time.sleep(0.1)

        if resp is None:
            logging.error('RPC get_camera_settings: resp is None!')
            sys.exit(1)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC saveimageCamera status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:safe_image) - error getting settings!')
            return False

        #FIXME need to look at result code
        return True

    def get_camera_settings(self):
        rc = self.send_server_request('get_camera_info', None)

        if not rc:
            logging.error('RPC get_camera_settings: error sending json request!')
            return False

        reqid = rc

        # FIXME this shouldn't be a problem unless RPC Server dies
        # FIXME add timeout
        # block until we get answer
        resp = None
        while True:
            #logging.debug('waiting...')
            resp = self.rpc_manager.check_rpc_command_status(reqid)
            if resp is not None:
                break
            time.sleep(0.1)

        if resp is None:
            logging.error('RPC get_camera_settings: resp is None!')
            sys.exit(1)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC saveimageCamera status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:get_camera_settings() - error getting settings!')
            return False

        result = resp['result']
        if 'framesize' in result:
            w, h = result['framesize']
            self.frame_width = w
            self.frame_height = h
        if 'binning' in result:
            self.set_binning(result['binning'], result['binning'])
        if 'roi' in result:
            self.roi = result['roi']

        return True

    def get_scalar_value(self, value_method, value_key, value_type):
#        logging.debug(f'RPC Camera get_scale_value {value_method} {value_key}')
        rc = self.send_server_request(value_method, None)

        if not rc:
            logging.error(f'RPC {value_method}: error sending json request!')
            return False

        resp = self.wait_for_response(rc)

        if resp is None:
            logging.error(f'RPC {value_method}: resp is None!')
            return None
            #sys.exit(1)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC {value_method} status/resp = {status} {resp}')

        if not status:
            logging.warning(f'RPC:{value_method} - error getting settings!')
            return None

        result = resp['result']

        result_value = result.get(value_key, None)

        if not isinstance(result_value, value_type):
            logging.error(f'get_scalar_type: {value_method} {value_key}: ' + \
                          f'expected {value_type} got {result_value} type {type(result_value)}')
            return None
        else:
            return result_value

    def set_scalar_value(self, value_method, value_key, value):
#        logging.debug(f'RPC:set_scalar_value {value_method} {value_key} = {value}')

        paramdict = {}
        paramdict['params'] = {}
        paramdict['params'][value_key] = value
        rc = self.send_server_request(value_method, paramdict)

        if not rc:
            logging.error('RPC:set_scalar_value - error')
            return False

        resp = self.wait_for_response(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC set_scalar_value status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:set_scalar_value - error getting settings!')
            return False

        #FIXME need to look at result code
        return True

    def get_image_data(self):
        logging.warning('RPC Camera get_image_data() not implemented!')

    def get_pixelsize(self):
        valx = self.get_scalar_value('get_camera_x_pixelsize', 'camera_x_pixelsize', float )
        valy = self.get_scalar_value('get_camera_y_pixelsize', 'camera_y_pixelsize', float )
        return valx, valy

    def get_egain(self):
        return self.get_scalar_value('get_camera_egain','camera_egain', float )

    def get_gain(self):
        return self.get_scalar_value('get_camera_gain', 'camera_gain', float )

    def get_current_temperature(self):
        return self.get_scalar_value('get_current_temperature', 'current_temperature', float )

    def get_target_temperature(self):
        return self.get_scalar_value('get_target_temperature', 'target_temperature', float )

    def set_target_temperature(self, temp_c):
#        logging.debug(f'RPC:set_target_temperature to {temp_c}')

        self.set_scalar_value('set_target_temperature', 'target_temperature', temp_c)

    def set_cooler_state(self, onoff):
#        logging.debug(f'RPC:set_cooler_state to {onoff}')

        return self.set_scalar_value('set_cooler_state', 'cooler_state', onoff)

    def get_cooler_state(self):
        return self.get_scalar_value('get_cooler_state', 'cooler_state', bool )

    def get_cooler_power(self):
        return self.get_scalar_value('get_cooler_power', 'cooler_power', float )

    def get_binning(self):
        return (self.binning, self.binning)

    def set_binning(self, binx, biny):
        # just ignore biny
        # cache for when we are going to take an exposure
        self.binning = binx

        if not self.frame_width or not self.frame_height:
            if not self.get_camera_settings():
                logging.error('RPC:set_binning - unable to get camera settings!')
                return False

        self.roi = (0, 0, self.frame_width/self.binning, self.frame_height/self.binning)
        return True

    def get_max_binning(self):
        return self.get_scalar_value('get_max_binning', 'max_binning', int )

    def get_size(self):
        if not self.frame_width or not self.frame_height:
            if not self.get_camera_settings():
                logging.error('RPC:get_size - unable to get camera settings!')
                return None

        return (self.frame_width, self.frame_height)

    def get_frame(self):
        return self.roi

    def set_frame(self, minx, miny, width, height):
        self.roi = (minx, miny, width, height)
        return True
