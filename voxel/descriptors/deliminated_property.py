from typing import Union, Callable, Optional, Any

from voxel.descriptors.descriptor_proxy import DescriptorProxy
from voxel.utils.logging import get_logger

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

        self.log = get_logger(f"{self.__class__.__name__}")

    def __get__(self, instance: Any, owner=None) -> Union['DeliminatedProperty', 'DeliminatedPropertyProxy']:
        if instance is None:
            return self

        self._instance = instance

        if self.fget is None:
            raise AttributeError("unreadable attribute")

        value = self.fget(instance)
        value = self._unwrap_proxy(value)
        return DeliminatedPropertyProxy(value, self)

    def __set__(self, instance: Any, value: Number) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self._instance = instance
        value = self._unwrap_proxy(value)
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

    @staticmethod
    def _unwrap_proxy(value: Any):
        if isinstance(value, DeliminatedPropertyProxy):
            return value.value
        return value


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

    def __getattribute__(self, item):
        """
        Overrides the default __getattribute__ method to allow access to the descriptor's attributes.
        :param item: The attribute to access.
        :type item: str
        :return: The attribute of the descriptor or the default __getattribute__ method.
        """
        if item in ['minimum', 'maximum', 'step', 'unit']:
            return self._descriptor.__getattribute__(item)
        return super().__getattribute__(item)

    @property
    def maximum(self) -> Number:
        return self._descriptor.maximum

    @property
    def minimum(self) -> Number:
        return self._descriptor.minimum

    @property
    def step(self) -> Optional[Number]:
        return self._descriptor.step

    @property
    def unit(self) -> str:
        return self._descriptor.unit

    def dict(self):
        return {
            "value": self.value,
            "minimum": self._descriptor.minimum,
            "maximum": self._descriptor.maximum,
            "step": self._descriptor.step,
            "unit": self._descriptor.unit
        }


def deliminated_property(
        minimum: StaticOrCallableNumber = float('-inf'),
        maximum: StaticOrCallableNumber = float('inf'),
        step: Optional[StaticOrCallableNumber] = None,
        unit: str = ''
) -> Callable[[Callable[[Any], Number]], DeliminatedProperty]:
    def decorator(func: Callable[[Any], Number]) -> DeliminatedProperty:
        return DeliminatedProperty(func, minimum=minimum, maximum=maximum, step=step, unit=unit)

    return decorator
