#
# ASCOM filterwheel device
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
from pyastrobackend.BaseBackend import BaseFilterWheel

import logging

import pythoncom
import win32com.client

class FilterWheel(BaseFilterWheel):
    def __init__(self, backend=None):
        self.filterwheel = None
        # backend ignore for ASCOM

    def has_chooser(self):
        return True

    def show_chooser(self, last_choice):
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType = "FilterWheel"
        filterwheel = chooser.Choose(last_choice)
        logging.debug(f'choice = {filterwheel}')
        return filterwheel

    def connect(self, name):
        pythoncom.CoInitialize()
        self.filterwheel = win32com.client.Dispatch(name)

        if self.filterwheel.Connected:
            logging.debug("	-> filterwheel was already connected")
        else:
            try:
                self.filterwheel.Connected = True
            except Exception:
                # FIXME Need to tighten up this exception
                logging.error('ASCOMBackend:filterwheel:connect() Exception '
                              '->', exc_info=True)
                return False

        if self.filterwheel.Connected:
            logging.debug(f"	Connected to filter wheel {name} now")
        else:
            logging.error("	Unable to connect to filter wheel, expect exception")

        return True

    def disconnect(self):
        if self.filterwheel:
            if self.filterwheel.Connected:
                self.filterwheel.Connected = False
                self.filterwheel = None

    def is_connected(self):
        if self.filterwheel:
            return self.filterwheel.Connected
        else:
            return False

    def get_position(self):
        return self.filterwheel.Position

    def get_position_name(self):
        #FIXME this should check return from get names, etc
        return self.get_names()[self.get_position()]

    def set_position(self, pos):
        """Sends request to driver to move filter wheel position

        This DOES NOT wait for filter to move into position!

        Use is_moving() method to check if its done.
        """
        if pos < self.get_num_positions():
            self.filterwheel.Position = pos
            return True
        else:
            return False

    def set_position_name(self, name):
        """Sends request to driver to move filter wheel position

        This DOES NOT wait for filter to move into position!

        Use is_moving() method to check if its done.
        """
        names = self.get_names()
        try:
            newpos = names.index(name)
        except ValueError:
            newpos = -1

        if newpos == -1:
            return False
        else:
            self.filterwheel.Position = newpos
            return True

    def is_moving(self):
        # ASCOM API defines position of -1 as wheel in motion
        return self.get_position() == -1

    def get_names(self):
        # names are setup in the 'Setup' dialog for the filter wheel
        return self.filterwheel.Names

    def get_num_positions(self):
        return len(self.get_names())
