import logging
from typing import Union, Callable, Optional, Any, Literal, TypeVar, Generic

logging.basicConfig(level=logging.DEBUG)

T = TypeVar('T', int, float)

class DeliminatedProperty(Generic[T], property):
    def __init__(
            self,
            fget: Optional[Callable[[Any], T]] = None,
            fset: Optional[Callable[[Any, T], None]] = None,
            fdel: Optional[Callable[[Any], None]] = None,
            *,
            minimum: Union[T, Callable[[Any], T]] = float('-inf'),
            maximum: Union[T, Callable[[Any], T]] = float('inf'),
            step: Optional[Union[T, Callable[[Any], T]]] = None,
            unit: str = ''
    ):
        super().__init__(fget, fset, fdel)
        self._minimum = minimum
        self._maximum = maximum
        self._step = step
        self._unit = unit
        self._instance: Any = None

        self.log = logging.getLogger(f"{__name__} - {self.__class__.__name__}")

    def __get__(self, instance: Any, owner=None) -> Union['DeliminatedProperty[T]', 'DeliminatedPropertyProxy[T]']:
        if instance is None:
            return self

        self._instance = instance

        if self.fget is None:
            raise AttributeError("unreadable attribute")

        value = self.fget(instance)
        return DeliminatedPropertyProxy(value, self)

    def __set__(self, instance: Any, value: T) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self._instance = instance
        original_value = value
        value = self._clamp(value)
        if self.step is not None:
            value = self._get_closest_step_multiple(value)
        if value != original_value:
            self.log.warning(f"Value {original_value} was adjusted to {value}\n\t{self}")
        self.fset(instance, value)

    def __delete__(self, instance: Any) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def getter(self, fget: Callable[[Any], T]) -> 'DeliminatedProperty[T]':
        return type(self)(
            fget, self.fset, self.fdel,
            minimum=self._minimum, maximum=self._maximum,
            step=self._step, unit=self._unit
        )

    def setter(self, fset: Callable[[Any, T], None]) -> 'DeliminatedProperty[T]':
        return type(self)(
            self.fget, fset, self.fdel,
            minimum=self._minimum, maximum=self._maximum,
            step=self._step, unit=self._unit
        )

    def deleter(self, fdel: Callable[[Any], None]) -> 'DeliminatedProperty[T]':
        return type(self)(
            self.fget, self.fset, fdel,
            minimum=self._minimum, maximum=self._maximum,
            step=self._step, unit=self._unit
        )

    @property
    def minimum(self) -> T:
        return self._safe_call(self._minimum)

    @property
    def maximum(self) -> T:
        return self._safe_call(self._maximum)

    @property
    def step(self) -> Optional[T]:
        return self._safe_call(self._step) if self._step is not None else None

    @property
    def unit(self) -> str:
        return self._unit

    def _get_closest_step_multiple(self, value: T) -> T:
        step = self.step
        if step is None:
            return value
        min_val = self.minimum
        max_val = self.maximum
        if isinstance(value, int) and isinstance(step, int) and isinstance(min_val, int):
            return int(round((value - min_val) / step) * step + min_val)
        return round((value - min_val) / step) * step + min_val

    def _clamp(self, value: T) -> T:
        max_val = self.maximum
        min_val = self.minimum
        step = self.step
        if step is not None and value > max_val:
            return (max_val - min_val) // step * step + min_val
        else:
            return max(min_val, min(value, max_val))


    def _safe_call(self, value: Union[T, Callable[[Any], T]]) -> T:
        if callable(value):
            if self._instance is None:
                raise ValueError("Cannot evaluate callable without an instance")
            return value(self._instance)
        return value

    def __repr__(self):
        min_repr = "callable" if callable(self._minimum) else self._minimum
        max_repr = "callable" if callable(self._maximum) else self._maximum
        step_repr = "callable" if callable(self._step) else self._step
        return (
            f"{self.__class__.__name__}"
            f"(minimum={min_repr}, "
            f"maximum={max_repr}, "
            f"step={step_repr}, "
            f"unit={self.unit})"
        )


class DeliminatedPropertyProxy(Generic[T]):
    def __init__(self, value: T, descriptor: DeliminatedProperty[T]):
        self._value = value
        self._descriptor = descriptor

    def __repr__(self):
        return repr(self._value)

    def __float__(self):
        return float(self._value)

    def __int__(self):
        return int(self._value)

    def __getattr__(self, name):
        return getattr(self._descriptor, name)

    # Forwarding operations to the underlying float value
    def __eq__(self, other):
        return self._value == other

    def __lt__(self, other):
        return self._value < other

    def __le__(self, other):
        return self._value <= other

    def __gt__(self, other):
        return self._value > other

    def __ge__(self, other):
        return self._value >= other

    def __add__(self, other):
        return self._value + other

    def __radd__(self, other):
        return other + self._value

    def __sub__(self, other):
        return self._value - other

    def __rsub__(self, other):
        return other - self._value

    def __mul__(self, other):
        return self._value * other

    def __rmul__(self, other):
        return other * self._value

    def __truediv__(self, other):
        return self._value / other

    def __rtruediv__(self, other):
        return other / self._value

    def __floordiv__(self, other):
        return self._value // other

    def __rfloordiv__(self, other):
        return other // self._value

    def __mod__(self, other):
        return self._value % other

    def __rmod__(self, other):
        return other % self._value


def deliminated_property(
        minimum: Union[T, Callable[[Any], T]] = float('-inf'),
        maximum: Union[T, Callable[[Any], T]] = float('inf'),
        step: Optional[Union[T, Callable[[Any], T]]] = None,
        unit: str = ''
) -> Callable[[Callable[[Any], T]], DeliminatedProperty[T]]:
    def decorator(func: Callable[[Any], T]) -> DeliminatedProperty[T]:
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
        def count(self, value: int) -> None:
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
