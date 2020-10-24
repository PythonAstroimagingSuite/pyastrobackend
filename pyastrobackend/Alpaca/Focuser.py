#
# Alpaca focuser device
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

from pyastrobackend.BaseBackend import BaseFocuser
from pyastrobackend.Alpaca.AlpacaDevice import AlpacaDevice

class Focuser(AlpacaDevice, BaseFocuser):

    def __init__(self, backend):
        # FIXME call initializer for AlpacaDevice mixin) - is this sensible way
        self._initialize_device_attr()
        self.backend = backend
        logging.info(f'alapaca focuser setting backend to {backend}')

    def get_absolute_position(self):
        return self.get_prop('position')

    def move_absolute_position(self, abspos):
        params = {'Position': abspos}
        return self.set_prop('move', params)

    def get_max_absolute_position(self):
        return self.get_prop('maxstep')

    def get_current_temperature(self):
        return self.get_prop('temperature')

    def stop(self):
        return self.set_prop('halt', {})

    def is_moving(self):
        return self.get_prop('ismoving')
