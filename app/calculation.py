from abc import ABC, abstractmethod
import datetime

from app.operations import (
    Addition, Subtraction, Multiplication, Division,
    Power, Root, Modulus, IntegerDivision, Percentage, AbsoluteDifference,
)

class Calculation(ABC):
    """Abstract base for all calculator calculations."""

    def __init__(self, a: float, b: float) -> None:
        self.a: float = a
        self.b: float = b
        self.timestamp: datetime.datetime = datetime.datetime.now()

    @abstractmethod
    def execute(self) -> float:
        pass  # pragma: no cover

    def __str__(self) -> str:
        result = self.execute()
        operation_name = self.__class__.__name__.replace('Calculation', '')
        return f"{self.__class__.__name__}: {self.a} {operation_name} {self.b} = {result}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(a={self.a}, b={self.b})"

    @property
    def operation(self) -> str:
        return self.__class__.__name__.replace('Calculation', '').lower()

    @property
    def operand1(self) -> float:
        return self.a

    @property
    def operand2(self) -> float:
        return self.b

    @property
    def result(self) -> float:
        return self.execute()

    def to_dict(self) -> dict:
        return {
            'operation': self.operation,
            'operand1': self.a,
            'operand2': self.b,
            'result': self.result,
            'timestamp': self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Calculation':
        calc = CalculationFactory.create_calculation(
            data['operation'],
            float(data['operand1']),
            float(data['operand2']),
        )
        if data.get('timestamp'):
            try:
                calc.timestamp = datetime.datetime.fromisoformat(str(data['timestamp']))
            except (ValueError, TypeError):
                pass
        return calc

class CalculationFactory:
    """Creates Calculation instances by registered type string."""

    _calculations = {}

    @classmethod
    def register_calculation(cls, calculation_type: str):
        def decorator(subclass):
            calculation_type_lower = calculation_type.lower()
            if calculation_type_lower in cls._calculations:
                raise ValueError(f"Calculation type '{calculation_type}' is already registered.")
            cls._calculations[calculation_type_lower] = subclass
            return subclass
        return decorator

    @classmethod
    def create_calculation(cls, calculation_type: str, a: float, b: float) -> Calculation:
        calculation_type_lower = calculation_type.lower()
        calculation_class = cls._calculations.get(calculation_type_lower)
        if not calculation_class:
            available_types = ', '.join(cls._calculations.keys())
            raise ValueError(
                f"Unsupported calculation type: '{calculation_type}'. "
                f"Available types: {available_types}"
            )
        return calculation_class(a, b)

@CalculationFactory.register_calculation('add')
class AddCalculation(Calculation):
    """Addition of two numbers."""

    def execute(self) -> float:
        return float(Addition().execute(self.a, self.b))


@CalculationFactory.register_calculation('subtract')
class SubtractCalculation(Calculation):
    """Subtraction of two numbers."""

    def execute(self) -> float:
        return float(Subtraction().execute(self.a, self.b))

@CalculationFactory.register_calculation('multiply')
class MultiplyCalculation(Calculation):
    """Multiplication of two numbers."""

    def execute(self) -> float:
        return float(Multiplication().execute(self.a, self.b))

@CalculationFactory.register_calculation('divide')
class DivideCalculation(Calculation):
    """Division of two numbers. Raises ValidationError for zero divisor."""

    def execute(self) -> float:
        return float(Division().execute(self.a, self.b))

@CalculationFactory.register_calculation('power')
class PowerCalculation(Calculation):
    """Raises a to the power of b. Requires non-negative exponent."""

    def execute(self) -> float:
        return float(Power().execute(self.a, self.b))

@CalculationFactory.register_calculation('root')
class RootCalculation(Calculation):
    """Computes the bth root of a. Requires non-negative base and non-zero degree."""

    def execute(self) -> float:
        return float(Root().execute(self.a, self.b))

@CalculationFactory.register_calculation('modulus')
class ModulusCalculation(Calculation):
    """Remainder of a divided by b. Raises ValidationError for zero divisor."""

    def execute(self) -> float:
        return float(Modulus().execute(self.a, self.b))

@CalculationFactory.register_calculation('intdiv')
class IntegerDivisionCalculation(Calculation):
    """Integer quotient of a divided by b, discarding any fractional part."""

    def execute(self) -> float:
        return float(IntegerDivision().execute(self.a, self.b))

@CalculationFactory.register_calculation('percentage')
class PercentageCalculation(Calculation):
    """Computes (a / b) * 100. Raises ValidationError for zero denominator."""

    def execute(self) -> float:
        return float(Percentage().execute(self.a, self.b))

@CalculationFactory.register_calculation('absdiff')
class AbsoluteDifferenceCalculation(Calculation):
    """Computes the absolute difference |a - b|."""

    def execute(self) -> float:
        return float(AbsoluteDifference().execute(self.a, self.b))