import logging
import pytest
from app.logger import Logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Clear Logger handlers after each test to prevent cross-test interference."""
    yield
    Logger._logger.handlers.clear()


def test_setup_creates_log_file(tmp_path):
    log_file = tmp_path / "logs" / "calculator.log"
    Logger.setup(log_file)
    assert log_file.exists()


def test_setup_creates_parent_directories(tmp_path):
    log_file = tmp_path / "deep" / "nested" / "calculator.log"
    Logger.setup(log_file)
    assert log_file.parent.exists()


def test_info_writes_to_file(tmp_path):
    log_file = tmp_path / "calculator.log"
    Logger.setup(log_file)
    Logger.info("Test info message")
    Logger._logger.handlers[0].flush()
    assert "INFO" in log_file.read_text()
    assert "Test info message" in log_file.read_text()


def test_warning_writes_to_file(tmp_path):
    log_file = tmp_path / "calculator.log"
    Logger.setup(log_file)
    Logger.warning("Test warning message")
    Logger._logger.handlers[0].flush()
    assert "WARNING" in log_file.read_text()
    assert "Test warning message" in log_file.read_text()


def test_error_writes_to_file(tmp_path):
    log_file = tmp_path / "calculator.log"
    Logger.setup(log_file)
    Logger.error("Test error message")
    Logger._logger.handlers[0].flush()
    assert "ERROR" in log_file.read_text()
    assert "Test error message" in log_file.read_text()


def test_setup_clears_previous_handlers(tmp_path):
    log_file = tmp_path / "calculator.log"
    Logger.setup(log_file)
    Logger.setup(log_file)
    assert len(Logger._logger.handlers) == 1


def test_info_with_format_args(tmp_path):
    log_file = tmp_path / "calculator.log"
    Logger.setup(log_file)
    Logger.info("Operation %s result: %s", "add", 42)
    Logger._logger.handlers[0].flush()
    content = log_file.read_text()
    assert "Operation add result: 42" in content


def test_logger_does_not_propagate(tmp_path):
    log_file = tmp_path / "calculator.log"
    Logger.setup(log_file)
    assert Logger._logger.propagate is False


def test_logger_level_is_debug(tmp_path):
    log_file = tmp_path / "calculator.log"
    Logger.setup(log_file)
    assert Logger._logger.level == logging.DEBUG


def test_setup_respects_encoding(tmp_path):
    log_file = tmp_path / "calculator.log"
    Logger.setup(log_file, encoding='utf-8')
    Logger.info("Encoded message")
    Logger._logger.handlers[0].flush()
    assert log_file.read_text(encoding='utf-8')
