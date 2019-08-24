""" RPC Device solution """

import json
import time
import queue
import select
import socket
import logging

from threading import Thread, Lock

# 0 = none, higher shows more
LOG_SERVER_TRAFFIC = 1

class RPCDeviceThread(Thread):
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
        #logging.debug(f'emit: {self.event_callbacks}')
        for cb in self.event_callbacks:
            #logging.debug(f'emit: {cb} {event} {args}')
            cb(event, *args)

    def run(self):
        logging.info(f'{self.__class__.__name__} started!')

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

                # read in new data
                if len(readable) > 0:
#                    logging.debug(f'reading data readable={readable}')

                    try:
                        self.populate_buffer()
                        if LOG_SERVER_TRAFFIC > 2:
                            logging.debug('called populate_buffer()')
                            logging.debug(f'self.buffer = |{self.buffer}|')
                    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                        logging.error('RPCClient: server reset connection!')
                        self.server_disconnected()
                        quit = True
                        continue

                # process all valid JSON blocks
                while True:
                    j = self.read_next_json_block()
                    if LOG_SERVER_TRAFFIC > 2:
                        logging.debug('read_next_json_block() returned {j}')
                    if j is None:
                        break

                    # if we get garbage json string dont die
                    try:
                        jdict = json.loads(j)
                    except json.decoder.JSONDecodeError:
                        logging.error(f'Error decoding {j}!', exc_info=True)
                        break

                    event = jdict.get('Event', None)
                    req_id = jdict.get('id', None)
                    if LOG_SERVER_TRAFFIC > 2:
                        logging.debug(f'{event} {req_id}')
                    if req_id is not None:
                        if LOG_SERVER_TRAFFIC > 0:
                            logging.debug(f'Received response {repr(jdict)}')
                            #logging.debug(f'Received response {repr(jdict)[:60]}')
                            #logging.debug('appending response to list')

                        # FIXME MSF SHOULD I REMOVE FOR NORMAL OPS?
                        # don't save duplicate ids
                        already = False
                        for resp in self.responses:
                            if resp.get('id', None) == req_id:
                                already = True
                        if not already:
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
                    except Exception:
                        logging.error(f'RPCClient: exception sending poll response!', exc_info=True)
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
        logging.debug(f'sending_polling_response for event ')
        #poll_cmd = {}
        #poll_cmd['request'] = 'polling'
        #self.rpc_socket.sendall(str.encode(json.dumps(poll_cmd)+'\n'))
        self.queue_rpc_command('polling', {})

    def populate_buffer(self):
        """
        Read in any new data into buffer.
        """

        self.rpc_socket.settimeout(0.05)
        got_data = False
        while True:
            #try:
            if True:
                try:
                    data = self.rpc_socket.recv(4096)
                except socket.timeout:
                    data = b''

                logging.debug(f'populate_buffer(): len(data) = {len(data)} data = |{data}|')

                if len(data) < 1:
                    # if we've received NOTHING this pass means socket closed
                    if not got_data:
                        raise BrokenPipeError('recv returned 0 bytes - connection lost!')
                    break

                got_data = True
                data = data.decode()
                self.buffer += data
                logging.debug(f'self.buffer = |{self.buffer}|')


    def read_next_json_block(self):
        """ read \n terminated JSON blocks """


            # find first '{' and '\n' and see if in between contains a valid json block
#            logging.debug(f'after read buffer = |{self.buffer}|')
        try:
            json_start = self.buffer.index('{')
        except ValueError:
            return None

        try:
            json_end = self.buffer[json_start:].index('\n')
        except ValueError:
            return None

        #print('json start/end = ', json_start, json_start + json_end)

        ret = self.buffer[json_start : json_start + json_end]
        logging.debug(f'json message      -> {ret} <-')
        self.buffer = self.buffer[ json_start + json_end : ]
        logging.debug(f'final read buffer -> {self.buffer} <-')

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
        logging.debug(f'check_rpc_command_status: req_id = {req_id}')
        logging.debug(f'check_rpc_command_status: self.responses={self.responses}')
        for resp in self.responses:
            logging.debug(f'check_rpc_command_status: checking resp={resp}')
            if resp.get('id', None) == req_id:
                logging.debug(f'Found response for request id {req_id} = {resp}')
                self.responses.remove(resp)
                return resp

        return None


