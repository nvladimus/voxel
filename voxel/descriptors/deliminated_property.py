import logging
from typing import Union, Callable, Optional, Any, Literal

from voxel.descriptors.descriptor_proxy import DescriptorProxy

Number = Union[int, float]
StaticOrCallableNumber = Union[Number, Callable[[Any], Number]]


class DeliminatedProperty(property):
    def __init__(
            self,
            fget: Optional[Callable[[Any], Number]] = None,
            fset: Optional[Callable[[Any, Number], None]] = None,
            fdel: Optional[Callable[[Any], None]] = None,
            *,
            minimum: StaticOrCallableNumber = float('-inf'),
            maximum: StaticOrCallableNumber = float('inf'),
            step: Optional[StaticOrCallableNumber] = None,
            unit: str = ''
    ):
        super().__init__(fget, fset, fdel)
        self._minimum = minimum
        self._maximum = maximum
        self._step = step
        self._unit = unit
        self._instance: Any = None

        self.log = logging.getLogger(f"{self.__class__.__name__}")

    def __get__(self, instance: Any, owner=None) -> Union['DeliminatedProperty', 'DeliminatedPropertyProxy']:
        if instance is None:
            return self

        self._instance = instance

        if self.fget is None:
            raise AttributeError("unreadable attribute")

        value = self.fget(instance)
        return DeliminatedPropertyProxy(value, self)

    def __set__(self, instance: Any, value: Number) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self._instance = instance
        original_value = value
        value = self._adjust_value(value)
        if value != original_value:
            self.log.warning(f"Value {original_value} was adjusted to {value}\t{self}")
        self.fset(instance, value)

    def __delete__(self, instance: Any) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def getter(self, fget: Callable[[Any], Number]) -> 'DeliminatedProperty':
        return type(self)(
            fget, self.fset, self.fdel,
            minimum=self._minimum, maximum=self._maximum,
            step=self._step, unit=self._unit
        )

    def setter(self, fset: Callable[[Any, Number], None]) -> 'DeliminatedProperty':
        return type(self)(
            self.fget, fset, self.fdel,
            minimum=self._minimum, maximum=self._maximum,
            step=self._step, unit=self._unit
        )

    def deleter(self, fdel: Callable[[Any], None]) -> 'DeliminatedProperty':
        return type(self)(
            self.fget, self.fset, fdel,
            minimum=self._minimum, maximum=self._maximum,
            step=self._step, unit=self._unit
        )

    @property
    def minimum(self) -> Number:
        return self._safe_call(self._minimum)

    @property
    def maximum(self) -> Number:
        return self._safe_call(self._maximum)

    @property
    def step(self) -> Optional[Number]:
        return self._safe_call(self._step) if self._step is not None else None

    @property
    def unit(self) -> str:
        return self._unit

    # TODO: Determine what the appropriate way to handle this is
    def _adjust_value(self, value: Number) -> Number:
        if self.step:
            value = round(value / self.step) * self.step
        return max(self.minimum, min(self.maximum, value))

    def _safe_call(self, value: StaticOrCallableNumber) -> Number:
        if callable(value):
            if self._instance is None:
                raise ValueError("Cannot evaluate callable without an instance")
            return value(self._instance)
        return value

    def __repr__(self):
        min_repr = self.minimum
        max_repr = self.maximum
        step_repr = self.step if self._step else '_'
        return (
            f"(min={min_repr}, "
            f"max={max_repr}, "
            f"step={step_repr}, "
            f"unit={self.unit})"
        )


class DeliminatedPropertyProxy(DescriptorProxy):
    def __init__(self, value: Number, descriptor: DeliminatedProperty):
        """
        Proxy object for DeliminatedProperty.
        Allows access to the value and descriptor of a DeliminatedProperty.
        If an attribute of the property is accessed, the proxy forwards the call to the descriptor.
        If the value (float or int) is accessed, the proxy forwards the call to the value.
        When the proxy is used in an operation, the operation is forwarded to the value.
        :param value: The value of the property.
        :param descriptor: The descriptor of the property.
        :type value: Number (float or int)
        :type descriptor: DeliminatedProperty
        """
        super().__init__(value, descriptor)

    def __getattr__(self, name):
        return getattr(self._descriptor, name)


def deliminated_property(
        minimum: StaticOrCallableNumber = float('-inf'),
        maximum: StaticOrCallableNumber = float('inf'),
        step: Optional[StaticOrCallableNumber] = None,
        unit: str = ''
) -> Callable[[Callable[[Any], Number]], DeliminatedProperty]:
    def decorator(func: Callable[[Any], Number]) -> DeliminatedProperty:
        return DeliminatedProperty(func, minimum=minimum, maximum=maximum, step=step, unit=unit)

    return decorator


if __name__ == "__main__":
    class Temperature:
        def __init__(self):
            self._value: float = 24
            self.season: Literal['summer', 'winter', 'spring', 'autumn'] = 'summer'

        @deliminated_property(
            minimum=lambda self: self.min_celsius,
            maximum=lambda self: self.max_celsius,
            step=0.1,
            unit='°C'
        )
        def celsius(self) -> float:
            return self._value

        @celsius.setter
        def celsius(self, value: float) -> None:
            self._value = value

        @property
        def max_celsius(self) -> float:
            return 100 if self.season == 'summer' else 75

        @property
        def min_celsius(self) -> float:
            return -10 if self.season == 'winter' else 20


    class Counter:
        def __init__(self):
            self._value: int = 0

        @deliminated_property(
            minimum=0,
            maximum=100,
            step=1,
            unit=''
        )
        def count(self) -> int:
            return self._value

        @count.setter
        def count(self, value) -> None:
            self._value = value


    def print_temperature(t: Temperature):
        print(f"Season is: {t.season}")
        print(f"Celsius step: {t.celsius.step}{t.celsius.unit}")
        print(f"Celsius min: {t.celsius.minimum}{t.celsius.unit}")
        print(f"Celsius max: {t.celsius.maximum}{t.celsius.unit}")
        print(f"Celsius val: {t.celsius}{t.celsius.unit}\n")


    def print_counter(c: Counter):
        print(f"Counter step: {c.count.step}{c.count.unit}")
        print(f"Counter min: {c.count.minimum}{c.count.unit}")
        print(f"Counter max: {c.count.maximum}{c.count.unit}")
        print(f"Counter val: {c.count}{c.count.unit}\n")


    # Test with float (Temperature)
    temp = Temperature()
    print("Initial temperature setting:")
    print_temperature(temp)

    temp.celsius = 30.5
    print("After setting temperature to 30.5°C:")
    print_temperature(temp)

    temp.celsius = 150  # This should be clamped to 100
    print("After attempting to set temperature to 150°C:")
    print_temperature(temp)

    # Test with int (Counter)
    counter = Counter()
    print("Initial counter setting:")
    print_counter(counter)

    counter.count = 50
    print("After setting counter to 50:")
    print_counter(counter)

    counter.count = 150  # This should be clamped to 100
    print("After attempting to set counter to 150:")
    print_counter(counter)

    counter.count = 75.7  # This should be rounded to 76 # type: ignore
    print("After attempting to set counter to 75.7:")
    print_counter(counter)
