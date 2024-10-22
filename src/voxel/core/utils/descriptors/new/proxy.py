from functools import total_ordering
from typing import Any


@total_ordering
class DescriptorProxy[T]:
    __slots__ = ("value", "descriptor", "instance")

    def __init__(self, value: T, instance: Any, descriptor: Any) -> None:
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "descriptor", descriptor)
        object.__setattr__(self, "instance", instance)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            try:
                return getattr(self.descriptor, name)
            except AttributeError:
                return getattr(self.value, name)

    def __setattr__(self, name, value):
        if name in DescriptorProxy.__slots__:
            object.__setattr__(self, name, value)
        else:
            setattr(self._value, name, value)

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)

    def __eq__(self, other) -> bool:
        if isinstance(other, DescriptorProxy):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other) -> bool:
        if isinstance(other, DescriptorProxy):
            return self.value < other.value
        return self.value < other

    def __hash__(self) -> int:
        return hash(self.value)

    def __format__(self, format_spec) -> str:
        return format(self.value, format_spec)

    def __add__(self, other: T) -> T:
        return self.value + other

    def __radd__(self, other: T) -> T:
        return other + self.value

    def __sub__(self, other: T) -> T:
        return self.value - other

    def __rsub__(self, other: T) -> T:
        return other - self.value

    def __mul__(self, other: T) -> T:
        return self.value * other

    def __rmul__(self, other: T) -> T:
        return other * self.value

    def __truediv__(self, other: T) -> T:
        return self.value / other

    def __rtruediv__(self, other: T) -> T:
        return other / self.value

    def __floordiv__(self, other: T) -> T:
        return self.value // other

    def __rfloordiv__(self, other: T) -> T:
        return other // self.value

    def __mod__(self, other: T) -> T:
        return self.value % other

    def __rmod__(self, other: T) -> T:
        return other % self.value

    def __neg__(self):
        return -self.value

    def __pos__(self):
        return +self.value

    def __abs__(self) -> T:
        return abs(self.value)

    def __round__(self, n=None) -> T:
        return round(self.value, n)
