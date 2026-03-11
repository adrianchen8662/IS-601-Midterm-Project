from abc import ABC, abstractmethod
from typing import Any
from app.calculation import Calculation
from app.logger import Logger


class HistoryObserver(ABC):
    """Abstract observer notified after each calculation."""

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        pass  # pragma: no cover


class LoggingObserver(HistoryObserver):
    """Logs each calculation to the log file."""

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        Logger.info(
            "Calculation performed: %s (%s, %s) = %s",
            calculation.operation,
            calculation.operand1,
            calculation.operand2,
            calculation.result,
        )


class AutoSaveObserver(HistoryObserver):
    """Auto-saves history after each calculation when enabled in config."""

    def __init__(self, calculator: Any):
        """Requires calculator to have 'config' and 'save_history' attributes."""
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            Logger.info("History auto-saved")
