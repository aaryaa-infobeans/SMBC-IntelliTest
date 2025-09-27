# Docker Setup for Playwright Test Automation

This directory contains Docker configuration files to run the Playwright test automation suite in containerized environments.

## Files Overview

- `DockerFile` - Main Docker image configuration with Python, Playwright, and all dependencies
- `Docker-compose.yml` - Orchestration file with multiple services for different use cases
- `docker-run.bat` - Windows batch script for easy test execution
- `docker-run.sh` - Linux/Mac shell script for easy test execution

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually included with Docker Desktop)

## Quick Start

### 1. Build and Run All Tests

```bash
# Navigate to the Docker directory
cd Docker

# Run all tests (Windows)
docker-run.bat

# Run all tests (Linux/Mac)
./docker-run.sh
```

### 2. Using Docker Compose Directly

```bash
# Build and run all tests
docker-compose up test-automation

# Run tests and generate Allure reports
docker-compose --profile reports up

# Run specific test file
docker-compose run --rm test-automation python -m pytest SRC/tests/test_login.py -v

# Run tests with specific markers
docker-compose run --rm test-automation python -m pytest SRC/tests/ -m "not skip" -v
```

## Advanced Usage

### Running Specific Tests

```bash
# Run specific test file
docker-run.bat -t SRC/tests/test_HomePage.py

# Run tests with specific markers
docker-run.bat -m "not skip"

# Run specific Xray test cases
docker-run.bat -x "MYS-12,MYS-13"
```

### Generate Reports

```bash
# Run tests and serve Allure reports
docker-run.bat -r

# Access reports at http://localhost:5050
```

### Manual Test Execution

```bash
# Start container for manual test execution
docker-compose --profile manual up -d test-specific

# Execute into the container
docker exec -it playwright-test-specific bash

# Run tests manually inside container
python -m pytest SRC/tests/test_login.py -v --alluredir=allure-results
```

## Services Available

### test-automation
- Main service that runs all tests automatically
- Generates JUnit XML, HTML, and Allure results
- Exits after test completion

### test-specific
- Manual execution service (profile: manual)
- Keeps container running for interactive testing
- Useful for debugging and development

### allure-report
- Allure report server (profile: reports)
- Serves reports on port 5050
- Automatically processes results from test runs

## Volume Mounts

The following directories are mounted to persist results:

- `../allure-results` → `/app/allure-results` - Allure test results
- `../test-results` → `/app/test-results` - JUnit XML and HTML reports
- `../screenshots` → `/app/screenshots` - Test failure screenshots
- `../SRC` → `/app/SRC` - Source code (for development)
- `../testData` → `/app/testData` - Test data files
- `../Utilities` → `/app/Utilities` - Utility modules

## Environment Variables

- `PYTHONPATH=/app` - Ensures proper Python module resolution
- `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` - Playwright browser location
- `DISPLAY=:99` - Virtual display for headless browser execution

## Troubleshooting

### Common Issues

1. **Permission Issues (Linux/Mac)**
   ```bash
   chmod +x docker-run.sh
   ```

2. **Port Already in Use**
   ```bash
   # Stop existing Allure service
   docker-compose --profile reports down
   ```

3. **Browser Installation Issues**
   ```bash
   # Rebuild the Docker image
   docker-compose build --no-cache test-automation
   ```

4. **Test Results Not Persisting**
   - Ensure the volume mount paths exist on the host
   - Check Docker Desktop file sharing settings

### Debugging

```bash
# View container logs
docker-compose logs test-automation

# Execute into running container
docker exec -it playwright-test-automation bash

# Check Playwright installation
docker-compose run --rm test-automation playwright --version
```

## Configuration

The tests use `config.json` in the project root for base configuration:

```json
{
  "base_url": "https://www.saucedemo.com/",
  "browser": "chromium",
  "headless": true,
  "viewport": {
    "width": 1280,
    "height": 720
  },
  "timeout": 30000,
  "slow_mo": 500
}
```

## CI/CD Integration

For CI/CD pipelines, use:

```bash
# Run tests without interactive elements
docker-compose run --rm test-automation

# Generate reports for CI artifacts
docker-compose run --rm test-automation sh -c "
  python -m pytest SRC/tests/ -v --alluredir=allure-results --junitxml=test-results/junit.xml &&
  tar -czf test-results.tar.gz allure-results/ test-results/ screenshots/
"
```
