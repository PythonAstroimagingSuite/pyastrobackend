#
# RPC device backend
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
""" RPC solution """

from pyastrobackend.BaseBackend import BaseDeviceBackend

# messy but we'll roll MaximDL camera support under ASCOM
from pyastrobackend.RPC.Camera import Camera as RPC_Camera
from pyastrobackend.RPC.Focuser import Focuser as RPC_Focuser
from pyastrobackend.RPC.Mount import Mount as RPC_Mount
from pyastrobackend.RPC.FilterWheel import FilterWheel as RPC_FilterWheel

class DeviceBackend(BaseDeviceBackend):

    def __init__(self, mainThread=True):
        self.connected = False

    def name(self):
        return 'RPC'

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        pass

    def isConnected(self):
        return self.connected

    def newCamera(self):
        return RPC_Camera(self)

    def newFocuser(self):
        return RPC_Focuser(self)

    def newFilterWheel(self):
        return RPC_FilterWheel(self)

    def newMount(self):
        return RPC_Mount(self)
