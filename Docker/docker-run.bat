@echo off
REM Docker run script for Playwright Test Automation (Windows)

echo === Playwright Test Automation Docker Runner ===

REM Default values
set TESTS=SRC/tests/
set MARKERS=
set XRAY_IDS=
set BROWSER=chromium
set HEADLESS=true
set REPORTS=false
set EXTRA_ARGS=

REM Parse command line arguments
:parse_args
if "%~1"=="" goto run_tests
if "%~1"=="-t" (
    set TESTS=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--tests" (
    set TESTS=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-m" (
    set MARKERS=-m %~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--markers" (
    set MARKERS=-m %~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-x" (
    set XRAY_IDS=--xray-ids %~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--xray-ids" (
    set XRAY_IDS=--xray-ids %~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-r" (
    set REPORTS=true
    shift
    goto parse_args
)
if "%~1"=="--reports" (
    set REPORTS=true
    shift
    goto parse_args
)
if "%~1"=="--help" (
    goto show_usage
)
set EXTRA_ARGS=%EXTRA_ARGS% %~1
shift
goto parse_args

:show_usage
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   -t, --tests ^<path^>     Run specific test file or directory (default: SRC/tests/)
echo   -m, --markers ^<marker^> Run tests with specific pytest markers
echo   -x, --xray-ids ^<ids^>   Run tests with specific Xray IDs (comma-separated)
echo   -r, --reports          Generate and serve Allure reports
echo   --help                 Show this help message
echo.
echo Examples:
echo   %0                                    # Run all tests
echo   %0 -t SRC/tests/test_login.py        # Run specific test file
echo   %0 -m "not skip"                     # Run tests not marked as skip
echo   %0 -x "MYS-12,MYS-13"                # Run specific Xray test cases
echo   %0 -r                                # Run tests and generate reports
goto end

:run_tests
REM Build the pytest command
set PYTEST_CMD=python -m pytest %TESTS% -v --alluredir=allure-results --junitxml=test-results/test-results.xml --html=test-results/report.html --self-contained-html

if not "%MARKERS%"=="" (
    set PYTEST_CMD=%PYTEST_CMD% %MARKERS%
)

if not "%XRAY_IDS%"=="" (
    set PYTEST_CMD=%PYTEST_CMD% %XRAY_IDS%
)

if not "%EXTRA_ARGS%"=="" (
    set PYTEST_CMD=%PYTEST_CMD% %EXTRA_ARGS%
)

echo Running command: %PYTEST_CMD%
echo Browser: %BROWSER%
echo Headless: %HEADLESS%
echo.

REM Run the Docker container
docker-compose -f Docker/Docker-compose.yml run --rm test-automation sh -c "%PYTEST_CMD%"

REM Generate Allure reports if requested
if "%REPORTS%"=="true" (
    echo.
    echo === Generating Allure Reports ===
    docker-compose -f Docker/Docker-compose.yml --profile reports up -d allure-report
    echo Allure reports will be available at: http://localhost:5050
    echo Press Ctrl+C to stop the report server
    pause
    docker-compose -f Docker/Docker-compose.yml --profile reports down
)

echo.
echo === Test Execution Complete ===
echo Results available in:
echo   - test-results/test-results.xml (JUnit XML)
echo   - test-results/report.html (HTML Report)
echo   - allure-results/ (Allure Results)

:end
