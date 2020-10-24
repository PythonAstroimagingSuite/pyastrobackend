import os

LOADED_BACKENDS = {}

def get_backend_for_os():
    """
    Return the backend matching the current system.

    If the environmental variable "PYASTROBACKEND" is defined it will override
    the default value.

    :returns:
        Name of the default backend for this platform.
    :rtype: str
    """

    if 'PYASTROBACKEND' in os.environ:
        return os.environ['PYASTROBACKEND']

    # chose an implementation, depending on os
    if os.name == 'nt':
        return 'ASCOM'
    elif os.name == 'posix':
        return 'INDI'
    else:
        raise Exception('Sorry: no implementation for your platform '
                        f'({os.name}) available')

def get_backend_choices():
    """
    Returns all valid values for the backend name.

    :return: Names of all possible backends.
    :rtype: List[str]

    """
    return ['ASCOM', 'ALPACA', 'RPC', 'INDI']

def get_backend(backend_name):
    """
    Returns a backend object for the requested backend.

    :param backend_name: Name of desired backend.
    :type backend_name: str
    :raises Exception: If unavailable backend requested raises exception.
    :return: Backend instance
    :rtype: Backend object

    """
    global LOADED_BACKENDS

    if backend_name in LOADED_BACKENDS:
        return LOADED_BACKENDS[backend_name]

    if backend_name == 'ASCOM':
        from pyastrobackend.ASCOMBackend import DeviceBackend as ASCOM_Backend
        backend = ASCOM_Backend()
    elif backend_name == 'RPC':
        from pyastrobackend.RPCBackend import DeviceBackend as RPC_Backend
        backend = RPC_Backend()
    elif backend_name == 'ALPACA':
        from pyastrobackend.AlpacaBackend import DeviceBackend as ALPACA_Backend
        backend = ALPACA_Backend()
    elif backend_name == 'INDI':
        from pyastrobackend.INDIBackend import DeviceBackend as INDI_Backend
        backend = INDI_Backend()
    else:
        # FIXME Exception might be extreme for this scenario.
        #       Also should look at standard exceptions for closer match.
        raise Exception(f'Error: no implementation for backend {backend_name} '
                        'available')

    LOADED_BACKENDS[backend_name] = backend
    return backend
