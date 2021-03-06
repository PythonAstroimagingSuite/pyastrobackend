#
# ASCOM mount device
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
""" Pure ASCOM solution """
from pyastrobackend.BaseBackend import BaseMount

import logging
from enum import Enum
import pythoncom
import win32com.client

class PierSide(Enum):
    EAST = 0
    UNKNOWN = -1
    WEST = 1

class Mount(BaseMount):
    def __init__(self, backend=None):
        self.mount = None
        #backend ignored for ASCOM

    def has_chooser(self):
        return True

    def show_chooser(self, last_choice):
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType = "Telescope"
        mount = chooser.Choose(last_choice)
        logging.debug(f'choice = {mount}')
        return mount

    def connect(self, name):
        pythoncom.CoInitialize()
        self.mount = win32com.client.Dispatch(name)

        if self.mount.Connected:
            logging.debug("	-> mount was already connected")
        else:
            try:
                self.mount.Connected = True
            except Exception:
                # FIXME Need to tighten up this exception
                logging.error('ASCOMBackend:mount:connect() Exception ->',
                              exc_info=True)
                return False

        if self.mount.Connected:
            logging.debug(f"	Connected to mount {name} now")
        else:
            logging.error("	Unable to connect to mount, expect exception")

        return True

    def disconnect(self):
        if self.mount:
            if self.mount.Connected:
                self.mount.Connected = False
                self.mount = None

    def is_connected(self):
        if self.mount:
            return self.mount.Connected
        else:
            return False

    def can_park(self):
        return self.mount.CanPark

    def is_parked(self):
        return self.AtPark

    def get_position_altaz(self):
        """Returns tuple of (alt, az) in degrees"""
        alt = self.mount.Altitude
        az = self.mount.Azimuth
        return (alt, az)

    def get_position_radec(self):
        """Returns tuple of (ra, dec) with ra in decimal hours and dec in degrees"""
        ra = self.mount.RightAscension
        dec = self.mount.Declination
        return (ra, dec)

    def get_pier_side(self):
        side = self.mount.SideOfPier
        #logging.debug(f'ASCOM Mount.get_pier_side() reports {side} {type(side)}')
        #logging.debug(f'PierSide.East = {PierSide.EAST} {type(PierSide.EAST)}')
        if side == PierSide.EAST.value:
            return 'EAST'
        elif side == PierSide.WEST.value:
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
        return self.mount.Slewing

    def abort_slew(self):
        self.mount.AbortSlew()

    def park(self):
        self.mount.Park()

    def slew(self, ra, dec):
        """Slew to ra/dec with ra in decimal hours and dec in degrees"""
        self.mount.SlewToCoordinates(ra, dec)

    def sync(self, ra, dec):
        """Sync to ra/dec with ra in decimal hours and dec in degrees"""
        self.mount.SyncToCoordinates(ra, dec)

    def unpark(self):
        self.mount.Unpark()

    def set_tracking(self, onoff):
        #rc = self.mount.Tracking = onoff
        #return rc
        logging.debug(f'set_tracking: setting to {onoff}')
        self.mount.Tracking = onoff
        #time.sleep(0.1)
        #check
        rc = self.mount.Tracking == onoff
        logging.debug('set_tracking: self.mount.Tracking = '
                      f'{self.mount.Tracking} rc = {rc}')
        return rc

    def get_tracking(self):
        return self.mount.Tracking
