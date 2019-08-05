from abc import ABCMeta, abstractmethod

class BaseDeviceBackend(metaclass=ABCMeta):
    """
    Definition of the backend class to be subclassed by actual classes implementing
    a particular backend.

    A backend represents the communication mechanism for the different device
    actions to interact with the actual device drivers underneath.  For INDI this
    would be the indi-server.  For ASCOM it is a placeholder as there is no
    actual conduit since all calls are within the process.
    """

    @abstractmethod
    def connect(self):
        """
        Connect to the backennd.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from backend.
        """
        pass

    @abstractmethod
    def isConnected(self):
        """
        Test to see if backend is connected.

        :return: True if connected, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def newCamera(self):
        """
        Create a new :class:`BaseCamera` reference.

        :return: :class:`BaseCamera` object.
        :rtype: :class:`BaseCamera`
        """
        pass

    @abstractmethod
    def newFocuser(self):
        """
        Create a new :class:`BaseFocuser` reference.

        :return: :class:`BaseFocuser` object.
        :rtype: :class:`BaseFocuser`
        """
        pass

    @abstractmethod
    def newFilterWheel(self):
        """
        Create a new :class:`BaseFilterWheel` reference.

        :return: :class:`BaseFilterWheel` object.
        :rtype: :class:`BaseFilterWheel`
        """
        pass

    @abstractmethod
    def newMount(self):
        """
        Create a new :class:`BaseMount` reference.

        :return: :class:`BaseMount` object.
        :rtype: :class:`BaseMount`
        """
        pass


class BaseCamera(metaclass=ABCMeta):
    """
    Definition of the camera class to be subclassed by actual classes implementing
    a particular camera driver.
    """

    @abstractmethod
    def has_chooser(self):
        """
        Test if a device chooser UI (ie., ASCOM) is available or not.

        :return: True if chooser available, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def show_chooser(self, last_choice):
        """
        Launch chooser for driver.

        Use :meth:`has_chooser` to test if one is available for a given backend/camera.

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def connect(self, name):
        """
        Connect to device.

        :param name: Name of driver.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from device.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Test if a device is connected.

        :return: True if connected, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_camera_name(self):
        """
        Get the camera name - result depends on backend in use.

        :return: Name of camera device.
        :rtype: str
        """
        pass

    @abstractmethod
    def get_camera_description(self):
        """
        Get the camera name - result depends on backend in use.

        :return: Description for camera device.
        :rtype: str
        """
        pass

    @abstractmethod
    def get_driver_info(self):
        """
        Get information about camera - result depends on backend in use.

        :return: Driver information about camera device.
        :rtype: str
        """
        pass

    @abstractmethod
    def get_driver_version(self):
        """
        Get version information about camera - result depends on backend in use.

        :return: Driver version information.
        :rtype: str
        """
        pass

