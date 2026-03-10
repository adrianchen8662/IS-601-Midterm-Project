from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List

from app.exceptions import ValidationError

# Registry shared by OperationFactory and the register_op decorator
_registry: Dict[str, type] = {}


def register_op(
    name: str,
    *,
    symbol: str = '',
    description: str = '',
    example: str = '',
    is_keyword: bool = False,
    is_infix: bool = False,
):
    """Class decorator that registers an Operation subclass and attaches help metadata"""
    def decorator(cls):
        cls.name = name
        cls.symbol = symbol
        cls.description = description
        cls.example = example
        cls.is_keyword = is_keyword
        cls.is_infix = is_infix
        _registry[name] = cls
        return cls
    return decorator


class Operation(ABC):
    """Abstract base for all arithmetic operations"""

    name: str = ''
    symbol: str = ''
    description: str = ''
    example: str = ''
    is_keyword: bool = False
    is_infix: bool = False

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        pass  # pragma: no cover

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """Override in subclasses to enforce operation-specific rules"""
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


@register_op('add',
             symbol='+',
             description='Add two numbers',
             example='1 + 2',
             is_infix=True)
class Addition(Operation):

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a + b


@register_op('subtract',
             symbol='-',
             description='Subtract b from a',
             example='5 - 3',
             is_infix=True)
class Subtraction(Operation):

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a - b


@register_op('multiply',
             symbol='*',
             description='Multiply two numbers',
             example='3 * 4',
             is_infix=True)
class Multiplication(Operation):

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a * b


@register_op('divide',
             symbol='/',
             description='Divide a by b',
             example='10 / 2',
             is_infix=True)
class Division(Operation):

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a / b


@register_op('power',
             description='Raise a to the power b',
             example='power 2 8',
             is_keyword=True)
class Power(Operation):

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b < 0:
            raise ValidationError("Negative exponents not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), float(b)))


@register_op('root',
             description='Compute the bth root of a',
             example='root 27 3',
             is_keyword=True)
class Root(Operation):

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))


@register_op('modulus',
             symbol='%',
             description='Remainder of a / b',
             example='modulus 10 3',
             is_keyword=True,
             is_infix=True)
class Modulus(Operation):

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Modulus by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a % b


@register_op('intdiv',
             symbol='//',
             description='Integer quotient of a // b',
             example='intdiv 10 3',
             is_keyword=True,
             is_infix=True)
class IntegerDivision(Operation):

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Integer division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(int(a // b))


@register_op('percentage',
             description='(a / b) x 100',
             example='percentage 25 200',
             is_keyword=True)
class Percentage(Operation):
    """(a / b) * 100"""

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Cannot calculate percentage with zero denominator")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(str(a / b)) * Decimal('100')


@register_op('absdiff',
             description='|a - b|',
             example='absdiff 9 4',
             is_keyword=True)
class AbsoluteDifference(Operation):
    """Absolute difference between two numbers"""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return abs(a - b)


class OperationFactory:
    """Creates Operation instances by name"""

    # Shares the registry so register_op and register_operation, both write to the same dict
    _operations: Dict[str, type] = _registry

    @classmethod
    def help_entries(cls) -> List[dict]:
        """Return help metadata for every registered keyword operation"""
        return [
            {
                'name': op.name,
                'description': op.description,
                'example': op.example,
            }
            for op in cls._operations.values()
            if getattr(op, 'is_keyword', False)
        ]

    @classmethod
    def infix_entries(cls) -> List[dict]:
        """Return help metadata for every registered infix operation"""
        return [
            {
                'symbol': op.symbol,
                'description': op.description,
                'example': op.example,
            }
            for op in cls._operations.values()
            if getattr(op, 'is_infix', False)
        ]

    @classmethod
    def keyword_op_names(cls) -> frozenset:
        """Return a frozenset of the names of all registered keyword operations"""
        return frozenset(
            name
            for name, op in cls._operations.items()
            if getattr(op, 'is_keyword', False)
        )

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        """Register a new operation type. Raises TypeError if not an Operation subclass"""
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """Return an Operation instance for the given type name. Raises ValueError if unknown"""
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()
