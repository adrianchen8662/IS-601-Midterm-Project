import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Optional
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError
from app.operations import OperationFactory

# Matches either a full expression "a op b" or a continuation "op b".
# Group layout:
#   Full:         (1) a   (2) op   (3) b
#   Continuation: (4) op  (5) b
EXPRESSION_PATTERN = re.compile(
    r'([+-]?\s*\d+(?:\.\d+)?)\s*(//|[+\-*/%])\s*([+-]?\s*\d+(?:\.\d+)?)'
    r'|'
    r'(//|[+\-*/%])\s*([+-]?\s*\d+(?:\.\d+)?)'
)

KEYWORD_OPS = OperationFactory.keyword_op_names()

@dataclass
class InputValidator:
    """Validates and sanitizes calculator inputs."""

    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig, previous_result: Optional[Decimal] = None) -> Decimal:
        """
        Convert input to Decimal. Accepts ``"ans"`` (lowercase) as a stand-in for
        *previous_result*. Raises ValidationError for invalid input
        """
        try:
            if isinstance(value, str):
                value = value.strip()
                if value == 'ans':
                    if previous_result is None:
                        raise ValidationError("No previous result available for 'ans'")
                    return previous_result
            number = Decimal(str(value))
            if abs(number) > config.max_input_value:
                raise ValidationError(f"Value exceeds maximum allowed: {config.max_input_value}")
            return number.normalize()
        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}") from e

    @staticmethod
    def validate_expression(raw: str) -> Optional[re.Match]:
        """Match raw input against the expression pattern. Returns None if unrecognized"""
        return EXPRESSION_PATTERN.fullmatch(raw)
