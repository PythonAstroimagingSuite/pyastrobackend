""" RPC Mount solution """

import sys
import time
import logging

from ..BaseBackend import BaseMount

from pyastrobackend.RPC.RPCDeviceBase import RPCDeviceThread, RPCDevice


class RPCMountThread(RPCDeviceThread):
    def __init__(self, port, user_data, *args, **kwargs):
        super().__init__(port, user_data, *args, **kwargs)


class Mount(RPCDevice, BaseMount):
    def __init__(self, backend=None):
        super().__init__(backend)

        self.rpc_manager = RPCMountThread(8800, None)
        self.rpc_manager.event_callbacks.append(self.event_callback)

    def event_callback(self, event, *args):
        if event == 'Connection':
            self.connected = True

    def send_radec_command(self, cmd, ra, dec):
        params = {'ra': ra, 'dec': dec}
        return self.send_command(cmd, params)

    def can_park(self):
        val = self.get_scalar_value('mount_can_park', 'can_park', (bool,))
        return val

    def is_parked(self):
        val = self.get_scalar_value('mount_at_park', 'at_park', (bool,))
        return val

    def get_position_altaz(self):
        """Returns tuple of (alt, az) in degrees"""
        rc = self.send_server_request('mount_get_altaz', None)

        if not rc:
            logging.error('RPC get_position_altaz: error sending json request!')
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
            logging.error('RPC get_position_altaz: resp is None!')
            sys.exit(1)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC saveimageCamera status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:get_position_altaz() - error getting settings!')
            return None

        result = resp['result']
        alt = result.get('alt', None)
        az = result.get('az', None)
        return alt, az

    def get_position_radec(self):
        """Returns tuple of (ra, dec) with ra in decimal hours and dec in degrees"""

        rc = self.send_server_request('mount_get_radec', None)

        if not rc:
            logging.error('RPC get_position_radec: error sending json request!')
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
            logging.error('RPC get_position_radec: resp is None!')
            sys.exit(1)

        # FIXME parse out status?
        status = 'result' in resp

#        logging.debug(f'RPC saveimageCamera status/resp = {status} {resp}')

        if not status:
            logging.warning('RPC:get_position_radec() - error getting settings!')
            return None

        result = resp['result']
        ra = result.get('ra', None)
        dec = result.get('dec', None)
        return ra, dec

    def get_pier_side(self):
        val = self.get_scalar_value('mount_pier_side', 'pier_side', (str,))
        return val

    def get_side_physical(self):
        logging.warning('Mount.get_side_physical() is not implemented for RPC!')
        return None

    def get_side_pointing(self):
        logging.warning('Mount.get_side_pointing() is not implemented for RPC!')
        return None

    def is_slewing(self):
        val = self.get_scalar_value('mount_is_slewing', 'is_slewing', (bool,))
        return val

    def abort_slew(self):
        self.send_command('mount_abort_slew', {})

    def park(self):
        self.send_command('mount_park', {})

    def slew(self, ra, dec):
        """Slew to ra/dec with ra in decimal hours and dec in degrees"""
        #self.mount.SlewToCoordinates(ra, dec)
        return self.send_radec_command('mount_slew_radec', ra, dec)

    def sync(self, ra, dec):
        """Sync to ra/dec with ra in decimal hours and dec in degrees"""
        #self.mount.SyncToCoordinates(ra, dec)
        return self.send_radec_command('mount_sync_radec', ra, dec)

    def unpark(self):
        self.send_command('mount_unpark', {})

    def set_tracking(self, onoff):
        #rc = self.mount.Tracking = onoff
        #return rc
        logging.debug(f'set_tracking: setting to {onoff}')
        self.set_scalar_value('mount_set_tracking', 'tracking', onoff)
        #time.sleep(0.1)
        #check
        val = self.get_scalar_value('mount_get_tracking', 'tracking', (bool,))
        rc = val == onoff
        logging.debug(f'set_tracking: Tracking = {val} rc = {rc}')
        return rc

    def get_tracking(self):
        val = self.get_scalar_value('mount_get_tracking', 'tracking', (bool,))
        return val
