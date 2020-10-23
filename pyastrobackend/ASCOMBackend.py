""" Pure ASCOM solution """

import logging
import warnings

import numpy as np
import pythoncom
import win32com.client

from pyastrobackend.BaseBackend import BaseDeviceBackend, BaseCamera, BaseFocuser
from pyastrobackend.BaseBackend import BaseFilterWheel, BaseMount

from pyastrobackend.ASCOM.Camera import Camera as ASCOM_Camera
from pyastrobackend.ASCOM.Focuser import Focuser as ASCOM_Focuser
from pyastrobackend.ASCOM.FilterWheel import FilterWheel
from pyastrobackend.ASCOM.Mount import Mount

from pyastrobackend.RPC.Camera import Camera as RPC_Camera
from pyastrobackend.RPC.Focuser import Focuser as RPC_Focuser

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

    # FIXME Need to move RPCCamera and RPCFocuser into a different backend
    def newRPCCamera(self):
        return RPC_Camera(self)

    # FIXME Need to move RPCCamera and RPCFocuser into a different backend
    def newRPCFocuser(self):
        return RPC_Focuser(self)
