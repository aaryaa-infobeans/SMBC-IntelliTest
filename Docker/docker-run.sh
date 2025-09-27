#!/bin/bash

# Docker run script for Playwright Test Automation

echo "=== Playwright Test Automation Docker Runner ==="

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --tests <path>     Run specific test file or directory (default: SRC/tests/)"
    echo "  -m, --markers <marker> Run tests with specific pytest markers"
    echo "  -x, --xray-ids <ids>   Run tests with specific Xray IDs (comma-separated)"
    echo "  -b, --browser <name>   Browser to use (chromium, firefox, webkit)"
    echo "  -h, --headless         Run in headless mode (default: true)"
    echo "  -r, --reports          Generate and serve Allure reports"
    echo "  --help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests"
    echo "  $0 -t SRC/tests/test_login.py        # Run specific test file"
    echo "  $0 -m \"not skip\"                    # Run tests not marked as skip"
    echo "  $0 -x \"MYS-12,MYS-13\"               # Run specific Xray test cases"
    echo "  $0 -r                                # Run tests and generate reports"
}

# Default values
TESTS="SRC/tests/"
MARKERS=""
XRAY_IDS=""
BROWSER="chromium"
HEADLESS="true"
REPORTS=false
EXTRA_ARGS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tests)
            TESTS="$2"
            shift 2
            ;;
        -m|--markers)
            MARKERS="-m $2"
            shift 2
            ;;
        -x|--xray-ids)
            XRAY_IDS="--xray-ids $2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -h|--headless)
            HEADLESS="true"
            shift
            ;;
        -r|--reports)
            REPORTS=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
    esac
done

# Build the pytest command
PYTEST_CMD="python -m pytest $TESTS -v --alluredir=allure-results --junitxml=test-results/test-results.xml --html=test-results/report.html --self-contained-html"

if [ ! -z "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD $MARKERS"
fi

if [ ! -z "$XRAY_IDS" ]; then
    PYTEST_CMD="$PYTEST_CMD $XRAY_IDS"
fi

if [ ! -z "$EXTRA_ARGS" ]; then
    PYTEST_CMD="$PYTEST_CMD $EXTRA_ARGS"
fi

echo "Running command: $PYTEST_CMD"
echo "Browser: $BROWSER"
echo "Headless: $HEADLESS"
echo ""

# Run the Docker container
docker-compose -f Docker/Docker-compose.yml run --rm test-automation sh -c "$PYTEST_CMD"

# Generate Allure reports if requested
if [ "$REPORTS" = true ]; then
    echo ""
    echo "=== Generating Allure Reports ==="
    docker-compose -f Docker/Docker-compose.yml --profile reports up -d allure-report
    echo "Allure reports will be available at: http://localhost:5050"
    echo "Press Ctrl+C to stop the report server"
    
    # Wait for user interrupt
    trap 'docker-compose -f Docker/Docker-compose.yml --profile reports down; exit' INT
    while true; do
        sleep 1
    done
fi

echo ""
echo "=== Test Execution Complete ==="
echo "Results available in:"
echo "  - test-results/test-results.xml (JUnit XML)"
echo "  - test-results/report.html (HTML Report)"
echo "  - allure-results/ (Allure Results)"
