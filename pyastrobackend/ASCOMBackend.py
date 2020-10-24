#
# ASCOM device backend
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

import warnings

from pyastrobackend.BaseBackend import BaseDeviceBackend

from pyastrobackend.ASCOM.Camera import Camera as ASCOM_Camera
from pyastrobackend.ASCOM.Focuser import Focuser as ASCOM_Focuser
from pyastrobackend.ASCOM.FilterWheel import FilterWheel
from pyastrobackend.ASCOM.Mount import Mount

#warnings.filterwarnings('always', category=DeprecationWarning)

class DeviceBackend(BaseDeviceBackend):

    def __init__(self, mainThread=True):
        self.connected = False

    def name(self):
        return 'ASCOM'

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        pass

    def isConnected(self):
        return self.connected

    def newCamera(self):
        return ASCOM_Camera(self)

    def newFocuser(self):
        return ASCOM_Focuser(self)

    def newFilterWheel(self):
        return FilterWheel(self)

    def newMount(self):
        return Mount(self)
