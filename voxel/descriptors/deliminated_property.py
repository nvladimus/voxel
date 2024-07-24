from collections.abc import Callable
from typing import Any, Generic, TypeVar, Union, Optional
import logging

T = TypeVar("T", int, float)


class DeliminatedPropertyError(Exception):
    """Custom exception for DeliminatedProperty errors."""


class DeliminatedProperty(property, Generic[T]):
    """
    Property descriptor that allows setting minimum, maximum, and step values for a property.
    Also supports setting a unit for the property.  \n
    If the value is outside the minimum or maximum, it will be adjusted to the closest value.  \n
    If the value is not a multiple of the step, it will be adjusted to the closest lower multiple of the step.  \n
    :param fget: The getter function for the property.
    :param fset: The setter function for the property.
    :param fdel: The deleter function for the property.
    :param doc: The docstring for the property.
    :param minimum: The minimum value for the property.
    :param maximum: The maximum value for the property.
    :param step: The step value for the property.
    :param unit: The unit for the property.
    :raises DeliminatedPropertyError: If the minimum value is greater than the maximum value.
    :raises DeliminatedPropertyError: If the step value is invalid.
    """
    log = logging.getLogger(f'{__name__}.DeliminatedProperty')
    log.setLevel(logging.WARNING)

    if not log.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.propagate = False

    def __init__(
            self,
            fget: Optional[Callable[[Any], T]] = None,
            fset: Optional[Callable[[Any, T], None]] = None,
            fdel: Optional[Callable[[Any], None]] = None,
            doc: Optional[str] = None,
            *,
            minimum: Union[T, Callable[[], T]] = float('-inf'),
            maximum: Union[T, Callable[[], T]] = float('inf'),
            step: Optional[T] = None,
            unit: str = "",
    ) -> None:
        super().__init__(fget, fset, fdel, doc)
        if not callable(minimum) and not callable(maximum) and minimum > maximum:
            raise DeliminatedPropertyError(
                f"Minimum value ({minimum}) cannot be greater than maximum value ({maximum})")
        if step is not None and type(step) not in (int, float, T):
            raise DeliminatedPropertyError(f"Invalid step value: {step}")
        self._minimum = minimum
        self._maximum = maximum
        self.step = step
        self.unit = unit

    @property
    def minimum(self) -> T:
        return self._minimum() if callable(self._minimum) else self._minimum

    @property
    def maximum(self) -> T:
        return self._maximum() if callable(self._maximum) else self._maximum

    def __set__(self, obj: Any, value: T) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        if self.fget is None:
            raise AttributeError("can't get attribute")

        original_value = value

        try:
            maximum = self.maximum
            minimum = self.minimum
        except Exception as e:
            raise DeliminatedPropertyError(f"Error getting minimum/maximum values: {e}")

        if minimum > maximum:
            self.log.error(f"Minimum value ({minimum}) cannot be greater than maximum value ({maximum})")

        # TODO: Is this the expected behavior for step? i.e. Adjusts to closest lower integer multiple of step
        if self.step is not None:
            steps = (value - minimum) // self.step
            value = minimum + (steps * self.step)

        value = min(maximum, max(value, minimum))

        # TODO: Find better way to handle warnings
        if value != original_value:
            self.log.warning(
                f"Value adjustment: "
                f"attr='{obj.__class__.__name__}.{self.fget.__name__}' "
                f"attempting={original_value} adjusted_to={value} "
                f"min={minimum} max={maximum} step={self.step} unit='{self.unit}'"
            )

        self.fset(obj, value)

    def setter(self, fset: Callable[[Any, T], None]) -> "DeliminatedProperty[T]":
        return type(self)(
            self.fget, fset, self.fdel, self.__doc__,
            minimum=self.minimum, maximum=self.maximum, step=self.step, unit=self.unit
        )

    def deleter(self, fdel: Callable[[Any], None]) -> "DeliminatedProperty[T]":
        return type(self)(
            self.fget, self.fset, fdel, self.__doc__,
            minimum=self.minimum, maximum=self.maximum, step=self.step, unit=self.unit
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.fget.__name__})\n"
            f"    minimum: {self.minimum}\n"
            f"    maximum: {self.maximum}\n"
            f"    step:    {self.step}\n"
            f"    unit:    {self.unit}"
        ) if self.fget else super().__repr__()


