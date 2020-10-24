import logging
import numpy as np

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
