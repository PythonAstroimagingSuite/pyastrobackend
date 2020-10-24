""" RPC Camera solution """
import sys
import time
import logging

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
        self.exposure_success = False

        self.roi = None
        self.binning = 1
        self.frame_width = None
        self.frame_height = None
        self.camera_gain = None

        self.rpc_manager = RPCCameraThread(8800, None)
        self.rpc_manager.event_callbacks.append(self.event_callback)

    def event_callback(self, event, *args):
        #logging.debug(f'Camera event_callback: {event} {args})')
        if event == 'Connection':
            self.connected = True
        elif event == 'Response':
            req_id = args[0]
            #logging.debug(f'event_callback: req_id = {req_id} exposure_reqid = {self.exposure_reqid}')
            if req_id == self.exposure_reqid:
                #logging.debug(f'exposure reqid = {self.exposure_reqid} response recvd!')
                resp = self.rpc_manager.check_rpc_command_status(req_id)
                #logging.debug(f'resp = {resp}')
                result = resp.get('result', None)
                error = resp.get('error', None)
                logging.debug(f'result {result} error {error}')

                if result is not None:
                    status = result.get('complete', None)
                    #logging.debug(f'status {status}')
                    if status is None:
                        logging.error('exposure completion status is None!')
                        logging.error('EXITTING')
                        sys.exit(1)
                        #logging.debug(f'setting exposure_complete to {status}')
                    self.exposure_complete = status
                    self.exposure_success = True
                elif error is not None:
                    logging.error(f'Error during exposure req_id = {req_id}!')
                    self.exposure_complete = True
                    self.exposure_success = False
                else:
                    logging.error('exposure response has no result or error!')
                    logging.error('EXITTING!!!!')
                    sys.exit(1)

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
        #logging.debug(f'RPC:Exposing image for {expos} seconds')

        paramdict = {}
        paramdict['params'] = {}
        paramdict['params']['exposure'] = expos
        paramdict['params']['binning'] = self.binning
        paramdict['params']['roi'] = self.roi

        logging.warning('!!!!!!RPC CAMERA start_exposure HAS '
                        'GAIN COMMENTED OUT!!!!!!')

        #if self.camera_gain is not None:
        #    paramdict['params']['camera_gain'] = self.camera_gain

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
        #logging.warning('RPC Camera stop_exposure() not implemented')
        #return None
        params = {}
        return self.send_command('abort_image', params)

    def check_exposure(self):
        # connect to response from RPC server in process()
        # FIXME this could break so many ways as it doesnt
        # link up to the actual id expected for method result
        return self.exposure_complete

    def check_exposure_success(self):
        # return True if exposure successful
        # only valid if check_exposure() returns True
        return self.exposure_success

    def supports_progress(self):
        logging.warning('RPC Camera supports_progress() not implemented')
        return False

# FIXME returns -1 to indicate progress is not available
# FIXME shold use cached value to know if progress is supported
    def get_exposure_progress(self):
        logging.warning('RPC Camera get_exposure_progress() not implemented')
        return -1

    def supports_saveimage(self):
        return True

    def save_image_data(self, path, overwrite=False):
        #logging.debug(f'RPC:Saving image to {path}')

        params = {'filename': path,
                  'overwrite': overwrite}
        return self.send_command('save_image', params)

    def get_settings(self):
        rc = self.send_server_request('get_camera_info', None)

        if not rc:
            logging.error('RPC get_settings: error sending json request!')
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
            logging.error('RPC get_settings: resp is None!')
            sys.exit(1)

        # FIXME parse out status?
        status = 'result' in resp

        #logging.debug(f'RPC saveimageCamera status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:get_settings() - error getting settings!')
            return None

        result = resp['result']
        if 'framesize' in result:
            w, h = result['framesize']
            self.frame_width = w
            self.frame_height = h
        if 'binning' in result:
            self.set_binning(*result['binning'])
        if 'roi' in result:
            self.roi = result['roi']
        if 'camera_gain' in result:
            gain = result['camera_gain']
            if gain is not None:
                self.camera_gain = gain

        return result

    def get_image_data(self):
        logging.warning('RPC Camera get_image_data() not implemented!')

    def get_pixelsize(self):
        valx = self.get_scalar_value('get_camera_x_pixelsize',
                                     'camera_x_pixelsize', (float, ))
        valy = self.get_scalar_value('get_camera_y_pixelsize',
                                     'camera_y_pixelsize', (float, ))
        return valx, valy

    def get_egain(self):
        return self.get_scalar_value('get_camera_egain', 'camera_egain', (float, ))

    def get_camera_gain(self):
        gain = self.get_scalar_value('get_camera_gain', 'camera_gain', (int, float))
        if gain is not None:
            self.camera_gain = gain
            return gain
        return None

    def set_camera_gain(self, gain):
        logging.warning('!!!!!!!! RPC set_camera_gain DISABLED for now until !!!!!!!!!')
        logging.warning('!!!!!!!! discrepancy between dialog gain and API gain !!!!!!!!!')
        logging.warning('!!!!!!!! better understood.                           !!!!!!!!!')
        self.camera_gain = None
        return

        # OLD CODE implementing gain change
        # logging.debug(f'Setting camera_gain to {gain}')
        # rc = self.set_scalar_value('set_camera_gain', 'camera_gain', gain)
        # if rc:
        #     self.camera_gain = gain

        # return rc

    def get_current_temperature(self):
        return self.get_scalar_value('get_current_temperature',
                                     'current_temperature', (float, ))

    def get_target_temperature(self):
        return self.get_scalar_value('get_target_temperature',
                                     'target_temperature', (float, ))

    def set_target_temperature(self, temp_c):
        #logging.debug(f'RPC:set_target_temperature to {temp_c}')

        return self.set_scalar_value('set_target_temperature',
                                     'target_temperature', temp_c)

    def set_cooler_state(self, onoff):
        #logging.debug(f'RPC:set_cooler_state to {onoff}')

        return self.set_scalar_value('set_cooler_state', 'cooler_state', onoff)

    def get_cooler_state(self):
        return self.get_scalar_value('get_cooler_state', 'cooler_state', (bool, ))

    def get_cooler_power(self):
        return self.get_scalar_value('get_cooler_power', 'cooler_power', (float, ))

    def get_binning(self):
        return (self.binning, self.binning)

    def set_binning(self, binx, biny):
        # just ignore biny
        # cache for when we are going to take an exposure
        self.binning = binx

        if not self.frame_width or not self.frame_height:
            if self.get_settings() is None:
                logging.error('RPC:set_binning - unable to get camera settings!')
                return False

        self.roi = (0, 0,
                    self.frame_width / self.binning,
                    self.frame_height / self.binning)

        #logging.debug(f'rpc camera set_binning: bin = {self.binning} roi = {self.roi}')

        return True

    def get_max_binning(self):
        return self.get_scalar_value('get_max_binning', 'max_binning', (int, ))

    def get_size(self):
        if not self.frame_width or not self.frame_height:
            if self.get_settings() is None:
                logging.error('RPC:get_size - unable to get camera settings!')
                return None

        return (self.frame_width, self.frame_height)

    def get_frame(self):
        return self.roi

    def set_frame(self, minx, miny, width, height):
        self.roi = (minx, miny, width, height)
        return True
