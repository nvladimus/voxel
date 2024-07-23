import pytest
from voxel.descriptors.deliminated_property import deliminated_property, DeliminatedPropertyError, DeliminatedProperty

VALUE_MIN = 20
VALUE_MAX = 100
VALUE_STEP = 3


class DummyDevice:
    device_property3 = DeliminatedProperty(
        fget=lambda instance: getattr(instance, "_device_property3"),
        fset=lambda instance, value: setattr(instance, "_device_property3", value),
        minimum=VALUE_MIN, maximum=VALUE_MAX, step=VALUE_STEP
    )

    def __init__(self):
        self.device_property0 = 40
        self.device_property1 = 40
        self.device_property2 = 40
        self.device_property3 = 40

    @deliminated_property(minimum=VALUE_MIN, maximum=VALUE_MAX, step=VALUE_STEP)
    def device_property0(self):
        return self._device_property0

    @device_property0.setter
    def device_property0(self, value):
        self._device_property0 = value

    @deliminated_property()
    def device_property1(self):
        return self._device_property1

    @device_property1.setter
    def device_property1(self, value):
        self._device_property1 = value

    @deliminated_property(minimum=VALUE_MIN)
    def device_property2(self):
        return self._device_property2

    @device_property2.setter
    def device_property2(self, value):
        self._device_property2 = value


@pytest.fixture
def device():
    return DummyDevice()


def test_initial_values(device):
    assert device.device_property0 == 38  # Due to step size: min is 20, step is 3 so 20 + 3 * 6 = 38
    assert device.device_property1 == 40
    assert device.device_property2 == 40
    assert device.device_property3 == 38  # Due to step size: min is 20, step is 3 so 20 + 3 * 6 = 38


def test_normal_assignment(device):
    device.device_property0 = 50
    assert device.device_property0 == 50  # min is 20, step is 3 so 20 + 3 * 10 = 50

    device.device_property1 = 60
    assert device.device_property1 == 60  # No constraints

    device.device_property2 = 70
    assert device.device_property2 == 70  # No step constraint, min is 20

    device.device_property3 = 81
    assert device.device_property3 == 80  # min is 20, step is 3 so 20 + 3 * 20 = 80


def test_minimum_constraint(device):
    device.device_property0 = VALUE_MIN - 10
    assert device.device_property0 == VALUE_MIN

    device.device_property1 = float('-inf')
    assert device.device_property1 == float('-inf')

    device.device_property2 = VALUE_MIN - 5
    assert device.device_property2 == VALUE_MIN

    device.device_property3 = VALUE_MIN - 15
    assert device.device_property3 == VALUE_MIN


def test_maximum_constraint(device):
    device.device_property0 = VALUE_MAX + 10
    assert device.device_property0 == VALUE_MAX

    device.device_property1 = float('inf')
    assert device.device_property1 == float('inf')

    device.device_property2 = VALUE_MAX + 20
    assert device.device_property2 == VALUE_MAX + 20  # No max constraint

    device.device_property3 = VALUE_MAX + 15
    assert device.device_property3 == VALUE_MAX


def test_step_constraint(device):
    device.device_property0 = 52
    assert device.device_property0 == 50  # min is 20, step is 3 so 20 + 3 * 10 = 50

    device.device_property1 = 53
    assert device.device_property1 == 53  # No step constraint

    device.device_property2 = 54
    assert device.device_property2 == 54  # No step constraint

    device.device_property3 = 55
    assert device.device_property3 == 53  # min is 20, step is 3 so 20 + 3 * 11 = 53


def test_property_attributes():
    assert DummyDevice.device_property0.minimum == VALUE_MIN
    assert DummyDevice.device_property0.maximum == VALUE_MAX
    assert DummyDevice.device_property0.step == VALUE_STEP

    assert DummyDevice.device_property1.minimum == float('-inf')
    assert DummyDevice.device_property1.maximum == float('inf')
    assert DummyDevice.device_property1.step is None

    assert DummyDevice.device_property2.minimum == VALUE_MIN
    assert DummyDevice.device_property2.maximum == float('inf')
    assert DummyDevice.device_property2.step is None

    assert DummyDevice.device_property3.minimum == VALUE_MIN
    assert DummyDevice.device_property3.maximum == VALUE_MAX
    assert DummyDevice.device_property3.step == VALUE_STEP


def test_callable_min_max(device):
    class DeviceWithCallable:
        @deliminated_property(
            minimum=lambda self: self._min,
            maximum=lambda self: self._max
        )
        def dynamic_property(self):
            return self._value

        @dynamic_property.setter
        def dynamic_property(self, value):
            self._value = value

        def __init__(self):
            self._min = 0
            self._max = 100
            self._value = 50

    d = DeviceWithCallable()
    assert d.dynamic_property == 50
    d.dynamic_property = 150
    assert d.dynamic_property == 100
    d._max = 200
    d.dynamic_property = 150
    assert d.dynamic_property == 150


def test_custom_exception_invalid_min_max():
    with pytest.raises(DeliminatedPropertyError, match="Minimum value .* cannot be greater than maximum value"):
        class InvalidDevice:
            @deliminated_property(minimum=100, maximum=50)
            def invalid_property(self):
                return 0

        _ = InvalidDevice()


def test_custom_exception_invalid_step():
    class StepDevice:
        def __init__(self):
            self._value = 50

        @deliminated_property(minimum=0, maximum=100, step="invalid")  # type: ignore
        def step_property(self):
            return self._value

        @step_property.setter
        def step_property(self, value):
            self._value = value

    d = StepDevice()
    with pytest.raises(DeliminatedPropertyError, match="Invalid step value"):
        d.step_property = 50


def test_custom_exception_callable_min_max():
    class CallableDevice:
        def __init__(self):
            self._value = 50

        @deliminated_property(
            minimum=lambda self: self.get_min(),
            maximum=lambda self: self.get_max()
        )
        def dynamic_property(self):
            return self._value

        @dynamic_property.setter
        def dynamic_property(self, value):
            self._value = value

        def get_min(self):
            raise ValueError("Error in min calculation")

        @staticmethod
        def get_max():
            return 100

    d = CallableDevice()
    with pytest.raises(DeliminatedPropertyError):
        d.dynamic_property = 50


if __name__ == "__main__":
    pytest.main([__file__])
