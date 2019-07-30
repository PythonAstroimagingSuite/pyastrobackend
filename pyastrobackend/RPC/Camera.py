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

# 0 = none, higher shows more
LOG_SERVER_TRAFFIC = 1

class RPCCameraThread(RPCDeviceThread):
    def __init__(self, port, user_data, *args, **kwargs):
        super().__init__(port, user_data, *args, **kwargs)

    def run(self):
        logging.info('RPCCameraThread Started!')

        while True:
            # clear out event queue
            while True:
                try:
                    self.event_queue.get_nowait()
                except queue.Empty:
                    break

            logging.info('Connecting to server')
            while True:
                try:
                    self.rpc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    logging.info('Attempting connect')
                    self.rpc_socket.connect(('127.0.0.1', self.port))
                    logging.info('Success!')
                    break
                except ConnectionRefusedError:
                    logging.error('Failed to connect to RPC Server')
                    self.rpc_socket.close()

                time.sleep(5)

            logging.debug('Sending connect event to queue')
            cdict = { 'Event' : 'Connected' }
            self.event_queue.put(cdict)

            logging.debug('Waiting on data')
            quit = False
            while not quit:
                #logging.debug('A')

                # check if time for status update request
                # if False and self.status_request_interval > 0:
                    # if time.time() - self.last_status_request_timestamp > self.status_request_interval:
                        # # request status
                        # logging.debug('Sending getstatus request')
                        # self.queue_rpc_command('getstatus', {})
                        # self.last_status_request_timestamp = time.time()

                read_list = [self.rpc_socket]
                readable, writable, errored = select.select(read_list, [], [], 0.5)
                #logging.debug('B')

                if len(readable) > 0:
#                    logging.debug(f'reading data readable={readable}')

                    with self._lock:
                        try:
                            j = self.read_json()
                            if LOG_SERVER_TRAFFIC > 2:
                                logging.debug(f'length of message = {len(j)}')
                                logging.debug(f'j = {j}')
                        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                            logging.error('RPCClient: server reset connection!')
                            self.server_disconnected()
                            quit = True
                            j = ''

                        if len(j) == 0:
                            logging.warning('Received select for read 0 bytes!')
                        else:
                            jdict = json.loads(j)
                            event = jdict.get('Event', None)
                            req_id = jdict.get('id', None)
                            if LOG_SERVER_TRAFFIC > 2:
                                logging.debug(f'{event} {req_id}')
                            if req_id is not None:
                                if LOG_SERVER_TRAFFIC > 0:
                                    logging.debug(f'Received response {repr(jdict)[:60]}')
                                    #logging.debug('appending response to list')
                                self.responses.append(jdict)
                                if LOG_SERVER_TRAFFIC > 2:
                                    logging.debug(f'req_id = {req_id}')
                                self.emit('Response', req_id)
                            elif event is not None:
                                if LOG_SERVER_TRAFFIC > 0:
                                    logging.debug(f'Received event {event}')
                                if event == 'Connection':
#                                    logging.debug('Recv Connection event')
                                    self.emit(event)
                            else:
                                logging.warning(f'RPCClient: received JSON {jdict} with no event or id!')

                # send any commands
                try:
                    rpccmd = self.command_queue.get(block=False)
                except queue.Empty:
                    rpccmd = None

                if rpccmd is not None:
                    if LOG_SERVER_TRAFFIC > 0:
                        logging.debug(f'Recvd command from queue {rpccmd}')
                    cmd, edict = rpccmd
                    cdict = { 'method' : cmd }
                    jdict = {**cdict, **edict}
                    jmsg = str.encode(json.dumps(jdict) + '\n')
                    if LOG_SERVER_TRAFFIC > 0:
                        logging.debug(f'Sending json rpc = {jmsg}')
                    try:
                        self.rpc_socket.sendall(jmsg)
                    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                        logging.error(f'RPCClient: connection reset sending poll response!')
                        self.server_disconnected()
                        quit = True
                    except Exception as e:
                        logging.error(f'RPCClient: exception sending poll response!')
                        self.server_disconnected()
                        quit = True


            # fell out so close socket and try to reconnect
            logging.debug('RPCClient: Fell out of main loop closing socket')
            try:
                self.rpc_socket.close()
            except:
                logging.error(f'RPCClient: Error closing rpc_socket={self.rpc_socket}', exc_info=True)


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

    def wait_for_server(self, reqid, timeout=15):
        # FIXME this shouldn't be a problem unless RPC Server dies
        # FIXME add timeout
        # block until we get answer
        resp = None
        waited = time.time()
        while (time.time() - waited) < timeout:
            #logging.debug('waiting...')
            resp = self.rpc_manager.check_rpc_command_status(reqid)
            if resp is not None:
                break
            time.sleep(0.1)

        if resp is None:
            logging.error('RPC wait for server: resp is None!')

        return resp

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

    def get_scalar_value(self, value_method, value_key):
#        logging.debug(f'RPC Camera get_scale_value {value_method} {value_key}')
        rc = self.send_server_request(value_method, None)

        if not rc:
            logging.error(f'RPC {value_method}: error sending json request!')
            return False

        resp = self.wait_for_server(rc)

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
        return result.get(value_key, None)

    def set_scalar_value(self, value_method, value_key, value):
#        logging.debug(f'RPC:set_scalar_value {value_method} {value_key} = {value}')

        paramdict = {}
        paramdict['params'] = {}
        paramdict['params'][value_key] = value
        rc = self.send_server_request(value_method, paramdict)

        if not rc:
            logging.error('RPC:set_scalar_value - error')
            return False

        resp = self.wait_for_server(rc)

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
        valx = self.get_scalar_value('get_camera_x_pixelsize', 'camera_x_pixelsize' )
        valy = self.get_scalar_value('get_camera_y_pixelsize', 'camera_y_pixelsize' )
        return valx, valy

    def get_egain(self):
        return self.get_scalar_value('get_camera_egain','camera_egain' )

    def get_egain(self):
        return self.get_scalar_value('get_camera_gain', 'camera_gain' )

    def get_current_temperature(self):
        return self.get_scalar_value('get_current_temperature', 'current_temperature' )

    def get_target_temperature(self):
        return self.get_scalar_value('get_target_temperature', 'target_temperature' )

    def set_target_temperature(self, temp_c):
#        logging.debug(f'RPC:set_target_temperature to {temp_c}')

        self.set_scalar_value('set_target_temperature', 'target_temperature', temp_c)

    def set_cooler_state(self, onoff):
#        logging.debug(f'RPC:set_cooler_state to {onoff}')

        return self.set_scalar_value('set_cooler_state', 'cooler_state', onoff)

    def get_cooler_state(self):
        return self.get_scalar_value('get_cooler_state', 'cooler_state' )

    def get_cooler_power(self):
        return self.get_scalar_value('get_cooler_power', 'cooler_power' )

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
        return get_scalar_value('get_max_binning', 'max_binning' )

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
