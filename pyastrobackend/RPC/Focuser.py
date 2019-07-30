""" RPC Camera solution """

import json
import time
import queue
import select
import socket
import logging
import weakref

from ..BaseBackend import BaseFocuser

from pyastrobackend.RPC.RPCDeviceBase import RPCDeviceThread, RPCDevice

# 0 = none, higher shows more
LOG_SERVER_TRAFFIC = 1

class RPCFocuserThread(RPCDeviceThread):
    def __init__(self, port, user_data, *args, **kwargs):
        super().__init__(port, user_data, *args, **kwargs)

    def run(self):
        logging.info('RPCFocuserThread Started!')

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
#                                logging.debug('appending response to list')
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


class Focuser(RPCDevice, BaseFocuser):
    def __init__(self, backend=None):
        super().__init__(backend)

        self.rpc_manager = RPCFocuserThread(8800, None)
        self.rpc_manager.event_callbacks.append(self.event_callback)

    def event_callback(self, event, *args):
#        logging.debug(f'Focsuer event_callback: {event} {args})')
        if event == 'Connection':
            self.connected = True
        elif event == 'Response':
            req_id = args[0]
#            logging.debug(f'event_callback: req_id = {req_id}')


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

    def get_absolute_position(self):
#        logging.debug(f'RPC:get_absolute_position image')

        rc = self.send_server_request('focuser_get_absolute_position', None)

        if not rc:
            logging.error('RPC:get_absolute_position - error')
            return False

        resp = self.wait_for_server(rc)

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

        resp = self.wait_for_server(rc)

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

        resp = self.wait_for_server(rc)

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

        resp = self.wait_for_server(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC is_moving status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:is_moving() - error getting settings!')
            return False

        result = resp['result']
        is_moving = result.get('focuser_is_moving', None)
#        logging.debug(f'RPC:is_moving() returns {is_moving}')
        return is_moving

    def stop(self):
#        logging.debug(f'RPC:focuser_stop')

        rc = self.send_server_request('focuser_stop', None)

        if not rc:
            logging.error('RPC:stop - error')
            return False

        resp = self.wait_for_server(rc)

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

        resp = self.wait_for_server(rc)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC move_absolute_position status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:move_absolute_position - error getting settings!')
            return False

        #FIXME need to look at result code
        return True
