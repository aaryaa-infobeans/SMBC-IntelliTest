"""Pytest configuration file for test setup, teardown, and hooks.

This module contains pytest fixtures and hooks for:
- Test execution reporting and logging
- Xray test management integration
- Automatic screenshot capture on test failures
- Evidence collection and attachment for test results
- Browser fixture for Playwright-based UI tests
"""

import logging
import os

import allure
import pytest
from playwright.sync_api import Page
from pytest_xray import evidence

from Utilities.ReportUtils.logger import get_logger

logger = get_logger()
xray_logger = logging.getLogger("pytest-xray-evidence")


def _handle_test_logging(item, call, report):
    """Handle test start/end logging.
    Args:
        item: The test item being executed.
        call: The call object containing information about the test phase.
        report: The test report object.
    """
    if call.when == "setup":
        logger.test_start(item.name)
    elif call.when == "teardown":
        status = "PASSED" if report.passed else "FAILED" if report.failed else "SKIPPED"
        logger.test_end(item.name, status)


def _handle_xray_test_keys(item, call):
    """Handle Xray test key processing.
    Args:
        item: The test item being executed.
        call: The call object containing information about the test phase.
    """
    if "xray" in item.keywords:
        test_key = item.get_closest_marker("xray").args[0]
        if hasattr(item, "rep_" + call.when):
            rep = getattr(item, "rep_" + call.when)
            rep.test_key = test_key
        if call.when == "call":
            # Only add the test_key once
            item.user_properties.append(("test_key", test_key))


def _capture_screenshot(item, report):
    """Capture screenshot on test failure.
    Args:
        item: The test item being executed.
        report: The test report object.
    Returns:
        str or None: Path to the screenshot if captured, None otherwise.
    """
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page", None)
        if page:
            test_file = os.path.splitext(os.path.basename(item.location[0]))[0]
            test_name = item.name
            screenshot_filename = f"{test_file}__{test_name}.jpeg"
            try:
                page.screenshot(path=screenshot_filename)
                logger.screenshot_captured(item.name, screenshot_filename)
                return screenshot_filename
            except Exception as e:
                logger.error(f"Screenshot capture failed for {item.name}: {e}")
        else:
            logger.warning(f"No page instance found for {item.name}")
    return None


def _attach_evidence(item, screenshot_path, report):
    """Attach evidence (screenshots) to test reports.
    Args:
        item: The test item being executed.
        screenshot_path: Path to the screenshot file.
        report: The pytest report object.
    """
    if not screenshot_path or not os.path.exists(screenshot_path):
        return

    try:
        logger.debug("Reading screenshot data for evidence attachment")
        with open(screenshot_path, "rb") as file:
            data = file.read()
        logger.debug("Screenshot data read successfully")

        # Attach to Xray evidence using the report object
        try:
            evidences = getattr(report, "evidences", [])
            evidences.append(evidence.jpeg(data=data, filename=os.path.basename(screenshot_path)))
            report.evidences = evidences
            logger.debug("[EVIDENCE] Xray evidence attached successfully")
        except (AttributeError, TypeError, ValueError) as e:
            logger.error(f"Failed to attach Xray evidence: {e}")

        # Attach to Allure report
        png_file_name = screenshot_path.replace(".jpeg", ".png")
        allure.attach.file(screenshot_path, name=png_file_name, attachment_type=allure.attachment_type.PNG)
        logger.evidence_attached(item.name, "screenshot")
        xray_logger.info("[EVIDENCE] Attached screenshot for failed test: %s", item.name)
    except (FileNotFoundError, PermissionError, IOError) as e:
        logger.error(f"Evidence attachment failed: {e}")
    # Uncomment to enable automatic deletion of screenshots after attachment
    try:
        os.remove(screenshot_path)
        logger.debug(f"Screenshot file {screenshot_path} deleted after attachment.")
    except Exception as cleanup_err:
        logger.error(f"Failed to delete screenshot file {screenshot_path}: {cleanup_err}")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Generate test reports and handle test execution lifecycle events.

    This hook coordinates between different reporting components:
    - Test logging (start/end)
    - Xray test key processing
    - Screenshot capture on failure
    - Evidence attachment for reporting

    Args:
        item: The test item being executed.
        call: The call object containing information about the test phase.

    Yields:
        The test report outcome object.
    """
    outcome = yield
    report = outcome.get_result()
    # Handle test logging
    _handle_test_logging(item, call, report)
    # Process Xray test keys
    _handle_xray_test_keys(item, call)
    # Handle screenshot capture and evidence attachment for failed tests
    if report.when == "call":
        logger.debug(f"Starting evidence collection for test: {item.name}")
        if report.failed:
            screenshot_path = _capture_screenshot(item, report)
            _attach_evidence(item, screenshot_path, report)
    return report


def pytest_collection_modifyitems(config, items):
    """Modify the collected test items based on Xray ID filtering.
    This hook filters test items to run only those marked with specific Xray IDs
    when the --xray-ids command line option is provided. Tests without matching
    Xray markers are deselected.
    Args:
        config: The pytest config object containing command line options.
        items: List of collected test items that can be modified in place.
    """
    xray_ids = config.getoption("--xray-ids")
    if xray_ids:
        xray_id_list = [x.strip() for x in xray_ids.split(",")]
        selected_items = []
        deselected_items = []
        for item in items:
            marker = item.get_closest_marker("xray")
            if marker and marker.args[0] in xray_id_list:
                selected_items.append(item)
            else:
                deselected_items.append(item)
        items[:] = selected_items
        config.hook.pytest_deselected(items=deselected_items)
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options to pytest.
    Registers the --xray-ids option which allows selective test execution
    based on Xray test IDs.
    Args:
        parser: The pytest argument parser to add options to.
    """
    parser.addoption(
        "--xray-ids",
        action="store",
        default=None,
        help="Run tests with specific xray ids (comma-separated)",
    )
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )
    parser.addoption("--env", action="store", default=None, help="Environment to run tests against")
    parser.addoption("--load_type", action="store", default=None, help="Type of load to perform")


@pytest.fixture(scope="function")
def page(page: Page):
    """Provide a browser page fixture for UI tests.
    This fixture initializes a Playwright browser page, navigates to the base URL
    specified in the BASE_URL environment variable, and ensures proper cleanup
    after each test.
    :param page: The Playwright page instance provided by the playwright-pytest plugin.
    :yield: A Playwright page object navigated to the base URL.
    :note:
        The fixture has function scope, meaning a new browser page is created
        for each test function.
    """
    base_url: str = os.getenv("BASE_URL") or ""
    logger.info(f"Navigating to base URL: {base_url}")
    page.goto(base_url)
    yield page
    logger.debug("Closing browser page")
    page.close()
