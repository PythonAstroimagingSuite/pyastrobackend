# FIXME not best way to control the backend!

#backend = 'ASCOM'
#BACKEND = 'INDI'

def get_backend_for_os():
    """
    Return the backend matching the current system.

    If the environmental variable "PYASTROBACKEND" is defined it will override
    the default value.

    :returns:
        'ASCOM' or 'INDI'.
    :rtype: str
    """
    import os

    if 'PYASTROBACKEND' in os.environ:
        return os.environ['PYASTROBACKEND']

    # chose an implementation, depending on os
    if os.name == 'nt': #sys.platform == 'win32':
        return 'ASCOM'
    elif os.name == 'posix':
        return 'INDI'
    else:
        raise Exception("Sorry: no implementation for your platform ('%s') available" % os.name)

