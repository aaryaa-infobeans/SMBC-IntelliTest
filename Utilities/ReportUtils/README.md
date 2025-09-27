# Logger Implementation Guide

## Overview

This document describes the singleton logger implementation for the test automation framework. The logger provides centralized logging functionality with both file and console output.

## Logger Features

### Singleton Pattern
- Ensures only one logger instance exists throughout the application
- Thread-safe implementation
- Automatic initialization on first use

### Logging Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about test execution
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may stop execution

### Output Destinations
- **File Logging**: Detailed logs saved to `logs/test_automation_YYYYMMDD_HHMMSS.log`
- **Console Logging**: Important messages displayed in console (INFO level and above)

### Special Methods
- `test_start(test_name)`: Log test start with formatting
- `test_end(test_name, status)`: Log test completion with status
- `step(description)`: Log test steps
- `verification(description, result)`: Log verification results
- `screenshot_captured(test_name, filename)`: Log screenshot capture
- `evidence_attached(test_name, evidence_type)`: Log evidence attachment

## Usage Examples

### Basic Usage
```python
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()

# Basic logging
logger.info("Test execution started")
logger.debug("Detailed debug information")
logger.warning("This is a warning")
logger.error("An error occurred")

# Test-specific logging
logger.test_start("test_login_functionality")
logger.step("Entering username and password")
logger.verification("Login successful", True)
logger.test_end("test_login_functionality", "PASSED")
```

### In Test Classes
```python
import pytest
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()

class TestLogin:
    def test_valid_login(self):
        logger.test_start("test_valid_login")
        logger.step("Navigating to login page")
        # Test implementation
        logger.verification("User logged in successfully", True)
        logger.test_end("test_valid_login", "PASSED")
```

### In Helper Classes
```python
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()

class LoginHelper:
    def login(self, username, password):
        logger.step(f"Logging in with username: {username}")
        # Implementation
        logger.info("Login completed successfully")
```

### In Page Classes
```python
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()

class HomePage:
    def verify_products_displayed(self):
        logger.step("Verifying products are displayed on home page")
        products = self.get_products()
        logger.info(f"Found {len(products)} products")
        return len(products) > 0
```

## Configuration

### Log Level Configuration
```python
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()
logger.set_log_level('DEBUG')  # Set to DEBUG, INFO, WARNING, ERROR, or CRITICAL
```

### File Locations
- Log files are created in the `logs/` directory
- Each test run creates a new log file with timestamp
- Format: `test_automation_YYYYMMDD_HHMMSS.log`

## Integration with Framework Components

### Replaced Components
The logger has been implemented across:

1. **conftest.py**: Test hooks and fixtures
2. **Test Files**: All test classes in `SRC/Tests/TestsUI/`
3. **Helper Classes**: All helpers in `SRC/Helpers/`
4. **Page Classes**: All page objects in `SRC/Pages/`
5. **Test Base**: Base test class setup

### Docker Integration
- Log directory mounted as volume in Docker containers
- Logs persist on host machine after container execution
- Available in both development and CI/CD environments

## Benefits

1. **Centralized Logging**: All logging goes through single point
2. **Consistent Format**: Standardized log format across framework
3. **Multiple Outputs**: Both file and console logging
4. **Test Traceability**: Special methods for test lifecycle tracking
5. **Debug Support**: Detailed logging for troubleshooting
6. **Evidence Collection**: Integration with screenshot and evidence capture

## Best Practices

1. **Use Appropriate Levels**: Choose correct logging level for each message
2. **Descriptive Messages**: Write clear, actionable log messages
3. **Test Lifecycle**: Use special methods for test start/end
4. **Step Logging**: Log important test steps for traceability
5. **Error Context**: Include relevant context in error messages

## Migration from Print Statements

All `print()` statements have been replaced with appropriate logger calls:
- `print("info message")` → `logger.info("info message")`
- `print("debug info")` → `logger.debug("debug info")`
- `print("warning")` → `logger.warning("warning")`
- `print("error")` → `logger.error("error")`

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure correct import path
   ```python
   from Utilities.ReportUtils.logger import get_logger
   ```

2. **Log Files Not Created**: Check directory permissions and PYTHONPATH

3. **No Console Output**: Check log level settings (INFO and above for console)

### Debug Mode
Enable debug logging to see detailed execution flow:
```python
logger.set_log_level('DEBUG')
```
