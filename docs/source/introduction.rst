Introduction
============



What is pyastrobackend?
----------------------

Pyastrobackend is a abstraction later which presents a singular API to python
applications allowing the use of ASCOM, MaximDL or INDI device driver frameworks underneath.
The goal is allow one to have a single source tree for an astronomical application
and be able to run it on a system using ASCOM, MaximDL or INDI.

How does it work?
-----------------

An application first determines which "backend" (ASCOM or INDI) is required for
the given system using the :func:`get_backend_for_os` function.

Then the application imports the appropriate backend and device control modules
for the system.

Once the backend and devices are connected then all api calls are uniform between
the ASCOM and INDI implementations.  This allows a single code base to work on both.

.. _examples:

Examples
--------

Here is an exmaple of loading the appropriate backend and camera drivers::

    from pyastrobackend.BackendConfig import get_backend_for_os

    BACKEND = get_backend_for_os()

    if BACKEND == 'ASCOM':
        from pyastrobackend.ASCOMBackend import DeviceBackend as Backend
    elif BACKEND == 'INDI':
        from pyastrobackend.INDIBackend import DeviceBackend as Backend
    else:
        raise Exception(f'Unknown backend {BACKEND}')

    if BACKEND == 'ASCOM':
        from pyastrobackend.MaximDL.Camera import Camera as MaximDL_Camera
    elif BACKEND == 'INDI':
        from pyastrobackend.INDIBackend import Camera as INDI_Camera
    else:
        raise Exception(f'Unknown backend {BACKEND}')

Later the backend and camera objects are created and the backend connected using::

        backend = Backend()

        rc = backend.connect()
        if not rc:
            logging.error('Failed to connect to backend!')
            sys.exit(-1)

        cam = None

        if BACKEND == 'ASCOM':
            cam = MaximDL_Camera()
        elif BACKEND == 'INDI':
            cam = INDI_Camera(backend)
        else:
            logging.error(f'Unknown BACKEND = {BACKEND}!')
            sys.exit(1)

Finally the camera driver is connected using::

        rc = cam.connect(camera_driver)
        if not rc:
            logging.error('Failed to connect to camera driver {camera_driver}!')
            sys.exit(-1)

Now the camera object is ready and can be used to takes images, etc.






