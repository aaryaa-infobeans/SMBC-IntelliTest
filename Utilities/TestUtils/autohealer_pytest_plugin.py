"""
Pytest plugin for AutoHealer GitHub PR integration.
This plugin automatically creates PRs for locator fixes at the end of test execution.
"""

import pytest
from typing import Optional

from Utilities.ReportUtils.logger import get_logger
from Utilities.TestUtils.auto_healer import create_pr_for_session_fixes, get_autohealer_pr_manager

logger = get_logger()


class AutoHealerPRPlugin:
    """Pytest plugin for AutoHealer PR creation."""
    
    def __init__(self):
        self.pr_manager = get_autohealer_pr_manager()
        self.fixes_collected = 0
        
    def pytest_configure(self, config):
        """Called after command line options have been parsed."""
        if self.pr_manager and self.pr_manager.is_running_in_github_actions():
            logger.info("AutoHealer pytest plugin initialized for GitHub Actions")
        
    def pytest_sessionstart(self, session):
        """Called after the Session object has been created."""
        if self.pr_manager and self.pr_manager.is_configured():
            logger.info("AutoHealer session started - collecting locator fixes")
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Called after whole test run finished."""
        if not self.pr_manager or not self.pr_manager.is_configured():
            return
            
        fixes_count = len(self.pr_manager.locator_fixes)
        
        if fixes_count > 0:
            logger.info(f"Test session finished. Found {fixes_count} locator fixes to create PR for")
            
            try:
                pr_url = create_pr_for_session_fixes()
                if pr_url:
                    logger.info(f"✅ AutoHealer PR created successfully: {pr_url}")
                    # Add a summary comment to the test output
                    print(f"\n🔧 AutoHealer created PR with {fixes_count} locator fixes: {pr_url}")
                else:
                    logger.warning("❌ Failed to create AutoHealer PR")
                    
            except Exception as e:
                logger.error(f"Error creating AutoHealer PR: {str(e)}")
        else:
            logger.info("No locator fixes collected during test session")
    
    def pytest_runtest_logreport(self, report):
        """Called for each test report (setup, call, teardown)."""
        # This could be used to track test-specific information if needed
        pass


# Register the plugin
autohealer_plugin = AutoHealerPRPlugin()


def pytest_configure(config):
    """Register the AutoHealer plugin."""
    config.pluginmanager.register(autohealer_plugin, "autohealer_pr_plugin")


def pytest_sessionstart(session):
    """Session start hook."""
    autohealer_plugin.pytest_sessionstart(session)


def pytest_sessionfinish(session, exitstatus):
    """Session finish hook."""
    autohealer_plugin.pytest_sessionfinish(session, exitstatus)


def pytest_runtest_logreport(report):
    """Test report hook."""
    autohealer_plugin.pytest_runtest_logreport(report)
