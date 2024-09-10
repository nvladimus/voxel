from enum import Enum
from typing import Type, Any, Callable, Optional, Union, List
from weakref import WeakKeyDictionary

from voxel.descriptors.descriptor_proxy import DescriptorProxy
from voxel.utils.logging import get_logger


class EnumeratedProperty:
    def __init__(
            self,
            fget: Optional[Callable[[Any], Enum]] = None,
            fset: Optional[Callable[[Any, Enum], None]] = None,
            fdel: Optional[Callable[[Any], None]] = None,
            *,
            enum_class: Type[Enum],
            options_getter: Optional[Callable[[Any], List]] = None
    ):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self._enum_class = enum_class
        self._options_getter = options_getter
        self._instance_proxies = WeakKeyDictionary()
        self.log = get_logger(f"{self.__class__.__name__}")

    def __get__(self, instance: Any, owner=None) -> Union['EnumeratedProperty', 'EnumeratedPropertyProxy', Enum]:
        if instance is None:
            return self

        if instance not in self._instance_proxies:
            value = self.fget(instance)
            value = self._unwrap_proxy(value)
            self._instance_proxies[instance] = EnumeratedPropertyProxy(value, self)

        return self._instance_proxies[instance]

    def __set__(self, instance: Any, value: Enum) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")

        if not isinstance(value, self._enum_class):
            try:
                value = self._enum_class(value)
            except ValueError:
                self.log.warning(f"Value {value} is not an instance of {self._enum_class.__name__}")
                return

        options = self.get_options(instance)
        if value not in options:
            self.log.warning(f"Invalid option: {value}. Valid options are: {options}")
            return

        self.fset(instance, value)

        if instance in self._instance_proxies:
            value = self._unwrap_proxy(value)
            self._instance_proxies[instance].value = value

    def __delete__(self, instance: Any) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)
        if instance in self._instance_proxies:
            del self._instance_proxies[instance]

    def get_options(self, instance: Any) -> List:
        if self._options_getter is None:
            return [option for option in self._enum_class]
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

    @staticmethod
    def _unwrap_proxy(value: Any):
        if isinstance(value, EnumeratedPropertyProxy):
            return value.value
        return value


class EnumeratedPropertyProxy(DescriptorProxy):
    def __init__(self, value: Enum, descriptor: 'EnumeratedProperty'):
        super().__init__(value, descriptor)

    def __getattribute__(self, name):
        if name == 'options':
            return self._descriptor.get_options(self._descriptor.get_instance_for_proxy(self))
        return super().__getattribute__(name)

    @property
    def options(self) -> List:
        return self._descriptor.get_options(self._instance)


def enumerated_property(
        enum_class: Type[Enum],
        options_getter: Optional[Callable[[Any], List]] = None
) -> Callable[[Callable[[Any], Enum]], EnumeratedProperty]:
    def decorator(func: Callable[[Any], Enum]) -> EnumeratedProperty:
        return EnumeratedProperty(func, enum_class=enum_class, options_getter=options_getter)

    return decorator


def set_ith_option(prop, i: int):
    try:
        prop = prop.options[0][i]
        return prop
    except IndexError:
        return None
