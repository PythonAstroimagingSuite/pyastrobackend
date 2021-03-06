#
# Alpaca mount device
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

from pyastrobackend.BaseBackend import BaseMount
from pyastrobackend.Alpaca.AlpacaDevice import AlpacaDevice

PIEREAST = 0
PIERWEST = 1

class Mount(AlpacaDevice, BaseMount):

    def __init__(self, backend):
        # FIXME call initializer for AlpacaDevice mixin) - is this sensible way
        self._initialize_device_attr()
        self.backend = backend
        logging.info(f'alapaca mount setting backend to {backend}')

    def can_park(self):
        return self.get_prop('canpark')

    def is_parked(self):
        return self.get_prop('atpark')

    def get_position_altaz(self):
        """Returns tuple of (alt, az) in degrees"""
        alt = self.get_prop('altitude')
        az = self.get_prop('azimuth')
        return (alt, az)

    def get_position_radec(self):
        """Returns tuple of (ra, dec) with ra in decimal hours and dec in degrees"""
        ra = self.get_prop('rightascension')
        dec = self.get_prop('declination')
        return (ra, dec)

    def get_pier_side(self):
        side = self.get_prop('sideofpier')

        # 0 = pierEast, 1 = pierWest, -1 = pierUnknown
        if side == PIEREAST:
            return 'EAST'
        elif side == PIERWEST:
            return 'WEST'
        else:
            return None

    def get_side_physical(self):
        logging.warning('Mount.get_side_physical() is not implemented for ASCOM!')
        return None

    def get_side_pointing(self):
        logging.warning('Mount.get_side_pointing() is not implemented for ASCOM!')
        return None

    def is_slewing(self):
        return self.get_prop('slewing')

    def abort_slew(self):
        return self.set_prop('abortslew', {})

    def park(self):
        return self.set_prop('park', {})

    def slew(self, ra, dec):
        """Slew to ra/dec with ra in decimal hours and dec in degrees"""
        params = {'RightAscension': ra, 'Declination': dec}
        #return self.set_prop('slewtocoordinates', params)
        return self.set_prop('slewtocoordinatesasync', params)

    def sync(self, ra, dec):
        """Sync to ra/dec with ra in decimal hours and dec in degrees"""
        params = {'RightAscension': ra, 'Declination': dec}
        return self.set_prop('synctocoordinates', params)

    def unpark(self):
        return self.set_prop('unpark', {})

    def set_tracking(self, onoff):
        #rc = self.mount.Tracking = onoff
        #return rc
        logging.debug(f'set_tracking: setting to {onoff}')
        params = {'Tracking': onoff}
        self.set_prop('tracking', params)
        #time.sleep(0.1)
        #check
        rc = self.get_prop('tracking') == onoff
        #logging.debug(f'set_tracking: self.mount.Tracking = {self.mount.Tracking} rc = {rc}')
        return rc

    def get_tracking(self):
        return self.get_prop('tracking')