# this is ASCOM specific!
#    @abstractmethod
#    def get_driver_interface_version(self):
#        pass

    @abstractmethod
    def get_state(self):
        """
        Get camera state.

        :returns:
                -1   Camera State unknown
                0    Camera idle
                2    Camera is busy (exposing)
                5    Camera error
        :rtype int:
        """
        # TODO Need to fix formatting of multiple return values.

        pass

    @abstractmethod
    def start_exposure(self, expos):
        """
        Start an exposure.

        :param expos: Exposure length (seconds)
        :ptype float:
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def stop_exposure(self):
        """
        Stop exposure.

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def check_exposure(self):
        """
        Check if exposure is complete.

        :return: True if exposure complete.
        :rtype: bool
        """
        pass

    @abstractmethod
    def check_exposure_success(self):
        """
        Check if exposure was successful - only valid if check_exposure() returns True.

        :return: True if exposure complete.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_exposure_progress(self):
        """
        Get percentage completion of exposure.
        Use :meth:`supports_progress` to test if driver supports this call.

        :return: Percentage completion of exposure.
        :rtype: int
        """
        pass

    @abstractmethod
    def supports_progress(self):
        """
        Check if exposure progress is supported.

        :return: True if progress info is available.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_image_data(self):
        """
        Return image data from last image taken.

        :return: Image data or None if not available.
        """
        pass

    @abstractmethod
    def get_pixelsize(self):
        """
        Return pixel size for camera sensor.

        :returns:
            A tuple containing the X and Y pixel sizes.
        :rtype: (float, float)
        """
        pass

    @abstractmethod
    def get_egain(self):
        """
        Return gain for camera as e- per ADU.

        :return: Camera gain
        :rtype: float
        """
        pass

    @abstractmethod
    def get_camera_gain(self):
        """
        Return gain for camera (not all cameras support).

        :return: Camera gain
        :rtype: float
        """
        pass

    @abstractmethod
    def set_camera_gain(self, gain):
        """
        Set gain for camera (not all cameras support).

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_current_temperature(self):
        """
        Return current camera temperature.

        :return: Temperature (C)
        :rtype: float
        """
        pass

    @abstractmethod
    def get_target_temperature(self):
        """
        Return current target camera cooler temperature.

        :return: Target cooler temperature (C)
        :rtype: float
        """
        pass

    @abstractmethod
    def set_target_temperature(self, temp_c):
        """
        Set target camera cooler temperature.

        :param temp_c: Target cooler temperature (C)
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def set_cooler_state(self, onoff):
        """
        Set cooler on or off

        :param onff: True to turn on camera.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_cooler_state(self):
        """
        Get cooler state.

        :return: True if cooler is on.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_cooler_power(self):
        """
        Get cooler power use (percentage of maximum).

        :return: Cooler power level.
        :rtype: float
        """
        pass

    @abstractmethod
    def get_binning(self):
        """
        Return pixel binning.

        :returns:
            A tuple containing the X and Y binning.
        :rtype: (int, int)
        """
        pass

    @abstractmethod
    def set_binning(self, binx, biny):
        """
        Set pixel binning.

        :param binx: X binning
        :param biny: Y binning
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_max_binning(self):
        """
        Return maximum pixel binning supported.

        :return: Maximum binning value.
        :rtype: int
        """
        pass

    @abstractmethod
    def get_size(self):
        """
        Return size of sensor in pixels.

        :returns:
            A tuple containing the X and Y pixel sizes.
        :rtype: (int, int)
        """
        pass

    @abstractmethod
    def get_frame(self):
        """
        Return region of interest (ROI) for image capture.

        :returns:
            A tuple containing the upper left (X, Y) for ROI and width/height.
        :rtype: (int, int, int, int)
        """
        pass

    @abstractmethod
    def set_frame(self, minx, miny, width, height):
        """
        Set region of interest (ROI) for image capture.

        :param minx: Leftmost extent of ROI.
        :param miny: Uppermost extent of ROI.
        :param width: Width of ROI.
        :param height: Height of ROI.
        :returns: True on success.
        :rtype: bool
        """
        pass

class BaseFocuser(metaclass=ABCMeta):
    @abstractmethod
    def has_chooser(self):
        """
        Test if a device chooser UI (ie., ASCOM) is available or not.

        :return: True if chooser available, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def show_chooser(self, last_choice):
        """
        Launch chooser for driver.

        Use :meth:`has_chooser` to test if one is available for a given backend/camera.

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def connect(self, name):
        """
        Connect to device.

        :param name: Name of driver.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from device.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Test if a device is connected.

        :return: True if connected, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_absolute_position(self):
        """
        Get absolute position of focuser.

        :return:  Absolute position of focuser.
        :rtype: int
        """
        pass

    @abstractmethod
    def move_absolute_position(self, abspos):
        """
        Move focuser to absolute position.

        :param abspos: Target position for focuser.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_current_temperature(self):
        """
        Get temperature from focuser.

        :return:  Temperature (C).
        :rtype: float
        """
        pass

    def get_max_absolute_position(self):
        """
        Get maximum possible absolute position of focuser.

        :return:  Absolute maximum possible position of focuser.
        :rtype: int
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop focuser motion..

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_moving(self):
        """
        Check if focuser is moving.

        :return: True if focuser is moving.
        :rtype: bool
        """
        pass

