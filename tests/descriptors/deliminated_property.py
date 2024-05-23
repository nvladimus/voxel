from voxel.descriptors.deliminated_property import DeliminatedProperty

VALUE_MIN = 20
VALUE_MAX = 100
VALUE_STEP = 3

class DummyDevice:
    device_property3 = DeliminatedProperty(fget=lambda instance: getattr(instance, "_device_property3"),
                                           fset=lambda instance, value: setattr(instance, "_device_property3", value),
                                           minimum=VALUE_MIN, maximum=VALUE_MAX, step=VALUE_STEP)

    def __init__(self):
        self.device_property0 = 10
        self.device_property1 = 20
        self.device_property2 = 30
        self.device_property3 = 40

    @DeliminatedProperty(minimum=VALUE_MIN, maximum=VALUE_MAX, step=VALUE_STEP)
    def device_property0(self):
        """Example property with minimum, maximum, and step as arguments"""
        return self._device_property0

    @device_property0.setter
    def device_property0(self, value):
        self._device_property0 = value

    @DeliminatedProperty
    def device_property1(self):
        """Example property with no arguments. Can also use @property"""
        return self._device_property1

    @device_property1.setter
    def device_property1(self, value):
        self._device_property1 = value

    @DeliminatedProperty(minimum=VALUE_MIN)
    def device_property2(self):
        """Example property with minimum as argument"""
        return self._device_property2

    @device_property2.setter
    def device_property2(self, value):
        self._device_property2 = value

if __name__ == "__main__":

    device = DummyDevice()

    # example device_property
    print('device_property')
    print(device.device_property0)
    device.device_property0 = 50
    print(device.device_property0)
    device.device_property0 = 120
    print(device.device_property0)
    device.device_property0 = -5
    print(device.device_property0)

    print(type(device).device_property0.minimum, type(device).device_property0.maximum, type(device).device_property0.step)

    # example device_property1
    print('\ndevice_property1')
    print(device.device_property1)
    device.device_property1 = 50
    print(device.device_property1)
    device.device_property1 = 120
    print(device.device_property1)
    device.device_property1 = -5
    print(device.device_property1)

    print(type(device).device_property1.minimum, type(device).device_property1.maximum, type(device).device_property1.step)

    # example device_property2
    print('\ndevice_property2')
    print(device.device_property2)
    device.device_property2 = 50
    print(device.device_property2)
    device.device_property2 = 120
    print(device.device_property2)
    device.device_property2 = -5
    print(device.device_property2)

    print(type(device).device_property2.minimum, type(device).device_property2.maximum, type(device).device_property1.step)

    # example device_property3
    print('\ndevice_property3')
    print(device.device_property3)
    device.device_property3 = 50
    print(device.device_property3)
    device.device_property2 = 120
    print(device.device_property3)
    device.device_property2 = -5
    print(device.device_property3)

    print(type(device).device_property3.minimum, type(device).device_property3.maximum,
          type(device).device_property3.step)