# send lots of garbage requests to server


import os
import sys
import json
import time
import logging
import socket
import secrets
import string

REQ_ID = 0

get_methods = [
                'get_camera_info',
                'get_current_temperature',
                'get_target_temperature',
                'get_cooler_state',
                'get_cooler_power',
                'get_camera_x_pixelsize',
                'get_camera_y_pixelsize',
                'get_camera_max_binning',
                'get_camera_egain',
                'get_camera_gain',
                'focuser_get_absolute_position',
                'focuser_get_max_absolute_position',
                'focuser_get_current_temperature',
                'focuser_is_moving',
                'focuser_stop'
        ]

set_methods = [
                ('set_cooler_state', { 'cooler_state' : bool }),
                ('set_target_temperature', { 'target_temperature' : float}),
                ('take_image', { 'exposure' : float, 'binning' : int, 'roi': tuple}),
                ('save_image', { 'filename' : str }),
                ('focuser_move_absolute_position', {'absolute_position' : int})
              ]

def random_string(maxlen):
    return ''.join(secrets.choice(string.printable) for _ in range(secrets.randbelow(maxlen-1)+1))

def submit_garbage_request(rpc_socket):
    cmd_key = random_string(16)
    cmd_value = random_string(16)
    id_value = random_string(16)
    cdict = { cmd_key : cmd_value, 'id' : id_value}
    cmd_dict = {}
    for i in range(0, secrets.randbelow(4)):
        cmd_dict[random_string(12)] = random_string(32)
    jdict = {**cdict, **cmd_dict}
    jmsg = str.encode(json.dumps(jdict) + '\n')
    logging.debug(f'Sending json rpc = {jmsg}')
    try:
        rpc_socket.sendall(jmsg)
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        logging.error(f'RPCClient: connection reset sending poll response!')
        sys.exit(1)
    except Exception:
        logging.error(f'RPCClient: exception sending poll response!', exc_info=True)
        sys.exit(1)

def submit_corrupted_request(rpc_socket):
    cmd_value = random_string(16)
    id_value = random_string(16)
    cdict = { 'method' : cmd_value, 'id' : id_value}
    cmd_dict = {}
    for i in range(0, secrets.randbelow(4)):
        cmd_dict[random_string(12)] = random_string(32)
    jdict = {**cdict, **cmd_dict}
    jmsg = str.encode(json.dumps(jdict) + '\n')
    logging.debug(f'Sending json rpc = {jmsg}')
    try:
        rpc_socket.sendall(jmsg)
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        logging.error(f'RPCClient: connection reset sending poll response!')
        sys.exit(1)
    except Exception:
        logging.error(f'RPCClient: exception sending poll response!', exc_info=True)
        sys.exit(1)

def submit_corrupted_get_request(rpc_socket):
    global REQ_ID
    cmd_value = secrets.choice(get_methods)
    #id_value = random_string(16)
    REQ_ID += 1
    cdict = { 'method' : cmd_value, 'id' : REQ_ID}
    cmd_dict = {}
    for i in range(0, secrets.randbelow(4)):
        cmd_dict[random_string(12)] = random_string(32)
    jdict = {**cdict, **cmd_dict}
    jmsg = str.encode(json.dumps(jdict) + '\n')
    logging.debug(f'Sending json rpc = {jmsg}')
    try:
        rpc_socket.sendall(jmsg)
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        logging.error(f'RPCClient: connection reset sending poll response!')
        sys.exit(1)
    except Exception:
        logging.error(f'RPCClient: exception sending poll response!', exc_info=True)
        sys.exit(1)

