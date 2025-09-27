import os

import allure
import pytest

from SRC.testbase import TestBase
from TestDataCommon.test_data import test_data
from Utilities.GenericUtils.retry_utils import retry
from Utilities.TestUtils.test_metadata import annotate_test_metadata

base_url = os.getenv("BASE_URL")


@allure.epic("SwagLabs access")
@pytest.mark.usefixtures("page")
class TestLogin(TestBase):
    page = None

    @pytest.fixture(autouse=True)
    def setup_method(self, page):
        """
        Setup the test environment.
        """
        super().setup_method(page)

    @annotate_test_metadata
    @pytest.mark.xray("MYS-7")
    def test_valid_login(self):
        """
        Test valid login functionality.
        Jira Test Case: MYS-3 - Verify the user can login with valid creds
        """
        self.login_helper.login(
            test_data["login"]["valid_credentials"]["username"], test_data["login"]["valid_credentials"]["password"]
        )
        self.login_helper.verify_login_success(base_url + "inventory.html")

    @annotate_test_metadata
    @pytest.mark.xray("MYS-12")
    @retry(max_attempts=3, delay=1)
    def test_logout(self):
        """
        Test logout functionality.
        """
        self.login_helper.login(
            test_data["login"]["valid_credentials"]["username"], test_data["login"]["valid_credentials"]["password"]
        )
        self.login_helper.logout()
        self.login_helper.verify_logout_success(base_url + "/index.html")

    @annotate_test_metadata
    @pytest.mark.xray("MYS-11")
    def test_page_title(self):
        """
        Test the page title after login.
        """
        self.login_helper.login(
            test_data["login"]["valid_credentials"]["username"], test_data["login"]["valid_credentials"]["password"]
        )
        self.login_helper.verify_page_title("Swag Labs")

    @annotate_test_metadata
    @pytest.mark.slow
    @pytest.mark.xray("MYS-8")
    @pytest.mark.slow
    def test_login_page_elements(self):
        """
        Test that essential elements on the home page are present.
        """
        self.page.goto(base_url)
        assert self.page.is_visible('input[name="user-name"]')
        assert self.page.is_visible('input[name="password"]')
        assert self.page.is_visible('input[type="submit"]')

    @annotate_test_metadata
    @pytest.mark.xray("MYS-9")
    def test_invalid_login(self):
        """
        Test invalid login functionality.
        """
        self.login_helper.login(
            test_data["login"]["invalid_credentials"]["username"], test_data["login"]["invalid_credentials"]["password"]
        )
        self.login_helper.verify_login_error("Epic sadface: Sorry, this user has been locked out")

    @annotate_test_metadata
    @pytest.mark.xray("MYS-10")
    def test_problem_user_login(self):
        """
        Test login with problem user credentials.
        """
        self.login_helper.login(
            test_data["login"]["problem_user"]["username"], test_data["login"]["problem_user"]["password"]
        )
        self.login_helper.verify_login_success(base_url + "inventory.html")