def deliminated_property(
        minimum: Union[T, Callable[[], T]] = float('-inf'),
        maximum: Union[T, Callable[[], T]] = float('inf'),
        step: Optional[T] = None,
        unit: str = ""
) -> Callable[[Callable[[Any], T]], DeliminatedProperty[T]]:
    """
    Decorator for DeliminatedProperty.  \n
    If the value is outside the minimum or maximum, it will be adjusted to the closest value.  \n
    If the value is not a multiple of the step, it will be adjusted to the closest lower multiple of the step.  \n
    :param minimum: The minimum value for the property.
    :param maximum: The maximum value for the property.
    :param step: The step value for the property.
    :param unit: The unit for the property.
    :type minimum: Union[T, Callable[[Any], T]]
    :type maximum: Union[T, Callable[[Any], T]]
    :type step: Optional[T]
    :type unit: Optional[str]
    :return: The wrapper function for the DeliminatedProperty.
    :rtype: Callable[[Callable[[Any], T]], DeliminatedProperty[T]]
    """
    def wrapper(fget: Callable[[Any], T]) -> DeliminatedProperty[T]:
        return DeliminatedProperty(
            fget,
            minimum=minimum,
            maximum=maximum,
            step=step,
            unit=unit
        )

    return wrapper


# Example usage
if __name__ == "__main__":

    def minimum_temperature(unit: str) -> float:
        if unit == "°C":
            return -273.15
        elif unit == "°F":
            return -459.67
        elif unit == "K":
            return 0.0
        else:
            raise ValueError(f"Unknown unit: {unit}")


    def maximum_temperature(unit: str) -> float:
        if unit == "°C":
            return 1000.0
        elif unit == "°F":
            return 1832.0
        elif unit == "K":
            return 1273.15
        else:
            raise ValueError(f"Unknown unit: {unit}")


    class AdvancedTemperature:
        def __init__(self, initial_celsius: float = 0, significant_digits: int = 2):
            self._celsius = initial_celsius
            self.significant_digits = significant_digits

        @deliminated_property(minimum=-273.15, maximum=1000.0, step=0.01, unit="°C")
        def celsius(self) -> float:
            return round(self._celsius, self.significant_digits)

        @celsius.setter
        def celsius(self, value: float) -> None:
            self._celsius = round(value, self.significant_digits)

        @deliminated_property(
            minimum=lambda: minimum_temperature("°F"),
            maximum=lambda: maximum_temperature("°F"),
            step=0.01,
            unit="°F"
        )
        def fahrenheit(self) -> float:
            return round((self._celsius * 9 / 5) + 32, self.significant_digits)

        @fahrenheit.setter
        def fahrenheit(self, value: float) -> None:
            self._celsius = round((value - 32) * 5 / 9, self.significant_digits)

        @deliminated_property(minimum=0.0, maximum=1273.15, step=0.01, unit="K")
        def kelvin(self) -> float:
            return round(self._celsius + 273.15, self.significant_digits)

        @kelvin.setter
        def kelvin(self, value: float) -> None:
            self._celsius = round(value - 273.15, self.significant_digits)

        def display_all_units(self) -> str:
            return (f"Temperature: "
                    f"{self.celsius:.2f}{self.__class__.celsius.unit}, "
                    f"{self.fahrenheit:.2f}{self.__class__.fahrenheit.unit}, "
                    f"{self.kelvin:.2f}{self.__class__.kelvin.unit}")

        def set_temperature(self, value: float, unit: str) -> None:
            if unit == self.__class__.celsius.unit:
                self.celsius = value
            elif unit == self.__class__.fahrenheit.unit:
                self.fahrenheit = value
            elif unit == self.__class__.kelvin.unit:
                self.kelvin = value
            else:
                raise ValueError(f"Unknown unit: {unit}")


    logging.basicConfig(level=logging.INFO)

    t = AdvancedTemperature(25)  # Initialize with 25°C
    print(f"Initial {t.display_all_units()}")

    t.set_temperature(-300, "°C")  # Will set to -273.15°C and log the adjustment
    print(f"After attempting to set to -300°C: {t.display_all_units()}")

    t.set_temperature(100, "°F")  # Sets Celsius to about 37.78°C
    print(f"After setting to 100°F: {t.display_all_units()}")

    t.set_temperature(0, "K")  # Will set to 0K (-273.15°C) and log the adjustment
    print(f"After attempting to set to 0K: {t.display_all_units()}")

    print(f"{t.__class__.celsius}\n\tValue\t{t.celsius}")

    print(f"Celsius max: {t.__class__.celsius.maximum}")
    print(f"Fahrenheit max: {t.__class__.fahrenheit.maximum}")