def submit_corrupted_set_request(rpc_socket):
    global REQ_ID
    cmd_value, cmd_params = secrets.choice(set_methods)
    #id_value = random_string(16)
    REQ_ID += 1
    cdict = { 'method' : cmd_value, 'id' : REQ_ID}
    cmd_dict = {}
    for i in range(0, secrets.randbelow(4)):
        cmd_dict[random_string(12)] = random_string(32)
    jdict = {**cdict, **cmd_dict}
    jmsg = str.encode(json.dumps(jdict) + '\n')
    logging.debug(f'Sending json rpc = {jmsg}')
    try:
        rpc_socket.sendall(jmsg)
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        logging.error(f'RPCClient: connection reset sending poll response!')
        sys.exit(1)
    except Exception:
        logging.error(f'RPCClient: exception sending poll response!', exc_info=True)
        sys.exit(1)

def submit_wrong_types_set_request(rpc_socket):
    global REQ_ID
    cmd_value, cmd_params = secrets.choice(set_methods)
    #id_value = random_string(16)
    REQ_ID += 1
    cdict = { 'method' : cmd_value, 'id' : REQ_ID}
#    cmd_dict = {}
#    for i in range(0, secrets.randbelow(4)):
#        cmd_dict[random_string(12)] = random_string(32)
    cmd_dict = {}
    #logging.info(f'{cmd_value} {cmd_params}')
    for k, t in cmd_params.items():
        v_type = secrets.choice([int, float, bool, str])
        if v_type is int:
            v_val = secrets.randbelow(32768)-65535
        elif v_type is float:
            v_val = float(secrets.randbelow(32768)-65535)
        elif v_type is bool:
            v_val = secrets.choice([True, False])
        elif v_type is str:
            v_val = random_string(16)
        cmd_dict[k] = v_val
    jdict = {**cdict}
    jdict['params'] = cmd_dict
    jmsg = str.encode(json.dumps(jdict) + '\n')
    logging.debug(f'Sending json rpc = {jmsg}')
    try:
        rpc_socket.sendall(jmsg)
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        logging.error(f'RPCClient: connection reset sending poll response!')
        sys.exit(1)
    except Exception:
        logging.error(f'RPCClient: exception sending poll response!', exc_info=True)
        sys.exit(1)

def submit_cmd_request(rpc_socket, cmd, cmd_dict):
    global REQ_ID
    REQ_ID += 1
    cdict = { 'method' : cmd, 'id' : REQ_ID}
    jdict = {**cdict, **cmd_dict}
    jmsg = str.encode(json.dumps(jdict) + '\n')
    logging.debug(f'Sending json rpc = {jmsg}')
    try:
        rpc_socket.sendall(jmsg)
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        logging.error(f'RPCClient: connection reset sending poll response!')
        sys.exit(1)
    except Exception:
        logging.error(f'RPCClient: exception sending poll response!', exc_info=True)
        sys.exit(1)



if __name__ == '__main__':

    FORMAT = '%(asctime)s [%(filename)20s:%(lineno)3s - %(funcName)20s() ] %(levelname)-8s %(message)s'

    logging.basicConfig(level=logging.DEBUG,
                        format=FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S')

    rpc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port = 8800

    try:
        rpc_socket.connect(('127.0.0.1', port))
    except ConnectionRefusedError:
        logging.error('Unable to connect!')
        sys.exit(1)

    #rpc_socket.settimeout(0.5)

    # send garbage to see if it will crash

    while True:
        submit_garbage_request(rpc_socket)
        #submit_corrupted_request(rpc_socket)
        #submit_corrupted_get_request(rpc_socket)
        #submit_corrupted_set_request(rpc_socket)
        #submit_wrong_types_set_request(rpc_socket)
        #time.sleep(1)


#    'take_image'
#    exposure = params.get('exposure', None)
#    newbin = params.get('binning', 1)
#    newroi = params.get('roi', None)
#
#    'save_image'
#    filename = params.get('filename', None)
#
#    'set_cooler_state'
#    state = params.get('cooler_state', None)
#
#    'set_target_temperature'
#    target = params.get('target_temperature', None)
#
#    focuser_move_absolute_position
#    abspos = params.get('absolute_position', None)


