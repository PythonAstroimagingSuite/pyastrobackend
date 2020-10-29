Introduction
============



What is pyastrobackend?
-----------------------

Pyastrobackend is a abstraction later which presents a singular API to Python
applications allowing the use of ASCOM, Alpaca or INDI device driver frameworks underneath.
The goal is allow one to have a single source tree for an astronomical application
and be able to run it on a system using any of these hardware frameworks.

How does it work?
-----------------

An application first determines which "backend" (for example, ASCOM or INDI)
is required for the given system using the :func:`get_backend_for_os` function.

Then the application imports the appropriate backend and device control modules
for the system.

Once the backend and devices are connected then all api calls are uniform between
the ASCOM and INDI implementations.  This allows a single code base to work on both.

.. _examples:

Examples
--------

Here is an exmaple of loading the appropriate backend and camera drivers::

    from pyastrobackend.BackendConfig import get_backend, get_backend_for_os

    backend_name = get_backend_for_os()
    backend = get_backend(backend_name)

Later the backend and camera objects are created and the backend connected using::

        rc = backend.connect()
        if not rc:
            logging.error('Failed to connect to backend!')
            sys.exit(-1)

        cam = backend.newCamera()

Finally the camera driver is connected using::

        rc = cam.connect(camera_driver)
        if not rc:
            logging.error('Failed to connect to camera driver {camera_driver}!')
            sys.exit(-1)

Now the camera object is ready and can be used to takes images, etc.







