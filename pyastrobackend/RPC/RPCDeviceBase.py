""" RPC Device solution """

import json
import time
import queue
import select
import socket
import logging
import weakref

from threading import Thread, Lock


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

    # def run(self):
        # logging.info('RPCDeviceThread Started!')

        # while True:
            # # clear out event queue
            # while True:
                # try:
                    # self.event_queue.get_nowait()
                # except queue.Empty:
                    # break

            # logging.info('Connecting to server')
            # while True:
                # try:
                    # self.rpc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # logging.info('Attempting connect')
                    # self.rpc_socket.connect(('127.0.0.1', self.port))
                    # logging.info('Success!')
                    # break
                # except ConnectionRefusedError:
                    # logging.error('Failed to connect to RPC Server')
                    # self.rpc_socket.close()

                # time.sleep(5)

            # logging.debug('Sending connect event to queue')
            # cdict = { 'Event' : 'Connected' }
            # self.event_queue.put(cdict)

            # logging.debug('Waiting on data')
            # quit = False
            # while not quit:
                # #logging.debug('A')

                # # check if time for status update request
                # # if False and self.status_request_interval > 0:
                    # # if time.time() - self.last_status_request_timestamp > self.status_request_interval:
                        # # # request status
                        # # logging.debug('Sending getstatus request')
                        # # self.queue_rpc_command('getstatus', {})
                        # # self.last_status_request_timestamp = time.time()

                # read_list = [self.rpc_socket]
                # readable, writable, errored = select.select(read_list, [], [], 0.5)
                # #logging.debug('B')

                # if len(readable) > 0:
# #                    logging.debug(f'reading data readable={readable}')

                    # with self._lock:
                        # try:
                            # j = self.read_json()
# #                            logging.debug(f'length of message = {len(j)}')
# #                            logging.debug(f'j = {j}')
                        # except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                            # logging.error('RPCClient: server reset connection!')
                            # self.server_disconnected()
                            # quit = True
                            # j = ''

                        # if len(j) == 0:
                            # logging.warning('Received select for read 0 bytes!')
                        # else:
                            # jdict = json.loads(j)
                            # event = jdict.get('Event', None)
                            # req_id = jdict.get('id', None)
                            # #logging.debug(f'{event} {req_id}')
                            # if req_id is not None:
                                # logging.debug(f'Received response {repr(jdict)[:60]}')
# #                                logging.debug('appending response to list')
                                # self.responses.append(jdict)
# #                                logging.debug(f'req_id = {req_id}')
                                # self.emit('Response', req_id)
                            # elif event is not None:
                                # logging.debug(f'Received event {event}')
                                # if event == 'Connection':
                                    # logging.debug('Recv Connection event')
                                    # self.emit(event)
                            # else:
                                # logging.warning(f'RPCClient: received JSON {jdict} with no event or id!')

                # # send any commands
                # try:
                    # rpccmd = self.command_queue.get(block=False)
                # except queue.Empty:
                    # rpccmd = None

                # if rpccmd is not None:
# #                    logging.debug(f'Recvd command from queue {rpccmd}')
                    # cmd, edict = rpccmd
                    # cdict = { 'method' : cmd }
                    # jdict = {**cdict, **edict}
                    # jmsg = str.encode(json.dumps(jdict) + '\n')
                    # logging.debug(f'Sending json rpc = {jmsg}')
                    # try:
                        # self.rpc_socket.sendall(jmsg)
                    # except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                        # logging.error(f'RPCClient: connection reset sending poll response!')
                        # self.server_disconnected()
                        # quit = True
                    # except Exception as e:
                        # logging.error(f'RPCClient: exception sending poll response!')
                        # self.server_disconnected()
                        # quit = True


            # # fell out so close socket and try to reconnect
            # logging.debug('RPCClient: Fell out of main loop closing socket')
            # try:
                # self.rpc_socket.close()
            # except:
                # logging.error(f'RPCClient: Error closing rpc_socket={self.rpc_socket}', exc_info=True)

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

    def read_json(self):
        """ read \n terminated JSON blocks """

        #self.rpc_socket.settimeout(0.5)
        ret = ''
        while True:
            #try:
            if True:
                data = self.rpc_socket.recv(4096)
                logging.debug(f'read_json(): len(data) = {len(data)} data = |{data}|')

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
            logging.debug(f'json message      -> {ret} <-')
            self.buffer = self.buffer[ json_start + json_end : ]
            logging.debug(f'final read buffer -> {self.buffer} <-')
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
#                logging.debug(f'Found response for request id {req_id}')
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
