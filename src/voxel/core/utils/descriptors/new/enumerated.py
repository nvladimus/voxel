from enum import IntEnum, StrEnum
from typing import Any, Callable, Self

from voxel.core.utils.descriptors.new.annotated import PropertyInfo
from voxel.core.utils.descriptors.new.proxy import DescriptorProxy


type PropertyOptions = set[str] | set[int] | set[float]
type DynamicOptions = PropertyOptions | Callable[[object], PropertyOptions]

type EnumerationClass = type[StrEnum] | type[IntEnum]


class EnumeratedPropertyProxy[T](DescriptorProxy[T]):
    @property
    def options(self) -> PropertyOptions:
        return self.descriptor.get_options(self.instance)


class EnumeratedProperty[T: str | int | float]:

    def __init__(
        self,
        options: DynamicOptions | type[StrEnum] | type[IntEnum],
        fget: Callable[[Any], Any] | None = None,
        fset: Callable[[Any, Any], None] | None = None,
        info: PropertyInfo | None = None,
    ) -> None:
        self.fget = fget
        self.fset = fset
        self.info = info
        self._name = ""
        if isinstance(options, type) and issubclass(options, (StrEnum, IntEnum)):
            options = set(e.value for e in options)
        self._options = options

    def __get__(self, obj, objtype=None) -> Self | EnumeratedPropertyProxy[T]:
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        value = self.fget(obj)
        return EnumeratedPropertyProxy(value, obj, self)

    def __set__(self, obj, value) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        static_options = self.get_options(obj)
        if value not in static_options and hasattr(obj, "on_property_update_notice"):
            msg: str = f"Invalid option: {value}. Valid options are: {static_options}"
            obj.on_property_update_notice(msg=msg, prop=self._name)
            return
        self.fset(obj, value)

    def __set_name__(self, owner, name) -> None:
        self._name = f"{owner.__name__}.{name}"

    def setter(self, fset) -> Self:
        return type(self)(self._options, self.fget, fset, self.info)

    def get_options(self, obj) -> PropertyOptions:
        if callable(self._options):
            return self._options(obj)
        else:
            return self._options


def enumerated_property(
    options: DynamicOptions | StrEnum | IntEnum, info: PropertyInfo
) -> Callable[..., EnumeratedProperty]:
    def decorator(func) -> EnumeratedProperty:
        return EnumeratedProperty(options, fget=func, info=info)

    return decorator
