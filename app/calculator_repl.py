import logging
from decimal import Decimal
from typing import Optional

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.input_validators import InputValidator, KEYWORD_OPS
from app.operations import OperationFactory

OPERATOR_MAP = {
    '+': 'add',
    '-': 'subtract',
    '*': 'multiply',
    '/': 'divide',
    '%': 'modulus',
    '//': 'intdiv',
}

HELP_TEXT = """
Calculator REPL
---------------
Usage:
  <num> <op> <num>      New expression, e.g. 1 + 2
  <op> <num>            Continue from last result, e.g. + 5
  power <a> <b>         Raise a to the power b, e.g. power 2 8
  root <a> <b>          Compute the bth root of a, e.g. root 27 3
  modulus <a> <b>       Remainder of a ÷ b, e.g. modulus 10 3
  intdiv <a> <b>        Integer quotient of a ÷ b, e.g. intdiv 10 3
  percentage <a> <b>    (a / b) × 100, e.g. percentage 25 200
  absdiff <a> <b>       |a − b|, e.g. absdiff 9 4

  For keyword operations either <a> or <b> may be 'ans' to
  substitute the previous result, e.g. power ans 2  or  root 256 ans
  = / ans               Show current result
  history / hist        Show calculation history
  undo / redo           Undo or redo the last calculation
  save / load           Save or load history to/from file
  c / clear             Clear result and history
  h / help              Show this help
  e / exit              Exit

Supported infix operators: + - * /
"""


def _format_result(value: Decimal) -> str:
    """Display as integer when there is no fractional part."""
    if value == value.to_integral_value():
        return str(int(value))
    return str(value)


def _display_history(history) -> None:
    if not history:
        print("No calculations in history yet.")
        return
    print("\nCalculation History:")
    for idx, calc in enumerate(history, start=1):
        print(f"  {idx}. {calc}")
    print()


def calculator_repl() -> None:
    """Expression-based REPL for the calculator."""
    try:
        calc = Calculator()
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))
    except Exception as exc:
        print(f"Fatal error: {exc}")
        logging.error("Fatal error initialising calculator: %s", exc)
        raise

    result: Optional[Decimal] = None
    print(HELP_TEXT)

    while True:
        prompt = f"[{_format_result(result)}] > " if result is not None else "> "
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting")
            break

        if not raw:
            continue

        cmd = raw.lower()

        if cmd in ('e', 'exit'):
            try:
                calc.save_history()
            except Exception:
                pass
            print("Exiting")
            break

        if cmd in ('h', 'help'):
            print(HELP_TEXT)
            continue

        if cmd in ('c', 'clear'):
            result = None
            calc.clear_history()
            print("Cleared.")
            continue

        if cmd in ('=', 'ans'):
            if result is None:
                print("No result yet.")
            else:
                print(f"= {_format_result(result)}")
            continue

        if cmd in ('history', 'hist'):
            _display_history(calc.show_history())
            continue

        if cmd == 'undo':
            if calc.undo():
                history = calc.show_history()
                result = Decimal(str(history[-1].result)) if history else None
                print("Undone.")
            else:
                print("Nothing to undo.")
            continue

        if cmd == 'redo':
            if calc.redo():
                history = calc.show_history()
                result = Decimal(str(history[-1].result)) if history else None
                print("Redone.")
            else:
                print("Nothing to redo.")
            continue

        if cmd == 'save':
            try:
                calc.save_history()
                print("History saved.")
            except Exception as exc:
                print(f"Error saving history: {exc}")
            continue

        if cmd == 'load':
            try:
                calc.load_history()
                history = calc.show_history()
                result = Decimal(str(history[-1].result)) if history else None
                print("History loaded.")
            except Exception as exc:
                print(f"Error loading history: {exc}")
            continue

        parts = raw.split()
        if len(parts) == 3 and parts[0].lower() in KEYWORD_OPS:
            op_name = parts[0].lower()
            try:
                calc.set_operation(OperationFactory.create_operation(op_name))
                result = calc.perform_operation(parts[1], parts[2], previous_result=result)
                print(_format_result(result))
            except (ValidationError, OperationError) as exc:
                print(f"Error: {exc}")
            continue

        match = InputValidator.validate_expression(raw)
        if not match:
            print("Error: Unrecognized input. Type 'h' for help.")
            continue

        try:
            if match.group(1) is not None:
                a_str = match.group(1).replace(' ', '')
                op_symbol = match.group(2)
                b_str = match.group(3).replace(' ', '')
            else:
                if result is None:
                    print("Error: No previous result. Start with a full expression, e.g. '1 + 2'.")
                    continue
                a_str = str(result)
                op_symbol = match.group(4)
                b_str = match.group(5).replace(' ', '')

            calc.set_operation(OperationFactory.create_operation(OPERATOR_MAP[op_symbol]))
            result = calc.perform_operation(a_str, b_str)
            print(_format_result(result))

        except (ValidationError, OperationError) as exc:
            print(f"Error: {exc}")
        except Exception as exc:
            print(f"Unexpected error: {exc}")
