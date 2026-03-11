import logging
from pathlib import Path


class Logger:
    """Centralized logger for the calculator application.

    Wraps Python's logging module to write calculation events, warnings,
    and errors to a configurable log file.
    """

    _logger: logging.Logger = logging.getLogger('calculator')

    @classmethod
    def setup(cls, log_file: Path, encoding: str = 'utf-8') -> None:
        """Configure the logger to write to log_file.

        Clears any existing handlers first so repeated calls (e.g. in tests)
        do not accumulate duplicate handlers.
        """
        cls._logger.handlers.clear()
        cls._logger.propagate = False
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_file, encoding=encoding)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        cls._logger.setLevel(logging.DEBUG)
        cls._logger.addHandler(handler)

    @classmethod
    def info(cls, message: str, *args) -> None:
        """Log a message at INFO level."""
        cls._logger.info(message, *args)

    @classmethod
    def warning(cls, message: str, *args) -> None:
        """Log a message at WARNING level."""
        cls._logger.warning(message, *args)

    @classmethod
    def error(cls, message: str, *args) -> None:
        """Log a message at ERROR level."""
        cls._logger.error(message, *args)
