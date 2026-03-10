import pytest
from decimal import Decimal
from typing import Any, Dict, Type

from app.exceptions import ValidationError
from app.operations import (
    Operation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Power,
    Root,
    Modulus,
    IntegerDivision,
    Percentage,
    AbsoluteDifference,
    OperationFactory,
    register_op,
)


class TestOperation:
    def test_str_representation(self):
        class TestOp(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a  # pragma: no cover

        assert str(TestOp()) == "TestOp"


class BaseOperationTest:
    """Base test class for all operations."""

    operation_class: Type[Operation]
    valid_test_cases: Dict[str, Dict[str, Any]]
    invalid_test_cases: Dict[str, Dict[str, Any]]

    def test_valid_operations(self):
        operation = self.operation_class()
        for name, case in self.valid_test_cases.items():
            a = Decimal(str(case["a"]))
            b = Decimal(str(case["b"]))
            expected = Decimal(str(case["expected"]))
            result = operation.execute(a, b)
            assert result == expected, f"Failed case: {name}"

    def test_invalid_operations(self):
        operation = self.operation_class()
        for name, case in self.invalid_test_cases.items():
            a = Decimal(str(case["a"]))
            b = Decimal(str(case["b"]))
            error = case.get("error", ValidationError)
            error_message = case.get("message", "")

            with pytest.raises(error, match=error_message):
                operation.execute(a, b)


class TestAddition(BaseOperationTest):
    operation_class = Addition
    valid_test_cases = {
        "positive_numbers": {"a": "5", "b": "3", "expected": "8"},
        "negative_numbers": {"a": "-5", "b": "-3", "expected": "-8"},
        "mixed_signs": {"a": "-5", "b": "3", "expected": "-2"},
        "zero_sum": {"a": "5", "b": "-5", "expected": "0"},
        "decimals": {"a": "5.5", "b": "3.3", "expected": "8.8"},
        "large_numbers": {"a": "1e10", "b": "1e10", "expected": "20000000000"},
    }
    invalid_test_cases = {}


class TestSubtraction(BaseOperationTest):
    operation_class = Subtraction
    valid_test_cases = {
        "positive_numbers": {"a": "5", "b": "3", "expected": "2"},
        "negative_numbers": {"a": "-5", "b": "-3", "expected": "-2"},
        "mixed_signs": {"a": "-5", "b": "3", "expected": "-8"},
        "zero_result": {"a": "5", "b": "5", "expected": "0"},
        "decimals": {"a": "5.5", "b": "3.3", "expected": "2.2"},
        "large_numbers": {"a": "1e10", "b": "1e9", "expected": "9000000000"},
    }
    invalid_test_cases = {}


class TestMultiplication(BaseOperationTest):
    operation_class = Multiplication
    valid_test_cases = {
        "positive_numbers": {"a": "5", "b": "3", "expected": "15"},
        "negative_numbers": {"a": "-5", "b": "-3", "expected": "15"},
        "mixed_signs": {"a": "-5", "b": "3", "expected": "-15"},
        "multiply_by_zero": {"a": "5", "b": "0", "expected": "0"},
        "decimals": {"a": "5.5", "b": "3.3", "expected": "18.15"},
        "large_numbers": {"a": "1e5", "b": "1e5", "expected": "10000000000"},
    }
    invalid_test_cases = {}


class TestDivision(BaseOperationTest):
    operation_class = Division
    valid_test_cases = {
        "positive_numbers": {"a": "6", "b": "2", "expected": "3"},
        "negative_numbers": {"a": "-6", "b": "-2", "expected": "3"},
        "mixed_signs": {"a": "-6", "b": "2", "expected": "-3"},
        "decimals": {"a": "5.5", "b": "2", "expected": "2.75"},
        "divide_zero": {"a": "0", "b": "5", "expected": "0"},
    }
    invalid_test_cases = {
        "divide_by_zero": {
            "a": "5",
            "b": "0",
            "error": ValidationError,
            "message": "Division by zero is not allowed"
        },
    }


class TestPower(BaseOperationTest):
    operation_class = Power
    valid_test_cases = {
        "positive_base_and_exponent": {"a": "2", "b": "3", "expected": "8"},
        "zero_exponent": {"a": "5", "b": "0", "expected": "1"},
        "one_exponent": {"a": "5", "b": "1", "expected": "5"},
        "decimal_base": {"a": "2.5", "b": "2", "expected": "6.25"},
        "zero_base": {"a": "0", "b": "5", "expected": "0"},
    }
    invalid_test_cases = {
        "negative_exponent": {
            "a": "2",
            "b": "-3",
            "error": ValidationError,
            "message": "Negative exponents not supported"
        },
    }


class TestRoot(BaseOperationTest):
    operation_class = Root
    valid_test_cases = {
        "square_root": {"a": "9", "b": "2", "expected": "3"},
        "cube_root": {"a": "27", "b": "3", "expected": "3"},
        "fourth_root": {"a": "16", "b": "4", "expected": "2"},
        "decimal_root": {"a": "2.25", "b": "2", "expected": "1.5"},
    }
    invalid_test_cases = {
        "negative_base": {
            "a": "-9",
            "b": "2",
            "error": ValidationError,
            "message": "Cannot calculate root of negative number"
        },
        "zero_root": {
            "a": "9",
            "b": "0",
            "error": ValidationError,
            "message": "Zero root is undefined"
        },
    }


class TestModulus(BaseOperationTest):
    operation_class = Modulus
    valid_test_cases = {
        "basic": {"a": "10", "b": "3", "expected": "1"},
        "exact_division": {"a": "9", "b": "3", "expected": "0"},
        "large_remainder": {"a": "7", "b": "4", "expected": "3"},
    }
    invalid_test_cases = {
        "modulus_by_zero": {
            "a": "10", "b": "0",
            "error": ValidationError,
            "message": "Modulus by zero is not allowed",
        },
    }


class TestIntegerDivision(BaseOperationTest):
    operation_class = IntegerDivision
    valid_test_cases = {
        "basic": {"a": "10", "b": "3", "expected": "3"},
        "exact": {"a": "9", "b": "3", "expected": "3"},
        "large": {"a": "100", "b": "7", "expected": "14"},
    }
    invalid_test_cases = {
        "division_by_zero": {
            "a": "10", "b": "0",
            "error": ValidationError,
            "message": "Integer division by zero is not allowed",
        },
    }


class TestPercentage(BaseOperationTest):
    operation_class = Percentage
    valid_test_cases = {
        "basic": {"a": "25", "b": "200", "expected": "12.5"},
        "full": {"a": "100", "b": "100", "expected": "100"},
        "half": {"a": "1", "b": "2", "expected": "50"},
    }
    invalid_test_cases = {
        "zero_denominator": {
            "a": "25", "b": "0",
            "error": ValidationError,
            "message": "Cannot calculate percentage with zero denominator",
        },
    }


class TestAbsoluteDifference(BaseOperationTest):
    operation_class = AbsoluteDifference
    valid_test_cases = {
        "a_greater": {"a": "9", "b": "4", "expected": "5"},
        "b_greater": {"a": "4", "b": "9", "expected": "5"},
        "equal": {"a": "5", "b": "5", "expected": "0"},
    }
    invalid_test_cases = {}


class TestOperationFactory:
    def test_create_valid_operations(self):
        operation_map = {
            'add': Addition,
            'subtract': Subtraction,
            'multiply': Multiplication,
            'divide': Division,
            'power': Power,
            'root': Root,
            'modulus': Modulus,
            'intdiv': IntegerDivision,
            'percentage': Percentage,
            'absdiff': AbsoluteDifference,
        }
        for op_name, op_class in operation_map.items():
            assert isinstance(OperationFactory.create_operation(op_name), op_class)
            assert isinstance(OperationFactory.create_operation(op_name.upper()), op_class)

    def test_create_invalid_operation(self):
        with pytest.raises(ValueError, match="Unknown operation: invalid_op"):
            OperationFactory.create_operation("invalid_op")

    def test_register_valid_operation(self):
        class NewOperation(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a  # pragma: no cover

        OperationFactory.register_operation("new_op", NewOperation)
        assert isinstance(OperationFactory.create_operation("new_op"), NewOperation)

    def test_register_invalid_operation(self):
        class InvalidOperation:
            pass

        with pytest.raises(TypeError, match="Operation class must inherit"):
            OperationFactory.register_operation("invalid", InvalidOperation)

    def test_help_entries_contains_keyword_ops(self):
        entries = OperationFactory.help_entries()
        names = [e['name'] for e in entries]
        assert 'power' in names
        assert 'root' in names
        assert 'modulus' in names
        assert 'intdiv' in names
        assert 'percentage' in names
        assert 'absdiff' in names

    def test_help_entries_excludes_infix_ops(self):
        entries = OperationFactory.help_entries()
        names = [e['name'] for e in entries]
        for infix in ('add', 'subtract', 'multiply', 'divide'):
            assert infix not in names

    def test_help_entries_have_required_fields(self):
        for entry in OperationFactory.help_entries():
            assert 'name' in entry
            assert 'description' in entry
            assert 'example' in entry
            assert entry['description'] != ''
            assert entry['example'] != ''

    def test_keyword_op_names_returns_keyword_ops(self):
        kw = OperationFactory.keyword_op_names()
        assert isinstance(kw, frozenset)
        assert 'power' in kw
        assert 'root' in kw
        assert 'modulus' in kw
        assert 'intdiv' in kw
        assert 'percentage' in kw
        assert 'absdiff' in kw

    def test_keyword_op_names_excludes_infix_ops(self):
        kw = OperationFactory.keyword_op_names()
        for infix in ('add', 'subtract', 'multiply', 'divide'):
            assert infix not in kw

    def test_infix_entries_contains_infix_ops(self):
        entries = OperationFactory.infix_entries()
        symbols = [e['symbol'] for e in entries]
        assert '+' in symbols
        assert '-' in symbols
        assert '*' in symbols
        assert '/' in symbols
        assert '%' in symbols
        assert '//' in symbols

    def test_infix_entries_have_required_fields(self):
        for entry in OperationFactory.infix_entries():
            assert 'symbol' in entry
            assert 'description' in entry
            assert 'example' in entry
            assert entry['symbol'] != ''
            assert entry['description'] != ''
            assert entry['example'] != ''

    def test_infix_entries_excludes_non_infix_ops(self):
        entries = OperationFactory.infix_entries()
        names_via_symbol = {e['symbol'] for e in entries}
        # power, root, percentage, absdiff have no symbol
        for op in OperationFactory._operations.values():
            if not getattr(op, 'is_infix', False):
                assert getattr(op, 'symbol', '') not in names_via_symbol or op.symbol == ''


class TestRegisterOpDecorator:
    def test_attaches_name(self):
        assert Power.name == 'power'

    def test_attaches_description(self):
        assert Power.description == 'Raise a to the power b'

    def test_attaches_example(self):
        assert Power.example == 'power 2 8'

    def test_is_keyword_true_for_keyword_ops(self):
        for cls in (Power, Root, Modulus, IntegerDivision, Percentage, AbsoluteDifference):
            assert cls.is_keyword is True

    def test_is_keyword_false_for_infix_ops(self):
        for cls in (Addition, Subtraction, Multiplication, Division):
            assert cls.is_keyword is False

    def test_is_infix_true_for_infix_ops(self):
        for cls in (Addition, Subtraction, Multiplication, Division, Modulus, IntegerDivision):
            assert cls.is_infix is True

    def test_is_infix_false_for_keyword_only_ops(self):
        for cls in (Power, Root, Percentage, AbsoluteDifference):
            assert cls.is_infix is False

    def test_attaches_symbol_for_infix_ops(self):
        assert Addition.symbol == '+'
        assert Subtraction.symbol == '-'
        assert Multiplication.symbol == '*'
        assert Division.symbol == '/'
        assert Modulus.symbol == '%'
        assert IntegerDivision.symbol == '//'

    def test_modulus_and_intdiv_are_both_infix_and_keyword(self):
        assert Modulus.is_infix is True
        assert Modulus.is_keyword is True
        assert IntegerDivision.is_infix is True
        assert IntegerDivision.is_keyword is True

    def test_decorator_registers_in_factory(self):
        @register_op('test_dec_op')
        class TestDecOp(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a + b  # pragma: no cover

        assert isinstance(OperationFactory.create_operation('test_dec_op'), TestDecOp)

    def test_new_keyword_op_appears_in_help(self):
        @register_op('test_help_op',
                     description='Test description',
                     example='test_help_op 1 2',
                     is_keyword=True)
        class TestHelpOp(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a  # pragma: no cover

        names = [e['name'] for e in OperationFactory.help_entries()]
        assert 'test_help_op' in names

    def test_new_keyword_op_appears_in_keyword_op_names(self):
        @register_op('test_kw_op', is_keyword=True)
        class TestKwOp(Operation):
            def execute(self, a: Decimal, b: Decimal) -> Decimal:
                return a  # pragma: no cover

        assert 'test_kw_op' in OperationFactory.keyword_op_names()
