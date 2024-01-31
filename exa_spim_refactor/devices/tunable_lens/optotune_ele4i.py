import logging
from .base import BaseTunableLens
import serial

# constants for Optotune EL-E-4i controller

MODES = {
    "external": ['MwDA', '>xxx'],
    "internal": ['MwCA', '>xxxBhh'],
}

class TunableLens(BaseTunableLens):

    def __init__(self, port: str):
        """Connect to hardware.

        :param tigerbox: TigerController instance.
        :param hardware_axis: stage hardware axis.
        """
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.tunable_lens = serial.Serial(port=port, baudrate=115200, timeout=1)
        self.tunable_lens.flush()

    @property
    def mode(self):
        """Get the tunable lens control mode."""
        mode = self.send_command('MMA', '>xxxB')[0]
        return mode

    @mode.setter
    def mode(self, mode: str):
        """Set the tunable lens control mode."""

        valid = list(MODES.keys())
        if mode not in valid:
            raise ValueError("mode must be one of %r." % valid)
        mode_list = MODES[mode]
        self.send_command(mode_list[0], mode_list[1])

    @property
    def temperature(self):
        """Get the temperature in deg C."""
        return self.send_command(b'TCA', '>xxxh')[0] * 0.0625

    def send_command(self, command, reply_fmt=None):
        if type(command) is not bytes:
            command = bytes(command, encoding='ascii')
        command = command + struct.pack('<H', crc_16(command))
        if self.debug:
            commandhex = ' '.join('{:02x}'.format(c) for c in command)
            print('{:<50} ¦ {}'.format(commandhex, command))
        self.connection.write(command)

        if reply_fmt is not None:
            response_size = struct.calcsize(reply_fmt)
            response = self.connection.read(response_size+4)
            if self.debug:
                responsehex = ' '.join('{:02x}'.format(c) for c in response)
                print('{:>50} ¦ {}'.format(responsehex, response))

            if response is None:
                raise Exception('Expected response not received')

            data, crc, newline = struct.unpack('<{}sH2s'.format(response_size), response)
            if crc != crc_16(data) or newline != b'\r\n':
                raise Exception('Response CRC not correct')

            return struct.unpack(reply_fmt, data)