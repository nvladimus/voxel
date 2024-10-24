from typing import Any, Callable, Self

from .annotated import PropertyInfo
from .proxy import DescriptorProxy


type DeliminatedNumber = int | float
type DynamicDeliminatedNumber = DeliminatedNumber | Callable[[Any], DeliminatedNumber]


class DeliminatedPropertyProxy[T](DescriptorProxy[T]):
    @property
    def minimum(self) -> T:
        return self.descriptor.get_minimum(self.instance)

    @property
    def maximum(self) -> T:
        return self.descriptor.get_maximum(self.instance)

    @property
    def step(self) -> T | None:
        return self.descriptor.get_step(self.instance)


class DeliminatedProperty[T: DynamicDeliminatedNumber]:
    def __init__(
        self,
        fget: Callable[[Any], T] | None = None,
        fset: Callable[[Any, T], None] | None = None,
        minimum: DynamicDeliminatedNumber = float("-inf"),
        maximum: DynamicDeliminatedNumber = float("inf"),
        step: DynamicDeliminatedNumber | None = None,
        info: PropertyInfo | None = None,
    ) -> None:
        self.fget = fget
        self.fset = fset
        self.info = info
        self._minimum = minimum
        self._maximum = maximum
        self._step = step

    def get_minimum(self, instance: object) -> T:
        return self._unwrap_dynamic_attribute(self._minimum, instance)

    def get_maximum(self, instance: object) -> T:
        return self._unwrap_dynamic_attribute(self._maximum, instance)

    def get_step(self, instance: object) -> T | None:
        return self._unwrap_dynamic_attribute(self._step, instance)

    def __get__(self, obj, objtype=None) -> Self | DeliminatedPropertyProxy[T]:
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        value = self.fget(obj)
        return DeliminatedPropertyProxy(value, obj, self)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        adjusted_value = self._adjust_value(value, obj)
        if value != adjusted_value and hasattr(obj, "on_property_update_notice"):
            msg: str = (
                f"Value {value} was adjusted to match delineation constraints. "
                f"Min: {self.get_minimum(obj)}, Max: {self.get_maximum(obj)}, "
                f"Step: {self.get_step(obj)}, Value: {adjusted_value}"
            )
            obj.on_property_update_notice(msg)
        self.fset(obj, adjusted_value)

    def __set_name__(self, owner, name) -> None:
        self._name = f"{owner.__name__}.{name}"

    def setter(self, fset) -> Self:
        return type(self)(self.fget, fset, self._minimum, self._maximum, self._step, self.info)

    def _adjust_value(self, value: T, obj: object) -> T:
        minimum = self.get_minimum(obj)
        maximum = self.get_maximum(obj)
        value = max(minimum, min(maximum, value))
        if not self._step:
            return value
        step = self.get_step(obj)
        return round((value - minimum) / step) * step + minimum

    @staticmethod
    def _unwrap_dynamic_attribute(value: T, obj: object) -> T:
        if callable(value):
            return value(obj)
        return value


def deliminated_property(
    minimum: DynamicDeliminatedNumber = float("-inf"),
    maximum: DynamicDeliminatedNumber = float("inf"),
    step: DynamicDeliminatedNumber | None = None,
    unit: str | None = None,
    description: str | None = None,
) -> Callable[..., DeliminatedProperty]:
    def decorator(func) -> DeliminatedProperty:
        info = PropertyInfo(unit=unit, description=description)
        return DeliminatedProperty(fget=func, minimum=minimum, maximum=maximum, step=step, info=info)

    return decorator
