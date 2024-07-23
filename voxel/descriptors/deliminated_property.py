from typing import Optional, Union, Callable, Any
import logging


class DeliminatedProperty(property):
    """
    A property descriptor that enforces minimum, maximum, and step constraints on values.
    It inherits from the built-in property class and adds additional functionality.
    """

    # Class-level logger
    log = logging.getLogger(f'{__name__}.DeliminatedProperty')
    log.setLevel(logging.WARNING)

    if not log.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.propagate = False  # Prevent double logging

    def __init__(
            self,
            fget: Optional[Callable] = None,
            fset: Optional[Callable] = None,
            fdel: Optional[Callable] = None,
            doc: Optional[str] = None,
            minimum: Union[int, float, Callable] = float('-inf'),
            maximum: Union[int, float, Callable] = float('inf'),
            step: Optional[Union[int, float]] = None,
            unit: Optional[str] = None,
    ):
        """
        Initialize the DeliminatedProperty.

        :param fget: Getter function
        :param fset: Setter function
        :param fdel: Deleter function
        :param doc: Docstring
        :param minimum: Minimum allowed value or a callable that returns the minimum
        :param maximum: Maximum allowed value or a callable that returns the maximum
        :param step: Step size for value quantization
        :param unit: Unit of measurement (for documentation purposes)
        """
        super().__init__(fget, fset, fdel, doc)
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.unit: str = unit if unit else ""

    def __set__(self, obj: Any, value: Any) -> None:
        """
        Set the property value, applying constraints and logging if necessary.

        :param obj: The instance that the property belongs to
        :param value: The value to set
        :raises AttributeError: If the property can't be set
        """
        if self.fset is None:
            raise AttributeError("can't set attribute")

        original_value = value

        if self.step is not None:
            value = round(value / self.step) * self.step

        maximum = self.maximum(obj) if callable(self.maximum) else self.maximum
        minimum = self.minimum(obj) if callable(self.minimum) else self.minimum

        value = min(maximum, max(value, minimum))

        if value != original_value:
            self.log.warning(
                f"Value adjustment: "
                f"attr='{obj.__class__.__name__}.{self.fget.__name__}' "
                f"attempting={original_value} adjusted_to={value} "
                f"min={round(minimum, 4)} max={round(maximum, 4)} step={self.step} unit='{self.unit}'"
            )

        self.fset(obj, value)

    def getter(self, fget: Callable) -> 'DeliminatedProperty':
        """
        Descriptor to obtain a copy of the property with a different getter.

        :param fget: The new getter function
        :return: A new DeliminatedProperty instance with the updated getter
        """
        return type(self)(fget, self.fset, self.fdel, self.__doc__,
                          self.minimum, self.maximum, self.step, self.unit)

    def setter(self, fset: Callable) -> 'DeliminatedProperty':
        """
        Descriptor to obtain a copy of the property with a different setter.

        :param fset: The new setter function
        :return: A new DeliminatedProperty instance with the updated setter
        """
        return type(self)(self.fget, fset, self.fdel, self.__doc__,
                          self.minimum, self.maximum, self.step, self.unit)

    def deleter(self, fdel: Callable) -> 'DeliminatedProperty':
        """
        Descriptor to obtain a copy of the property with a different deleter.

        :param fdel: The new deleter function
        :return: A new DeliminatedProperty instance with the updated deleter
        """
        return type(self)(self.fget, self.fset, fdel, self.__doc__,
                          self.minimum, self.maximum, self.step, self.unit)


def deliminated_property(
        minimum: Union[int, float, Callable] = float('-inf'),
        maximum: Union[int, float, Callable] = float('inf'),
        step: Optional[Union[int, float]] = None,
        unit: Optional[str] = None,
):
    """
    Decorator factory for creating DeliminatedProperty instances.

    :param minimum: Minimum allowed value or a callable that returns the minimum
    :param maximum: Maximum allowed value or a callable that returns the maximum
    :param step: Step size for value quantization
    :param unit: Unit of measurement (for documentation purposes)
    :return: A decorator that creates a DeliminatedProperty
    """

    def wrapper(fget: Callable) -> DeliminatedProperty:
        return DeliminatedProperty(fget, minimum=minimum, maximum=maximum, step=step, unit=unit)

    return wrapper


# Example usage
if __name__ == "__main__":

    class AdvancedTemperature:
        def __init__(self, initial_celsius=0):
            self._celsius = initial_celsius

        @deliminated_property(minimum=-273.15, maximum=1000, step=0.01, unit="°C")
        def celsius(self) -> float:
            return self._celsius

        @celsius.setter
        def celsius(self, value):
            self._celsius = value

        @deliminated_property(minimum=-459.67, maximum=1832, step=0.018, unit="°F")
        def fahrenheit(self):
            return (self._celsius * 9 / 5) + 32

        @fahrenheit.setter
        def fahrenheit(self, value):
            self._celsius = (value - 32) * 5 / 9

        @deliminated_property(minimum=0, maximum=1273.15, step=0.01, unit="K")
        def kelvin(self):
            return self._celsius + 273.15

        @kelvin.setter
        def kelvin(self, value):
            self._celsius = value - 273.15

        @deliminated_property(
            minimum=lambda self: round(self.celsius + 10, 2),
            maximum=lambda self: round(self.celsius + 50, 2),
            step=0.1,
            unit="°C"
        )
        def comfortable_range(self):
            return self._celsius + 20

        @comfortable_range.setter
        def comfortable_range(self, value):
            self._celsius = value - 20

        def display_all_units(self):
            return (f"Temperature: "
                    f"{self.celsius:.2f}{self.__class__.celsius.unit}, "
                    f"{self.fahrenheit:.2f}{self.__class__.fahrenheit.unit}, "
                    f"{self.kelvin:.2f}{self.__class__.kelvin.unit}")

        def set_temperature(self, value: float, unit: str):
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

    t.set_temperature(-300, "°C")  # Will set to -273.15°C (absolute zero) and log the adjustment
    print(f"After attempting to set to -300°C: {t.display_all_units()}")

    t.set_temperature(100, "°F")  # Sets Celsius to about 37.78°C
    print(f"After setting to 100°F: {t.display_all_units()}")

    t.set_temperature(0, "K")  # Will set to 0K (-273.15°C) and log the adjustment
    print(f"After attempting to set to 0K: {t.display_all_units()}")

    print(f"Comfortable range: {t.comfortable_range:.2f}{t.__class__.comfortable_range.unit}")
    t.comfortable_range = 30  # This will adjust the base temperature
    print(f"After setting comfortable range to 30°C: {t.celsius:.2f} {t.__class__.celsius.unit}, "
          f"Comfortable range: {t.comfortable_range:.2f}{t.__class__.comfortable_range.unit}")

    t.comfortable_range = 0  # This will be adjusted to the minimum (t.celsius + 10)
    print(f"After attempting to set comfortable range to 0°C: {t.celsius:.2f} {t.__class__.celsius.unit}, "
          f"Comfortable range: {t.comfortable_range:.2f} {t.__class__.comfortable_range.unit}")
