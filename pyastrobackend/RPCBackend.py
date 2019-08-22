""" RPC solution """

from pyastrobackend.BaseBackend import BaseDeviceBackend

# messy but we'll roll MaximDL camera support under ASCOM
from pyastrobackend.RPC.Camera import Camera as RPC_Camera
from pyastrobackend.RPC.Focuser import Focuser as RPC_Focuser

class DeviceBackend(BaseDeviceBackend):

    def __init__(self, mainThread=True):
        self.connected = False

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


