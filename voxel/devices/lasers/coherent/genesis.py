from voxel.devices.lasers import BaseLaser
import os
import ctypes as C

class GenesisLaser(BaseLaser):
    def __init__(self):
        pass

    @property
    def power_mw(self):
        pass

    @power_mw.setter
    def power_mw(self, value: float):
        pass

    @property
    def modulation_mode(self):
        pass

    @modulation_mode.setter
    def modulation_mode(self, value: str):
        pass

    @property
    def signal_temperature_c(self):
        pass

    def status(self):
        pass

    def cdrh(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def close(self):
        pass

# Example usage
if __name__ == "__main__":
    HOPS_DLL = ".\\lib\\CohrHOPS.dll"
    MAX_DEVICES = 2

    os.add_dll_directory(os.getcwd())
    os.add_dll_directory(os.path.join(os.getcwd(), "lib"))
    dll = C.cdll.LoadLibrary(HOPS_DLL)

    LPSTRING = C.Array[C.c_char]
    LPDWORD = C.POINTER(C.c_ulong)
    LPULPTR = C.POINTER(C.c_ulong * MAX_DEVICES)

    get_dll_version = dll.CohrHOPS_GetDLLVersion
    get_dll_version.argtypes = [LPSTRING]

    buffer: LPSTRING = C.create_string_buffer(100)
    def print_buffer():
        print(buffer.value.decode("utf-8"))

    get_dll_version(buffer)
    print_buffer()

    devices_connected = LPULPTR((C.c_ulong * MAX_DEVICES)())
    number_of_devices_connected = LPDWORD()
    devices_added = LPULPTR((C.c_ulong * MAX_DEVICES)())
    number_of_devices_added = LPDWORD()
    devices_removed = LPULPTR((C.c_ulong * MAX_DEVICES)())
    number_of_devices_removed = LPDWORD()

    # for connected in devices_connected:
    #     connected.contents = C.c_ulong(0)
    # number_of_devices_connected.contents = C.c_ulong(0)
    # for added in devices_added:
    #     added.contents = C.c_ulong(0)
    # number_of_devices_added.contents = C.c_ulong(0)
    # for removed in devices_removed:
    #     removed.contents = C.c_ulong(0)
    # number_of_devices_removed.contents = C.c_ulong(0)

    def print_devices():
        if devices_connected and devices_connected.contents is not None:
            print("Devices connected: ", devices_connected.contents.value)
        if number_of_devices_connected and number_of_devices_connected.contents is not None:
            print("Number of devices connected: ", number_of_devices_connected.contents.value)
        if devices_added and devices_added.contents is not None:
            print("Devices added: ", devices_added.contents.value)
        if number_of_devices_added and number_of_devices_added.contents is not None:
            print("Number of devices added: ", number_of_devices_added.contents.value)
        if devices_removed and devices_removed.contents is not None:
            print("Devices removed: ", devices_removed.contents.value)
        if number_of_devices_removed and number_of_devices_removed.contents is not None:
            print("Number of devices removed: ", number_of_devices_removed.contents.value)

    check_for_devices = dll.CohrHOPS_CheckForDevices
    check_for_devices.argtypes = [LPULPTR, LPDWORD, LPULPTR, LPDWORD, LPULPTR, LPDWORD]

    devices: int = check_for_devices(
        devices_connected, number_of_devices_connected,
        devices_added, number_of_devices_added,
        devices_removed, number_of_devices_removed
        )
    print(devices)
    # print_devices()

    class HopsDevices(C.Structure):
        _fields_ = [
            ("devices_connected", C.c_ulong),
            ("number_of_devices_connected", C.c_ulong),
            ("devices_added", C.c_ulong),
            ("number_of_devices_added", C.c_ulong),
            ("devices_removed", C.c_ulong),
            ("number_of_devices_removed", C.c_ulong)
        ]

        # initialize the structure with values of 0
        def __init__(self):
            self.devices_connected = 0
            self.number_of_devices_connected = 0
            self.devices_added = 0
            self.number_of_devices_added = 0
            self.devices_removed = 0
            self.number_of_devices_removed = 0
