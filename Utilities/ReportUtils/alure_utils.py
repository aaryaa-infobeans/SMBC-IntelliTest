import os
import traceback
from pathlib import Path

import allure
import pytest
from allure_commons.types import AttachmentType


class AllurePytestReporter:
    """Allure reporter for attaching screenshots, tracebacks, and step descriptions."""

    def __init__(self, screenshot_dir: str = "screenshots"):
        self.screenshot_dir = screenshot_dir
        Path(self.screenshot_dir).mkdir(parents=True, exist_ok=True)

    def attach_screenshot(self, screenshot_path: str = ""):
        """Attach screenshot to failed test."""
        try:
            if not screenshot_path:
                # Find latest screenshot
                screenshots = list(Path(self.screenshot_dir).glob("*.png"))
                if screenshots:
                    screenshot_path = str(max(screenshots, key=os.path.getctime))

            if screenshot_path and os.path.exists(screenshot_path):
                with open(screenshot_path, "rb") as img:
                    allure.attach(img.read(), name="Failure Screenshot", attachment_type=AttachmentType.PNG)
        except Exception as e:
            allure.step(f"Failed to attach screenshot: {str(e)}")

    def attach_traceback(self, exc_info):
        """Attach full traceback to failed test."""
        if exc_info:
            tb_str = "".join(traceback.format_exception(*exc_info))
            allure.attach(tb_str, name="Traceback", attachment_type=AttachmentType.TEXT)

    def handle_failure(self, item, call):
        """Handle test failure by attaching screenshot and traceback."""
        if call.excinfo:
            self.attach_traceback(call.excinfo)

            # Attach screenshot for UI tests
            if "tests_ui" in str(item.fspath):
                self.attach_screenshot()


# Pytest hooks
def pytest_configure(config):
    """Initialize Allure reporter."""
    config._allure_reporter = AllurePytestReporter()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test failures and attach details."""
    outcome = yield
    report = outcome.get_result()

    if report.failed and hasattr(item.config, "_allure_reporter"):
        item.config._allure_reporter.handle_failure(item, call)


# Step decorator for method descriptions
def step(description: str):
    """
    Decorator for marking methods as Allure steps.

    Usage:
        @step("Performing Login")
        def login(self, username, password):
            pass
    """

    def decorator(func):
        @allure.step(description)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
