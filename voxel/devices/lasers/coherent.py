import serial

class CoherentLaser:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.ser.flush()

    def send_command(self, command):
        """Send a command to the laser and return the response."""
        self.ser.write(f"{command}\r\n".encode('utf-8'))
        response = self.ser.readline().decode('utf-8').strip()
        return response

    def query_status(self):
        """Query the status of the laser."""
        return self.send_command("?HST")

    def set_power(self, power):
        """Set the laser power (in watts)."""
        return self.send_command(f"PCMD={power}")

    def get_power(self):
        """Get the current laser power."""
        return self.send_command("?P")

    def enable_laser(self):
        """Enable the laser."""
        return self.send_command("KEY=1")

    def disable_laser(self):
        """Disable the laser."""
        return self.send_command("KEY=0")

    def close(self):
        """Close the serial connection."""
        self.ser.close()

# Example usage
if __name__ == "__main__":
    laser_driver = CoherentLaser(port='COM3')  # Adjust COM port as needed
    print(laser_driver.query_status())
    print(laser_driver.set_power(10))  # Set power to 10W
    print(laser_driver.get_power())
    print(laser_driver.enable_laser())
    print(laser_driver.query_status())
    print(laser_driver.disable_laser())
    laser_driver.close()