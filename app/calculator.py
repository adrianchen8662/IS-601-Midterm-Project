import datetime
import logging
from decimal import Decimal
from typing import List, Optional

import pandas as pd

from app.calculation import Calculation, CalculationFactory
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation


class Calculator:
    """
    Core calculator using the Operation strategy pattern with history tracking.

    Supports undo/redo via CalculatorMemento snapshots and CSV persistence.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None) -> None:
        self.config: CalculatorConfig = config or CalculatorConfig()
        self.config.validate()

        self._history: List[Calculation] = []
        self._observers: List[HistoryObserver] = []
        self._undo_stack: List[CalculatorMemento] = []
        self._redo_stack: List[CalculatorMemento] = []
        self._operation: Optional[Operation] = None

    def add_observer(self, observer: HistoryObserver) -> None:
        """Register an observer to be notified after each calculation."""
        if not isinstance(observer, HistoryObserver):
            raise TypeError("Observer must be a HistoryObserver instance")
        self._observers.append(observer)

    def _notify_observers(self, calculation: Calculation) -> None:
        for observer in self._observers:
            observer.update(calculation)

    def set_operation(self, operation: Operation) -> None:
        self._operation = operation

    def perform_operation(self, a: str, b: str, previous_result: Optional[Decimal] = None) -> Decimal:
        """
        Validate inputs, execute the current operation, and record the result.

        Either operand may be ``"ans"`` to substitute *previous_result*.

        Raises:
            ValidationError: If either input is invalid or exceeds the configured maximum.
            OperationError: If no operation is set or the operation fails.
        """
        num_a: Decimal = InputValidator.validate_number(a, self.config, previous_result)
        num_b: Decimal = InputValidator.validate_number(b, self.config, previous_result)

        if self._operation is None:
            raise OperationError("No operation set. Call set_operation() first.")

        self._undo_stack.append(CalculatorMemento(list(self._history)))
        self._redo_stack.clear()

        try:
            result: Decimal = self._operation.execute(num_a, num_b)
        except (ZeroDivisionError, ValueError, ValidationError) as exc:
            self._undo_stack.pop()
            raise OperationError(str(exc)) from exc

        calculation: Calculation = CalculationFactory.create_calculation(
            self._operation.name, float(num_a), float(num_b)
        )
        self._history.append(calculation)
        self._notify_observers(calculation)

        return result

    def show_history(self) -> List[Calculation]:
        """Return a copy of the current calculation history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear history and reset undo/redo stacks."""
        self._history.clear()
        self._undo_stack.clear()
        self._redo_stack.clear()

    def undo(self) -> bool:
        """Restore history to before the most recent calculation. Returns False if nothing to undo."""
        if not self._undo_stack:
            return False
        self._redo_stack.append(CalculatorMemento(list(self._history)))
        memento = self._undo_stack.pop()
        self._history = list(memento.history)
        return True

    def redo(self) -> bool:
        """Re-apply the most recently undone calculation. Returns False if nothing to redo."""
        if not self._redo_stack:
            return False
        self._undo_stack.append(CalculatorMemento(list(self._history)))
        memento = self._redo_stack.pop()
        self._history = list(memento.history)
        return True

    def save_history(self) -> None:
        """Save calculation history to CSV (path from config)."""
        self.config.history_dir.mkdir(parents=True, exist_ok=True)
        records = [
            {
                'operation': calc.operation,
                'operand1': calc.operand1,
                'operand2': calc.operand2,
                'result': calc.result,
                'timestamp': calc.timestamp.isoformat(),
            }
            for calc in self._history
        ]
        df = pd.DataFrame(records, columns=['operation', 'operand1', 'operand2', 'result', 'timestamp'])
        df.to_csv(self.config.history_file, index=False, encoding=self.config.default_encoding)
        logging.info("History saved to %s", self.config.history_file)

    def load_history(self) -> None:
        """Load calculation history from CSV (path from config). Silently skips unparseable rows."""
        if not self.config.history_file.exists():
            return

        self._history.clear()
        df = pd.read_csv(self.config.history_file, encoding=self.config.default_encoding)
        for _, row in df.iterrows():
            try:
                calc = CalculationFactory.create_calculation(
                    row['operation'],
                    float(row['operand1']),
                    float(row['operand2']),
                )
                if 'timestamp' in row and pd.notna(row['timestamp']):
                    try:
                        calc.timestamp = datetime.datetime.fromisoformat(str(row['timestamp']))
                    except (ValueError, TypeError):
                        pass
                self._history.append(calc)
            except (ValueError, KeyError) as exc:
                logging.warning("Skipping invalid history entry: %s", exc)

        logging.info("History loaded from %s", self.config.history_file)
