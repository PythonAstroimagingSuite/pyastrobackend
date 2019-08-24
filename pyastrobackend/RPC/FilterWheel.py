""" RPC FilterWheel solution """

from ..BaseBackend import BaseFilterWheel

from pyastrobackend.RPC.RPCDeviceBase import RPCDeviceThread, RPCDevice

# 0 = none, higher shows more
LOG_SERVER_TRAFFIC = 1

class RPCFilterWheelThread(RPCDeviceThread):
    def __init__(self, port, user_data, *args, **kwargs):
        super().__init__(port, user_data, *args, **kwargs)


class FilterWheel(RPCDevice, BaseFilterWheel):
    def __init__(self, backend=None):
        super().__init__(backend)

        self.rpc_manager = RPCFilterWheelThread(8800, None)
        self.rpc_manager.event_callbacks.append(self.event_callback)

    def event_callback(self, event, *args):
#        logging.debug(f'Focsuer event_callback: {event} {args})')
        if event == 'Connection':
            self.connected = True
#        elif event == 'Response':
#            req_id = args[0]
#            logging.debug(f'event_callback: req_id = {req_id}')


    def get_position(self):
        return self.get_scalar_value('filterwheel_get_position',
                                    'filter_position',
                                    (float,int))

    def get_position_name(self):
        #FIXME this should check return from get names, etc
        return self.get_names()[self.get_position()]

    def set_position(self, pos):
        """Sends request to driver to move filter wheel position

        This DOES NOT wait for filter to move into position!

        Use is_moving() method to check if its done.
        """
        if pos < self.get_num_positions():
            return self.set_scalar_value('filterwheel_move_position',
                              'filter_position', pos)
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
            self.set_position(newpos)
            return True

    def is_moving(self):
        # ASCOM API defines position of -1 as wheel in motion
        return self.get_position() == -1

    def get_names(self):
        # names are setup in the 'Setup' dialog for the filter wheel
        return self.get_list_value('filterwheel_get_filter_names', 'filter_names')

    def get_num_positions(self):
        return len(self.get_names())

