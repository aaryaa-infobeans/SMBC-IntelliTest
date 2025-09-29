from playwright.sync_api import Page

from SRC.base.base_page import BasePage
from Utilities.ReportUtils.alure_utils import step
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class LoginPage(BasePage):

    __loc_username_input = "#user-name"
    __loc_password_input = "input[type='password']"  # nosec - This is a CSS selector, not a real password
    __loc_login_button = "#login-button"
    __loc_error_message = "//h3[text()]"
    __loc_logout_button = '//button[contains(text(), "Logout")]'

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page  # Add page attribute

    @step("Entering username.")
    def enter_username(self, username: str):
        """Fill the username input field with the provided username.
        :param username: The username to be entered.
        """
        logger.debug(f"Entering username: {username}")
        self.fill(self.__loc_username_input, username, description="username input field")
        logger.info("Successfully entered username")

    @step("Entering password")
    def enter_password(self, password: str):
        """Fill the password input field with the provided password.
        :param password: The password to be entered.
        """
        logger.debug("Entering password")
        self.fill(self.__loc_password_input, password, description="password input field")
        logger.info("Successfully entered password")

    @step("Clicking login button")
    def click_login(self):
        """Click the login button to submit the login form.
        :return: True if the login was successful, False otherwise.
        """
        logger.debug("Clicking login button")
        self.click(self.__loc_login_button, description="login submit button")
        logger.info("Successfully clicked login button")
        return True

    @step("Getting error message")
    def get_error_message(self):
        """Retrieve the error message text displayed on the login page.
        :return: The error message text.
        """
        logger.debug("Retrieving error message")
        error_message = self.text_content(self.__loc_error_message, description="login error message")
        logger.info(f"Retrieved error message: {error_message}")
        return error_message

    @step("Clicking logout button")
    def click_logout(self):
        """Click the logout button to log out of the application."""
        logger.debug("Initiating logout process")
        self.page.get_by_role("button", name="Open menu").click()
        logger.debug("Opened menu for logout")
        self.click(self.__loc_logout_button, description="logout button")
        logger.info("Successfully completed logout process")
