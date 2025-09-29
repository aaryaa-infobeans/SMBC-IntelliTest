from SRC.pages.login_page import LoginPage
from Utilities.ReportUtils.alure_utils import step
from Utilities.ReportUtils.logger import get_logger
from Utilities.ReportUtils.report_utils import log_step

logger = get_logger()


class LoginHelper:
    def __init__(self, page):
        self.page = page
        self.login_page = LoginPage(page)

    @log_step("Performing Login with username and password")
    def login(self, username: str, password: str, use_password_locator: bool = False):
        """
        Login to the application with given username and password
        :param username: The username to be used for login.
        :param password: The password to be used for login.
        """
        logger.info(f"Logging in with username: {username}")
        self.login_page.enter_username(username)
        logger.info(f"Logging in with password: {password[:3]}...")
        if use_password_locator:
            self.login_page.enter_password(password, use_password_locator)
        else:
            self.login_page.enter_password(password)
        logger.info("Clicking login button")
        self.login_page.click_login()
        logger.info("Login completed successfully")

    @step("Verifying login error message")
    def verify_login_error(self, expected_error: str):
        """
        Verify that the login error message contains the given text.

        :param expected_error: The text that is expected to be present in the error message.
        """
        logger.debug(f"Verifying login error message contains: {expected_error}")
        actual_error = self.login_page.get_error_message()
        assert expected_error in actual_error, f"Expected error: {expected_error}, but got: {actual_error}"
        logger.info(
            f"Login error verification completed successfully. " f"Expected: {expected_error}, Actual: {actual_error}"
        )

    @step("Verifying successful login by checking URL")
    def verify_login_success(self, expected_url: str):
        """
        Verify that the login was successful by checking the current URL.
        :param expected_url: The expected URL after a successful login.
        """
        actual_url = self.page.url
        logger.info(f"Verifying login success with expected URL: {expected_url} | Actual URL: {actual_url}")
        assert actual_url == expected_url, f"Expected URL: {expected_url}, but got: {actual_url}"

    @step("Performing Logout")
    def logout(self):
        """
        Logout from the application.
        """
        logger.info("Clicking logout button")
        self.login_page.click_logout()
        logger.info("Logout completed successfully")

    @step("Verifying successful logout by checking URL")
    def verify_logout_success(self, expected_url: str):
        """
        Verify that the logout was successful by checking the current URL.
        :param expected_url: The expected URL after a successful logout.
        """
        actual_url = self.page.url
        logger.info(f"Verifying logout success with expected URL: {expected_url} | Actual URL: {actual_url}")
        assert actual_url == expected_url, f"Expected URL: {expected_url}, but got: {actual_url}"

    @step("Verifying page title")
    def verify_page_title(self, expected_title: str):
        """
        Verify the page title after login.
        :param expected_title: The expected title of the page.
        """
        actual_title = self.page.title()
        logger.info(f"Verifying page title with expected title: {expected_title} | Actual title: {actual_title}")
        assert actual_title == expected_title, f"Expected title: {expected_title}, but got: {actual_title}"

    @step("Verifying login page elements are present")
    def verify_login_page_elements(self):
        """
        Verify that essential elements on the login page are present.
        """
        logger.info("Verifying login page elements")
        assert self.page.is_visible("text=Swag Labs"), "Login page title is not visible."
        assert self.page.is_visible('input[name="user-name"]'), "Username input field is not visible."
        assert self.page.is_visible('input[name="password"]'), "Password input field is not visible."
        assert self.page.is_visible('input[type="submit"]'), "Login button is not visible."
        logger.info("Login page elements verified successfully")

    def get_current_url(self):
        """Get the current URL."""
        logger.debug("Getting current URL")
        url = self.page.url
        logger.info(f"Current URL: {url}")
        return url
