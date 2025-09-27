import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Add a new attribute `funcLine`
        record.funcLine = f"{record.funcName}:{record.lineno}"
        return super().format(record)


class Logger:
    """
    Singleton Logger class for the test automation framework.
    Provides centralized logging functionality with file and console output.
    """

    _instance: Optional["Logger"] = None
    _logger: Optional[logging.Logger] = None
    _initialized: bool = False

    def __new__(cls) -> "Logger":
        """Ensure only one instance of Logger exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger if not already initialized."""
        if not self._initialized:
            self._setup_logger()
            Logger._initialized = True

    def _setup_logger(self):
        """Set up the logger configuration."""
        # Create logger
        self._logger = logging.getLogger("TestAutomationFramework")
        self._logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self._logger.handlers:
            return

        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Use your custom formatter instead of plain logging.Formatter
        detailed_formatter = CustomFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(funcLine)-10s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        simple_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S")

        # File handler for detailed logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(log_dir / f"test_automation_{timestamp}.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        # Console handler for important messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)

        # Add handlers to logger
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

        # Log initialization
        self._logger.info("Logger initialized successfully")

    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        if self._logger:
            self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        if self._logger:
            self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        if self._logger:
            self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        if self._logger:
            self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        if self._logger:
            self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback."""
        if self._logger:
            self._logger.exception(message, *args, **kwargs)

    def test_start(self, test_name: str):
        """Log test start with special formatting."""
        self.info(f"{'=' * 60}")
        self.info(f"STARTING TEST: {test_name}")
        self.info(f"{'=' * 60}")

    def test_end(self, test_name: str, status: str):
        """Log test end with special formatting."""
        self.info(f"{'=' * 60}")
        self.info(f"FINISHED TEST: {test_name} - STATUS: {status}")
        self.info(f"{'=' * 60}\n\n")

    def step(self, step_description: str):
        """Log test step with special formatting."""
        self.info(f"STEP: {step_description}")

    def verification(self, description: str, result: bool):
        """Log verification with result."""
        status = "PASSED" if result else "FAILED"
        self.info(f"VERIFICATION: {description} - {status}")

    def screenshot_captured(self, test_name: str, filename: str):
        """Log screenshot capture."""
        self.info(f"SCREENSHOT: Captured for test '{test_name}' as '{filename}'")

    def evidence_attached(self, test_name: str, evidence_type: str):
        """Log evidence attachment."""
        self.info(f"EVIDENCE: Attached {evidence_type} for test '{test_name}'")

    def set_log_level(self, level: str):
        """Set logging level dynamically."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if level.upper() in level_map and self._logger:
            self._logger.setLevel(level_map[level.upper()])
            self.info(f"Log level set to {level.upper()}")
        else:
            self.warning(f"Invalid log level: {level}")


# Global logger instance
logger = Logger()


def get_logger() -> Logger:
    """Get the singleton logger instance."""
    return logger