class RPCDevice:
    def __init__(self, backend=None):
        super().__init__()

        self.connected = False
        self.rpc_manager = None
        self.port = 8800

        # need to have code like this to setup the thread that talks to RPC server
        # and point to event handler
        #self.rpc_manager = RPCDeviceThread(8800, None)
        #self.rpc_manager.event_callbacks.append(self.event_callback)

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('RPC Device Backend: no show_chooser()!')
        return None

    # name is currently ignored
    def connect(self, name):
        if self.rpc_manager is not None and self.rpc_manager.is_alive():
            logging.error('RPCDevice.connect(): rpc_manager is not None! and running')
            return False

        logging.info(f'RPC Device connect: Connecting to RPCServer 127.0.0.1:{self.port}')

        logging.info('Starting RPC Device manager thread')
        self.rpc_manager.start()

        while True:
            logging.info('Waiting on connection')
            if self.connected:
                break
            time.sleep(1)

        return True

    def disconnect(self):
        self.rpc_manager.close()
        self.connected = False

    def is_connected(self):
        return self.connected

    def event_callback(self, event, *args):
        logging.debug(f'event_callback: {event} {args})')
        logging.warning('replace event_callback with custom')

    def send_server_request(self, req, paramsdict=None):
        #logging.debug(f'send_server_req: {req} {paramsdict}')
        if paramsdict is None:
            paramsdict = {}

        rc = self.rpc_manager.queue_rpc_command(req, paramsdict)
        #logging.debug(f'send_server_req: queue_rpc_command returned {rc}')
        return rc

    def wait_for_response(self, reqid, timeout=15):
        # FIXME this shouldn't be a problem unless RPC Server dies
        # FIXME add timeout
        # block until we get answer
        logging.debug(f'wait_for_response: waiting for reqid={reqid} timeout={timeout}')
        resp = None
        waited = time.time()
        while (time.time() - waited) < timeout:
            #logging.debug('waiting...')
            resp = self.rpc_manager.check_rpc_command_status(reqid)
            if resp is not None:
                logging.debug(f'wait_for_response: Found resp={resp}')
                break
            time.sleep(1)

        if resp is None:
            logging.error(f'RPC wait for serverreq_id={reqid}  TIMEOUT ->  resp is None!')
        else:
            logging.debug(f'Response for req_id={reqid} is {resp}')

        return resp


    def get_scalar_value(self, value_method, value_key, value_types):
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
            logging.error(f'RPC:{value_method} - error getting settings!')
            return None

        result = resp['result']

        result_value = result.get(value_key, None)

        match = False
        for value_type in value_types:
            match = isinstance(result_value, value_type)
            if match:
                break
        if not match:
            logging.error(f'get_scalar_type: {value_method} {value_key}: ' + \
                          f'expected one of {value_types} got {result_value} ' + \
                          f'type {type(result_value)}')
            return None
        else:
            return result_value

    def set_scalar_value(self, value_method, value_key, value):
#        logging.debug(f'RPC:set_scalar_value {value_method} {value_key} = {value}')

        paramdict = {}
        if value_key is not None:
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

    def send_command(self, command, params={}):
#        logging.debug(f'RPC:set_scalar_value {value_method} {value_key} = {value}')

        paramdict = {}
        paramdict['params'] = {}
        for k, v in params.items():
            paramdict['params'][k] = v
        rc = self.send_server_request(command, paramdict)

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


    def get_list_value(self, value_method, value_key):
        return self.get_scalar_value(value_method, value_key, (list,))
