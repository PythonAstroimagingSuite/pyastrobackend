#
# ASCOM focuser device
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
from pyastrobackend.BaseBackend import BaseFocuser

import logging

import pythoncom
import win32com.client

class Focuser(BaseFocuser):
    def __init__(self, backend=None):
        self.focus = None
        # backend ignored for ASCOM

    def has_chooser(self):
        return True

    def show_chooser(self, last_choice):
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType = "Focuser"
        focuser = chooser.Choose(last_choice)
        logging.debug(f'choice = {focuser}')
        return focuser

    def connect(self, name):
        pythoncom.CoInitialize()
        self.focus = win32com.client.Dispatch(name)

        # FIXME
        #
        # Found I had to use Generic Hub for MoonliteDRO driver or else it would
        # eventually hang from all the open/close events from running the
        # autofocus routine as a separate shoft lived application
        #
        # For some reason the generic hub returns an error if you try to access
        # the .Connected property!
        #
        # Looking at this code:
        #   https://github.com/ASCOMInitiative/ASCOMPlatform/blob/master/ASCOM.DriverConnect/ConnectForm.cs
        #
        # Around line 245 they try 'Connected' and then 'Link' and use the one which work.
        #

        try:
            #logging.debug('Connecting focuser trying "Connected"')
            self.focus.Connected = True
            #logging.debug('Connecting focuser "Connected" worked')
        except:
            # FIXME Need to tighten up this exception
            try:
                #logging.debug('Connecting focuser trying "Link"')
                self.focus.Link = True
                #logging.debug('Connecting focuser "Link" worked')
            except Exception:
                # FIXME Need to tighten up this exception
                logging.error('Both "Connected" and "Link" failed!')
                logging.error('ASCOMBackend:focuser:connect() Exception ->',
                              exc_info=True)
                return False

        if self.is_connected():
            logging.debug(f'Connected to focuser {name} now')
        else:
            logging.error('Unable to connect to focuser, expect exception')

        # check focuser works in absolute position
        if not self.focus.Absolute:
            logging.error('ERROR - focuser does not use absolute position!')

        return True

    def disconnect(self):
        if self.focus:
            if self.focus.Connected:
                self.focus.Connected = False
                self.focus = None

    def is_connected(self):
        if self.focus:
            connected = False
            try:
                #logging.debug('Focuser is_connected trying "Connected"')
                connected = self.focus.Connected
            except:
                # FIXME Need to tighten up this exception
                try:
                    #logging.debug('Focuser is_connected trying "Link"')
                    connected = self.focus.Link
                except Exception:
                    # FIXME Need to tighten up this exception
                    logging.error('Both "Connected" and "Link" failed!')
                    logging.error('ASCOMBackend:focuser:is_connected() '
                                  'Exception ->', exc_info=True)
                    return False
            return connected
        else:
            return False

    def get_absolute_position(self):
        return self.focus.Position

    def move_absolute_position(self, abspos):
        self.focus.Move(abspos)
        return True

    def get_max_absolute_position(self):
        return self.focus.MaxStep

    def get_current_temperature(self):
        return self.focus.Temperature

    def stop(self):
        self.focus.Halt()

    def is_moving(self):
        return self.focus.isMoving
