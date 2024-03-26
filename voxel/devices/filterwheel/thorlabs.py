import logging
import time
import serial
from voxel.devices.filterwheel.base import BaseFilterWheel

# constants for the Thorlabs FW102C filter wheel

SWITCH_TIME_S = 0.1 # estimated timing

class Cmd(StrEnum):
    Position = "pos"  # Enable/Disable Laser Emission. Or DL?
    Speed = "speed"  # Enable(1)/Disable(0) External power control

class Query(StrEnum):
    Position = "pos?"  # Enable/Disable Laser Emission. Or DL?
    ID = "*idn?"  # Gets the integer index of the filter wheel

class SpeedModes(IntEnum):
    FAST = 1,
    SLOW = 0

THORLABS_COM_SETUP = \
    {
        "baudrate": 115200,
        "bytesize": EIGHTBITS,
        "parity": PARITY_NONE,
        "stopbits": STOPBITS_ONE,
        "xonxoff": False,
        "timeout": 1
    }

REPLY_TERMINATION = b'\r\n'

class FilterWheel(BaseFilterWheel):

    """Filter Wheel Abstraction from an ASI Tiger Controller."""

    def __init__(self, port: str, filters: dict):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.ser = Serial(port, **THORLABS_COM_SETUP) if type(port) != Serial else port
        self.id = self.get(Query.ID)
        self.filters = filters
        # force homing of the wheel
        self.filter = next(key for key, value in self.filters.items() if value == 0)
        # force slow moving by default
        self.set(Cmd.Speed, SpeedModes.SLOW)

    @property
    def filter(self):
        filter_position = self.get(Query.Position)
        return next(key for key, value in self.filters.items() if value == filter_positin)

    @filter.setter
    def filter(self, filter_name: str):
        """Set the filterwheel index."""
        self._filter = filter_name
        self.set(Cmd.Position, self.filters[filter_name])
        time.sleep(SWITCH_TIME_S)

    def close(self):
        self.ser.close()

    def get(self, msg: Query) -> str:
        """Request a setting from the device."""
        reply = self._send(msg.value)
        return reply

    def set(self, msg: Cmd, value) -> str:
        return self._send(f"{msg}={value}")

    def _send(self, msg: str, raise_timeout: bool = True) -> str:
        """send a message and return the reply.
        :param msg: the message to send in string format
        :param raise_timeout: bool to indicate if we should raise an exception
            if we timed out.
        :returns: the reply (without line formatting chars) in str format
            or emptystring if no reply. Raises a timeout exception if flagged
            to do so.
        """
        # Note: Timing out on a serial port read does not throw an exception,
        #   so we need to do this manually.

        # All outgoing commands are bookended with a '\r\n' at the beginning
        # and end of the message.
        prefix_msg = f'{self.prefix}{msg}\r'
        self.ser.write(prefix_msg.encode('ascii'))
        start_time = perf_counter()
        # Read the first '\r\n'.
        reply = self.ser.read_until(REPLY_TERMINATION)
        # Raise a timeout if we got no reply and have been flagged to do so.
        if not len(reply) and raise_timeout and \
                perf_counter() - start_time > self.ser.timeout:
            raise SerialTimeoutException
        return reply.rstrip(REPLY_TERMINATION).decode('utf-8')