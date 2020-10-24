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
