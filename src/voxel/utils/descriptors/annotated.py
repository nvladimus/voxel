from dataclasses import dataclass
from typing import Any, Callable, Self

from .proxy import DescriptorProxy


@dataclass
class PropertyInfo:
    unit: str | None
    description: str | None


class AnnotatedPropertyProxy[T](DescriptorProxy[T]):
    @property
    def info(self) -> PropertyInfo:
        return self.descriptor.info


class AnnotatedProperty[T]:
    def __init__(
        self,
        fget: Callable[[Any], T] | None = None,
        fset: Callable[[Any, T], None] | None = None,
        info: PropertyInfo | None = None,
    ) -> None:
        self.fget = fget
        self.fset = fset
        self.info = info

    def __get__(self, obj, objtype=None) -> Self | T:
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        value = self.fget(obj)
        return value
        # return AnnotatedPropertyProxy(value, obj, self)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def setter(self, fset) -> Self:
        return type(self)(self.fget, fset, self.info)


def annotated_property(unit: str, description: str) -> Callable[..., AnnotatedProperty]:
    def decorator(func) -> AnnotatedProperty:
        return AnnotatedProperty(fget=func, info=PropertyInfo(unit, description))

    return decorator
