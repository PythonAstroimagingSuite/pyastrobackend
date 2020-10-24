#
# RPC focuser device
#
# Copyright 2020 Michael Fulbright
#
#
#    pyastrobackend is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
""" RPC Focuser solution """

from ..BaseBackend import BaseFocuser

from pyastrobackend.RPC.RPCDeviceBase import RPCDeviceThread, RPCDevice


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
        #elif event == 'Response':
            #req_id = args[0]
            #logging.debug(f'event_callback: req_id = {req_id}')

    def get_absolute_position(self):
        return self.get_scalar_value('focuser_get_absolute_position',
                                     'absolute_position',
                                     (float, int))

    def get_max_absolute_position(self):
        return self.get_scalar_value('focuser_get_max_absolute_position',
                                     'max_absolute_position',
                                     (float, int))

    def get_current_temperature(self):
        return self.get_scalar_value('focuser_get_current_temperature',
                                     'current_temperature',
                                     (float, int))

    def is_moving(self):
        return self.get_scalar_value('focuser_is_moving', 'is_moving', (bool, ))

    def stop(self):
        return self.send_command('focuser_stop', {})

    def move_absolute_position(self, abspos):
        return self.set_scalar_value('focuser_move_absolute_position',
                                     'absolute_position',
                                     abspos)
