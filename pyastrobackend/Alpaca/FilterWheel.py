import logging
import numpy as np

from pyastrobackend.BaseBackend import BaseFilterWheel
from pyastrobackend.Alpaca.AlpacaDevice import AlpacaDevice

class FilterWheel(AlpacaDevice, BaseFilterWheel):

    def __init__(self, backend):
        # FIXME call initializer for AlpacaDevice mixin) - is this sensible way
        self._initialize_device_attr()
        self.backend = backend
        logging.info(f'alapaca filterwheel setting backend to {backend}')

    def get_position(self):
        return self.get_prop('position')

    def get_position_name(self):
        #FIXME this should check return from get names, etc
        return self.get_names()[self.get_position()]

    def set_position(self, pos):
        """Sends request to driver to move filter wheel position

        This DOES NOT wait for filter to move into position!

        Use is_moving() method to check if its done.
        """
        if pos < self.get_num_positions():
            params = {'Position': pos}
            return self.set_prop('position', params)
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
            #self.filterwheel.Position = newpos
            self.set_position(newpos)
            return True

    def is_moving(self):
        # ASCOM API defines position of -1 as wheel in motion
        return self.get_position() == -1

    def get_names(self):
        # names are setup in the 'Setup' dialog for the filter wheel
        return self.get_prop('names')

    def get_num_positions(self):
        return len(self.get_names())
