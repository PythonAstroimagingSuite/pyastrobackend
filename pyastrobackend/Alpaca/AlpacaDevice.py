#
# Alpaca device backend
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
import logging

class AlpacaDevice:

    def _initialize_device_attr(self):
        self.device_number = None
        self.device_type = None

    # Alpaca connect string is "ALPACA:<device type>:<device_number>"
    def connect(self, name):
        device_number = None
        device_type = None
        try:
            alpaca_field, device_type, device_number = name.split(':')
            device_number = int(device_number)
        except ValueError:
            logging.error('Error parsing Alpaca device spec in connect()')

        if alpaca_field != 'ALPACA' or None in [device_type, device_number]:
            logging.error('Connect requires Alpaca device spec in the form '
                          '"ALPACA:<device type>:<device_number>"!')

            self.device_number = None
            self.device_type = None
            return False

        logging.debug(f'Alpaca connect device_type={device_type}, '
                      f'device_number={device_number}')
        logging.debug(f'connect camera {name}')

        self.device_number = device_number
        self.device_type = device_type

        return True

    def disconnect(self):
        # FIXME should this do anything?
        return True

    def is_connected(self):
        # return False if device attributes not initialized
        if None in [self.device_type, self.device_number]:
            return False

        val = self.get_prop('connected')
        return val

    def has_chooser(self):
        return False

    def show_chooser(self, last_choice):
        logging.warning('Alpaca devices do not have a chooser')
        return None

    def get_prop(self, prop, params={}, returndict=False):
        return self.backend.get_prop(self.device_type, self.device_number,
                                     prop, params, returndict)

    def set_prop(self, prop, params={}):
        return self.backend.set_prop(self.device_type, self.device_number,
                                     prop, params)