class BaseFilterWheel(metaclass=ABCMeta):
    @abstractmethod
    def has_chooser(self):
        """
        Test if a device chooser UI (ie., ASCOM) is available or not.

        :return: True if chooser available, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def show_chooser(self, last_choice):
        """
        Launch chooser for driver.

        Use :meth:`has_chooser` to test if one is available for a given backend/camera.

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def connect(self, name):
        """
        Connect to device.

        :param name: Name of driver.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from device.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Test if a device is connected.

        :return: True if connected, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_position(self):
        """
        Get position of filter wheel.
        First position is 0!

        :return:  Position of filter wheel.
        :rtype: int
        """
        pass

    @abstractmethod
    def get_position_name(self):
        """
        Get name of filter at current position.

        :return:  Name of current filter.
        :rtype: str
        """
        pass

    @abstractmethod
    def set_position(self, abspos):
        """
        Set position of filter wheel.
        First position is 0!

        :param abspos:  New position of filter wheel.
        :return: True on success.
        :rtype: int
        """
        pass

    @abstractmethod
    def set_position_name(self, name):
        """
        Set position of filter wheel by filter name..

        :param name:  Name of new position of filter wheel.
        :return: True on success.
        :rtype: int
        """
        pass

    @abstractmethod
    def is_moving(self):
        """
        Check if filter wheel is moving.

        :return: True if filter wheel is moving.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_names(self):
        """
        Get names of all filter positions.

        :return: List of filter names.
        :rtype: list
        """
        pass

    @abstractmethod
    def get_num_positions(self):
        """
        Get number of filter positions.

        :return: Number of filter positions
        :rtype: int
        """
        pass

class BaseMount(metaclass=ABCMeta):
    @abstractmethod
    def has_chooser(self):
        """
        Test if a device chooser UI (ie., ASCOM) is available or not.

        :return: True if chooser available, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def show_chooser(self, last_choice):
        """
        Launch chooser for driver.

        Use :meth:`has_chooser` to test if one is available for a given backend/camera.

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def connect(self, name):
        """
        Connect to device.

        :param name: Name of driver.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from device.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Test if a device is connected.

        :return: True if connected, False otherwise.
        :rtype: bool
        """
        pass

    @abstractmethod
    def can_park(self):
        """
        Test if a mount can park.

        :return: True if mount can park.
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_parked(self):
        """
        Test if mount is parked.

        :return: True if mount is parked.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_position_altaz(self):
        """
        Get alt/az position of mount.

        :returns:
            Tuple of (alt, az) in degrees.
        :rtype: (float, float)
        """
        pass

    @abstractmethod
    def get_position_radec(self):
        """
        Get RA/DEC position of mount.

        :returns:
            Tuple of (ra, dec) with ra in decimal hours and dec in degrees.
        :rtype: (float, float)
        """
        pass

    @abstractmethod
    def get_pier_side(self):
        """
        Returns backend specific pier side information.
        **NOTE:** **NOT** recommended for use as ASCOM and INDI may give
        different results for different drivers - not tested extensively at all
        so use with caution.

        :returns:
            'EAST', 'WEST' or None if unknown.
        """
        pass

    @abstractmethod
    def get_side_physical(self):
        """
        Get physical side of mount.
        **NOTE:** **NOT** tested extensively with all INDI drivers so it is recommended
        to test results for 'normal' and 'through the pole' positions on both side of
        the pier with a given mount driver!

        :returns:
            'EAST', 'WEST' or None if unknown.
        """
        pass

    @abstractmethod
    def get_side_pointing(self):
        """
        Get side of meridian where mount is pointing.
        **NOTE** may not be same as result from get_side_physical() if
        counterweights are pointing up, etc!
        **NOTE:** **NOT** tested extensively with all INDI drivers so it is recommended
        to test results for 'normal' and 'through the pole' positions on both side of
        the pier with a given mount driver!

        :returns:
            'EAST', 'WEST' or None if unknown.
        """
        pass

    @abstractmethod
    def is_slewing(self):
        """
        Test if mount is slewing.

        :return: True if mount is slewing.
        :rtype: bool
        """
        pass

    @abstractmethod
    def abort_slew(self):
        """
        Abort slew.

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def park(self):
        """
        Park mount.

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def slew(self, ra, dec):
        """
        Slew mount to RA/DEC position.

        :param ra: RA in decimal hours.
        :param dec: DEC in degrees.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def sync(self, ra, dec):
        """
        Sync mount to RA/DEC position.

        :param ra: RA in decimal hours.
        :param dec: DEC in degrees.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def unpark(self):
        """
        Unark mount.

        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def set_tracking(self, onoff):
        """
        Enable/disable mount tracking.

        :param onoff: Flag to turn tracking on/off.
        :return: True on success.
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_tracking(self):
        """
        Get mount tracking state.

        :return: True if tracking.
        :rtype: bool
        """
        pass