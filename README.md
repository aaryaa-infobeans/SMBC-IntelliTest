# SMBC-IntelliTest

*Smarter regression with intelligence built-in.*

A comprehensive Python-based test automation framework using **Pytest** and **Playwright** for UI and API testing.

## 🏗️ Project Structure

```
SMBC-IntelliTest/
├── SRC/                          # Source code
│   ├── tests/                    # Test cases
│   │   ├── tests_ui/            # UI test scenarios
│   │   └── tests_api/           # API test scenarios
│   ├── pages/                   # Page Object Model classes
│   ├── helpers/                 # Business logic helpers
│   └── base/                    # Base classes
├── Utilities/                   # Framework utilities
│   ├── GenericUtils/           # Generic utility functions
│   ├── ReportUtils/            # Reporting utilities
│   └── TestUtils/              # Test-specific utilities
├── TestDataCommon/             # Test data management
├── docs/                       # Documentation
├── screenshots/                # Test failure screenshots
├── test-evidence/              # Test execution evidence
├── .github/workflows/          # CI/CD pipelines
├── conftest.py                 # Pytest configuration
├── pytest.ini
├── requirements.txt
├── config.json
└── README.md
```

## ✨ Key Features

- **🎭 Multi-Browser Support:** Chromium, Firefox, WebKit via Playwright
- **🏗️ Page Object Model:** Clean, maintainable test architecture
- **🔄 Helper Layer:** Reusable business logic components
- **📊 Rich Reporting:** Allure, HTML, JSON, PDF report formats
- **🔧 CI/CD Ready:** GitHub Actions and Azure Pipelines configured
- **📝 Test Management:** Jira Xray integration for test case tracking
- **⚡ Parallel Execution:** Fast test runs with pytest-xdist
- **🛡️ Quality Gates:** Automatic screenshot capture on failures
- **📈 Data-Driven:** Dynamic test data with Faker integration

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (recommended)
- **Git** for version control
- **Node.js** (optional, for Allure report serving)

### Setup

1. **Create and activate a virtual environment (recommended):**
    - On Windows:
      ```bash
      python -m venv .venv
      .venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Install Playwright browsers:**
    ```bash
    playwright install
    ```

4. **Configure environment (optional):**
    - Edit `config.json` for environment-specific settings.
    - Update/add test data in `testData/`.

## Running Tests

1. **Run all tests:**
    ```bash
    pytest
    ```

2. **Run a specific test:**
    ```bash
    pytest Automation/tests/test_login.py
    ```

3. **Generate Allure report:**
    ```bash
    allure serve allure-results
    ```

## Contribution Guidelines

- Use the Page Object Model for new UI flows.
- Place reusable logic in `helpers/`.
- Store all test data in `testData/`.
- Use fixtures in `conftest.py` for setup/teardown.
- Keep configuration out of test code.
- 4c32b6d3d685a902186a7a3d5193b5b703df55c84919fa445c7f44c49335701f

## Troubleshooting

- Ensure all dependencies are installed and the virtual environment is active.
- If browsers are missing, re-run `playwright install`.
- For verbose test output, use:
    ```bash
    pytest -v -s
    ```
- Check `pytest.ini` and `config.json` for correct configuration.

## Support
Sample commit

For questions or issues, contact the framework maintainer or raise an issue in the repository.
Commit for Demo

