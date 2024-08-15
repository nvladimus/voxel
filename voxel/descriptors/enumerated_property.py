from enum import Enum
from functools import total_ordering
from typing import Type, Dict, Any, Callable, Optional, Union
from weakref import WeakKeyDictionary


class EnumeratedProperty:
    def __init__(
            self,
            fget: Optional[Callable[[Any], Enum]] = None,
            fset: Optional[Callable[[Any, Enum], None]] = None,
            fdel: Optional[Callable[[Any], None]] = None,
            *,
            enum_class: Type[Enum],
            options_getter: Optional[Callable[[Any], Dict[Enum, Any]]] = None
    ):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self._enum_class = enum_class
        self._options_getter = options_getter
        self._instance_proxies = WeakKeyDictionary()

    def __get__(self, instance: Any, owner=None) -> Union['EnumeratedProperty', 'EnumeratedPropertyProxy']:
        if instance is None:
            return self

        if instance not in self._instance_proxies:
            value = self.fget(instance)
            self._instance_proxies[instance] = EnumeratedPropertyProxy(value, self)

        return self._instance_proxies[instance]

    def __set__(self, instance: Any, value: Enum) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")

        if not isinstance(value, self._enum_class):
            try:
                value = self._enum_class(value)
            except ValueError:
                raise ValueError(f"Value must be an instance of {self._enum_class.__name__}")

        options = self.get_options(instance)
        if value not in options:
            raise ValueError(f"Invalid option: {value}. Valid options are: {list(options.keys())}")

        self.fset(instance, value)

        if instance in self._instance_proxies:
            self._instance_proxies[instance]._value = value

    def __delete__(self, instance: Any) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)
        if instance in self._instance_proxies:
            del self._instance_proxies[instance]

    def get_options(self, instance: Any) -> Dict[Enum, Any]:
        if self._options_getter is None:
            return {e: e.value for e in self._enum_class}
        return self._options_getter(instance)

    def get_instance_for_proxy(self, proxy: 'EnumeratedPropertyProxy') -> Any:
        for instance, stored_proxy in self._instance_proxies.items():
            if stored_proxy is proxy:
                return instance
        raise ValueError("Proxy not associated with any known instance")

    def setter(self, fset: Callable[[Any, Enum], None]) -> 'EnumeratedProperty':
        return type(self)(
            self.fget, fset, self.fdel,
            enum_class=self._enum_class,
            options_getter=self._options_getter
        )

    def deleter(self, fdel: Callable[[Any], None]) -> 'EnumeratedProperty':
        return type(self)(
            self.fget, self.fset, fdel,
            enum_class=self._enum_class,
            options_getter=self._options_getter
        )


@total_ordering
class EnumeratedPropertyProxy:
    __slots__ = ('_value', '_descriptor')

    def __init__(self, value: Enum, descriptor: 'EnumeratedProperty'):
        self._value = value
        self._descriptor = descriptor

    def __getattribute__(self, name):
        if name in EnumeratedPropertyProxy.__slots__:
            return object.__getattribute__(self, name)
        if name == 'options':
            return object.__getattribute__(self, '_get_options')()
        return getattr(object.__getattribute__(self, '_value'), name)

    def _get_options(self) -> Dict[Enum, Any]:
        instance = self._descriptor.get_instance_for_proxy(self)
        return self._descriptor.get_options(instance)

    def __repr__(self):
        return repr(self._value)

    def __str__(self):
        return str(self._value)

    def __int__(self):
        return int(self._value.value)

    def __float__(self):
        return float(self._value.value)

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return self._value.value == other
        return self._value == other

    def __lt__(self, other):
        if isinstance(other, (int, float)):
            return self._value.value < other
        return self._value.value < getattr(other, 'value', other)

    def __add__(self, other):
        return self._value.value + other

    def __radd__(self, other):
        return other + self._value.value

    def __sub__(self, other):
        return self._value.value - other

    def __rsub__(self, other):
        return other - self._value.value

    def __mul__(self, other):
        return self._value.value * other

    def __rmul__(self, other):
        return other * self._value.value

    def __truediv__(self, other):
        return self._value.value / other

    def __rtruediv__(self, other):
        return other / self._value.value

    def __floordiv__(self, other):
        return self._value.value // other

    def __rfloordiv__(self, other):
        return other // self._value.value

    def __mod__(self, other):
        return self._value.value % other

    def __rmod__(self, other):
        return other % self._value.value


def enumerated_property(
        enum_class: Type[Enum],
        options_getter: Optional[Callable[[Any], Dict[Enum, Any]]] = None
) -> Callable[[Callable[[Any], Enum]], EnumeratedProperty]:
    def decorator(func: Callable[[Any], Enum]) -> EnumeratedProperty:
        return EnumeratedProperty(func, enum_class=enum_class, options_getter=options_getter)

    return decorator
