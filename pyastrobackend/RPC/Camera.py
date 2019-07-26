""" RPC Camera solution """

import json
import time
import queue
import select
import socket
import logging
import weakref

#from PyQt5 import QtNetwork

# FIXME YUCK needed to process Qt event loop while blocking on
# response from server for certain RPC methods!
#from PyQt5 import QtWidgets

from ..BaseBackend import BaseCamera

from threading import Thread, Lock


class RPCCameraThread(Thread):
    def __init__(self, port, user_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = port
        self.user_data = user_data

        # this make the thread die when sys.exit() called
        self.daemon = True
        self.initialize()

    def initialize(self):
        self.daemon = True
        self.socket = None
        self.buffer = ''

        self.rpc_request_id = 0

        self._lock = Lock()
        self.command_queue = queue.Queue()
        self.event_queue = queue.Queue()
        self.responses = []
        
        # FIXME need weakrefs?  
        self.event_callbacks = []

    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.initialize()

    def emit(self, event, *args):
        logging.debug(f'emit: {self.event_callbacks}')
        for cb in self.event_callbacks:
            logging.debug(f'emit: {cb} {event} {args}')
            cb(event, *args)
            
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

            logging.info('Waiting on data')
            quit = False
            while not quit:
                #logging.info('A')

                # check if time for status update request
                # if False and self.status_request_interval > 0:
                    # if time.time() - self.last_status_request_timestamp > self.status_request_interval:
                        # # request status
                        # logging.debug('Sending getstatus request')
                        # self.queue_rpc_command('getstatus', {})
                        # self.last_status_request_timestamp = time.time()

                read_list = [self.rpc_socket]
                readable, writable, errored = select.select(read_list, [], [], 0.5)
                #logging.info('B')

                if len(readable) > 0:
                    logging.info(f'reading data readable={readable}')

                    with self._lock:
                        try:
                            j = self.read_json()
                            logging.info(f'length of message = {len(j)}')
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
                            #logging.info(f'{event} {req_id}')
                            if req_id is not None:
                                logging.debug(f'Received response {repr(jdict)[:60]}')
                                logging.debug('appending response to list')
                                self.responses.append(jdict)
                                logging.debug(f'req_id = {req_id}')
                                self.emit('Response', req_id)
                            elif event is not None:
                                logging.debug(f'Received event {event}')
                                if event == 'Connection':
                                    logging.debug('Recv Connection event')
                                    self.emit(event)
                            else:
                                logging.warning(f'RPCClient: received JSON {jdict} with no event or id!')

                # send any commands
                try:
                    rpccmd = self.command_queue.get(block=False)
                except queue.Empty:
                    rpccmd = None

                if rpccmd is not None:
                    logging.debug(f'Recvd command from queue {rpccmd}')
                    cmd, edict = rpccmd
                    cdict = { 'method' : cmd }
                    jdict = {**cdict, **edict}
                    jmsg = str.encode(json.dumps(jdict) + '\n')
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

    def server_disconnected(self):
        logging.error('RPCClient: server disconnection!')
        self.rpc_socket.close()
        self.buffer = ''
        self.latest_status = ''
        self.latest_status_timestamp = 0
        cdict = { 'Event' : 'Disconnected' }
        self.event_queue.put(cdict)

    # given a received json for an event send a polling response to reset timer
    def send_polling_response(self):
        logging.info(f'sending_polling_response for event ')
        #poll_cmd = {}
        #poll_cmd['request'] = 'polling'
        #self.rpc_socket.sendall(str.encode(json.dumps(poll_cmd)+'\n'))
        self.queue_rpc_command('polling', {})

    def read_json(self):
        """ read \n terminated JSON blocks """

        #self.rpc_socket.settimeout(0.5)
        ret = ''
        while True:
            #try:
            if True:
                data = self.rpc_socket.recv(4096)
#                logging.debug(f'read_json(): len(data) = {len(data)} data = |{data}|')

                if len(data) < 1:
                    logging.warning('socket ran dry')

                    # if we've received NOTHING this pass means socket closed
                    if ret == '':
                        raise BrokenPipeError('recv returned 0 bytes - connection lost!')

                    break

                data = data.decode()
                self.buffer += data
                #print('self.buffer = |', self.buffer, '|')

            # find first '{' and '\n' and see if in between contains a valid json block
#            logging.debug(f'after read buffer = |{self.buffer}|')
            try:
                json_start = self.buffer.index('{')
            except ValueError:
                continue

            try:
                json_end = self.buffer[json_start:].index('\n')
            except ValueError:
                continue

            #print('json start/end = ', json_start, json_start + json_end)

            ret = self.buffer[json_start : json_start + json_end]
            #print('json message      ->', ret, '<-')
            self.buffer = self.buffer[ json_start + json_end : ]
            #print('final read buffer ->', self.buffer, '<-')
            break

        return ret

    def get_latest_status(self):
        with self._lock:
            ret = self.latest_status, self.latest_status_timestamp

        #print('-----------------------\n', ret)
        return ret

    def queue_rpc_command(self, cmd, argsdict):
        """
        Accept rpc command and dictionary of arguments and creates the json
        request dictionary and submits to command queue for rpc client thread.
        """

        #FIXME This works for our simple case but seems unclear if 'OK'
        self.rpc_request_id += 1
        jdict = { 'id' : self.rpc_request_id, **argsdict}
        self.command_queue.put((cmd, jdict))

        return self.rpc_request_id

    def check_rpc_command_status(self, req_id):
        """
        See if response available for request id req_id and returns it.
        Removes from list of requests.
        """

        for resp in self.responses:
            if resp.get('id', None) == req_id:
                logging.debug(f'Found response for request id {req_id}')
                self.responses.remove(resp)
                return resp

        return None





class Camera(BaseCamera):
    def __init__(self, backend=None):
        self.camera_has_progress = None
        self.connected = False
        self.rpc_camera_manager = None
        self.port = 8800

        # set when exposure it going on
        self.exposure_reqid = None
        self.exposure_complete = False
        
        self.roi = None
        self.binning = 1
        self.frame_width = None
        self.frame_height = None

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('RPC Camera Backend: no show_chooser()!')
        return None

    # name is currently ignored
    def connect(self, name):
        if self.rpc_camera_manager is not None:
            logging.error('RPCCamera.connect(): rpc_camera_manager is not None!')
            return False
    
        logging.info(f'RPC Camera connect: Connecting to RPCServer 127.0.0.1:{self.port}')

        self.rpc_camera_manager = RPCCameraThread(8800, None)
        self.rpc_camera_manager.event_callbacks.append(self.event_callback)
        self.rpc_camera_manager.start()
       
        # FIXME this should do something to confirm a connection!

        while True:
            logging.info('Waiting on connection')
            if self.connected:
                break
            time.sleep(1)
        
        #logging.info('Connected to RPCServer')
        
        #self.connected = True

        return True

    def disconnect(self):
        self.rpc_camera_manager.close()
        self.connected = False

    def is_connected(self):
        return self.connected

    def event_callback(self, event, *args):
        logging.debug(f'event_callback: {event} {args})')
        if event == 'Connection':
            self.connected = True
        elif event == 'Response':
            req_id = args[0]
            logging.debug(f'event_callback: req_id = {req_id} exposure_reqid = {self.exposure_reqid}')
            if req_id == self.exposure_reqid:
                logging.debug(f'exposure reqid = {self.exposure_reqid} response recvd!')
                resp = self.rpc_camera_manager.check_rpc_command_status(req_id)
                logging.debug(f'resp = {resp}')
                result = resp.get('result', None)
                logging.debug(f'result {result}')
                if result is None:
                    logging.error('exposure response has no result!')
                    sys.exit(1)
                status = result.get('complete', None)    
                logging.debug(f'status {status}')
                if status is None:
                    logging.error('exposure completion status is None!')
                    sys.exit(1)
                logging.debug(f'setting exposure_complete to {status}')
                self.exposure_complete = status
        
    # def process(self):
        # if not self.socket:
            # logging.error('server not connected!')
            # return False

            
            
            
            
            
            
        # logging.info(f'process(): {self.socket}')

        # while True:
            # resp = self.socket.readLine(2048)

            # if len(resp) < 1:
                # break

            # logging.info(f'server sent {resp}')

            # try:
                # j = json.loads(resp)

            # except Exception as e:
                # logging.error(f'RPCServer_client_test - exception message was {resp}!')
                # logging.error('Exception ->', exc_info=True)
                # continue

            # logging.info(f'json = {j}')

            # if 'Event' in j:
                # if j['Event'] == 'Connection':
                    # servid = None
                    # vers = None
                    # if 'Server' in j:
                        # servid = j['Server']
                    # if 'Version' in j:
                        # vers = j['Version']
                    # logging.info(f'Server ack on connection: Server={servid} Version={vers}')
                # elif j['Event'] == 'Ping':
                    # logging.info('Server ping received')
            # elif 'jsonrpc' in j:
                # if 'result' in j:
                    # reqid = j['id']
                    # result = j['result']
                    # logging.info(f'result of request {reqid} was {result} {type(result)}')
                    # if reqid == self.outstanding_reqid:
                        # FIXME need better way to communicate result!
                        # self.outstanding_complete = True
                        # self.outstanding_result_status = True
                        # self.outstanding_result_value = result
                # elif 'error' in j:
                    # reqid =j['id']

                    # FIXME not sure how this should be handled!
                    # if reqid == self.outstanding_reqid:
                        # FIXME need better way to communicate result!
                        # self.outstanding_complete = True
                        # self.outstanding_result_status = False
                        # self.outstanding_result_value = None
        # return

    # def send_server_request(self, req, paramsdict=None):
        # reqdict = {}
        # reqdict['method'] = req

        # if paramsdict is not None:
            # reqdict['params'] = paramsdict

        # return self.__send_json_message(reqdict)

    # def __send_json_message(self, cmd):
        # # don't use 0 for an id since we return id as success code
# #        if self.json_id == 0:
# #            self.json_id = 1
        # cmd['id'] = self.json_id
        # self.json_id += 1

        # cmdstr = json.dumps(cmd) + '\n'
        # logging.info(f'__send_json_message->{bytes(cmdstr, encoding="ascii")}')

        # try:
            # self.socket.writeData(bytes(cmdstr, encoding='ascii'))
        # except Exception as e:
            # logging.error(f'__send_json_message - cmd was {cmd}!')
            # logging.error('Exception ->', exc_info=True)
            # return False

        # logging.info('Wrote json message')    
            
        # return (True, cmd['id'])
        
    def send_server_request(self, req, paramsdict=None):
        logging.debug(f'send_server_req: {req} {paramsdict}')
        if paramsdict is None:
            paramsdict = {}

        rc = self.rpc_camera_manager.queue_rpc_command(req, paramsdict)
        logging.debug(f'send_server_req: queue_rpc_command returned {rc}')
        return rc
        
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
        logging.info(f'RPC:Exposing image for {expos} seconds')

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
        logging.info(f'RPC:Saving image to {path}')

        paramdict = {}
        paramdict = {}
        paramdict['params'] = {}
        paramdict['params']['filename'] = path
        rc = self.send_server_request('save_image', paramdict)

        if not rc:
            logging.error('RPC:saveimageCamera - error')
            return False

        reqid = rc

        logging.debug(f'save_image: reqid = {reqid}')
        
        resp = None
        while True:
            resp = self.rpc_camera_manager.check_rpc_command_status(reqid)
            if resp is not None:
                break
            time.sleep(0.1)

        if resp is None:
            logging.error('RPC get_camera_settings: resp is None!')
            sys.exit(1)

        # FIXME parse out status?
        status = 'result' in resp
            
        logging.info(f'RPC saveimageCamera status/resp = {status} {resp}')

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
            resp = self.rpc_camera_manager.check_rpc_command_status(reqid)
            if resp is not None:
                break
            time.sleep(0.1)

        if resp is None:
            logging.error('RPC get_camera_settings: resp is None!')
            sys.exit(1)

        # FIXME parse out status?
        status = 'result' in resp
            
        logging.info(f'RPC saveimageCamera status/resp = {status} {resp}')

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

    def get_image_data(self):
        logging.warning('RPC Camera get_image_data() not implemented!')

    def get_pixelsize(self):
        logging.warning('RPC Camera get_pixelsize() not implemented!')

    def get_egain(self):
        logging.warning('RPC Camera get_egain() not implemented!')

    def get_current_temperature(self):
        logging.warning('RPC Camera get_current_temperature() not implemented!')

    def get_target_temperature(self):
        logging.warning('RPC Camera get_target_temperature() not implemented!')

    def set_target_temperature(self, temp_c):
        logging.warning('RPC Camera set_target_temperature() not implemented!')

    def set_cooler_state(self, onoff):
        logging.warning('RPC Camera set_cooler_state() not implemented!')

    def get_cooler_state(self):
        logging.warning('RPC Camera get_cooler_state() not implemented!')

    def get_cooler_power(self):
        logging.warning('RPC Camera get_cooler_power() not implemented!')

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
        logging.warning('RPC Camera get_max_binning() not implemented!')

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
