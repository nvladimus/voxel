from enum import Enum
from functools import total_ordering
from typing import Union, Any


@total_ordering
class DescriptorProxy:
    __slots__ = ('_value', '_descriptor')

    def __init__(self, value: Union[int, float, Enum], descriptor: Any):
        self._value = value
        self._descriptor = descriptor

    def __getattribute__(self, name):
        if name in DescriptorProxy.__slots__:
            return object.__getattribute__(self, name)
        return getattr(object.__getattribute__(self, '_value'), name)

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return repr(self._value)

    def __eq__(self, other):
        return self._value == other

    def __lt__(self, other):
        return self._value < other

    def __hash__(self):
        return hash(self._value)

    # def __eq__(self, other):
    #     return self._value == other
    #
    # def __lt__(self, other):
    #     return self._value < other
    #
    # def __le__(self, other):
    #     return self._value <= other
    #
    # def __gt__(self, other):
    #     return self._value > other
    #
    # def __ge__(self, other):
    #     return self._value >= other

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

    def __neg__(self):
        return -self._value

    def __pos__(self):
        return +self._value

    def __abs__(self):
        return abs(self._value)
