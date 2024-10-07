from enum import Enum
from functools import total_ordering
from typing import Union, Any


@total_ordering
class DescriptorProxy:
    __slots__ = ("value", "_descriptor")

    def __init__(self, value: Union[int, float, Enum], descriptor: Any):
        self.value = value
        self._descriptor = descriptor

    def __getattribute__(self, name):
        if name in DescriptorProxy.__slots__:
            return object.__getattribute__(self, name)
        return object.__getattribute__(object.__getattribute__(self, "value"), name)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        if isinstance(other, DescriptorProxy):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other):
        if isinstance(other, DescriptorProxy):
            return self.value < other.value
        return self.value < other

    def __hash__(self):
        return hash(self.value)

    def __format__(self, format_spec):
        return format(self.value, format_spec)

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __sub__(self, other):
        return self.value - other

    def __rsub__(self, other):
        return other - self.value

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __truediv__(self, other):
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __floordiv__(self, other):
        return self.value // other

    def __rfloordiv__(self, other):
        return other // self.value

    def __mod__(self, other):
        return self.value % other

    def __rmod__(self, other):
        return other % self.value

    def __neg__(self):
        return -self.value

    def __pos__(self):
        return +self.value

    def __abs__(self):
        return abs(self.value)

    def __round__(self, n=None):
        return round(self.value, n)
