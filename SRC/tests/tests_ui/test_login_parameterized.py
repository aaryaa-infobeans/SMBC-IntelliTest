import os

import allure
import pytest

from SRC.testbase import TestBase
from Utilities.GenericUtils.file_op_utils import read_csv
from Utilities.TestUtils.test_metadata import annotate_test_metadata

base_url = os.getenv("BASE_URL")


@allure.epic("Login Parameterized")
@pytest.mark.usefixtures("page")
class TestLoginParameterized(TestBase):
    page: None

    @pytest.fixture(autouse=True)
    def setup_method(self, page):
        """
        Setup the test environment.
        """
        super().setup_method(page)

    # @annotate_test_metadata
    # @pytest.mark.xray("MYS-28")
    @pytest.mark.parametrize(
        "username,password,is_valid_user,expected_result",
        [tuple(data.values()) for data in read_csv("TestDataCommon/test_data_csv.csv")],
    )
    def test_parameterized_valid_login(self, username, password, is_valid_user, expected_result):
        """
        Test login functionality with valid and invalid credentials.
        """
        self.login_helper.login(username, password)
        # Convert string to boolean for is_valid_user
        is_valid = is_valid_user.lower() == "true" if isinstance(is_valid_user, str) else is_valid_user

        if is_valid and expected_result == "Success":
            # For successful login, verify we're redirected to inventory page
            expected_url = f"{base_url}inventory.html"
            page_url = self.login_helper.get_current_url()
            assert page_url == expected_url
        else:
            # For failed login, verify error message is displayed
            if username == "locked_out_user":
                self.login_helper.verify_login_error("Epic sadface: Sorry, this user has been locked out.")
            else:
                # Handle other failure cases if needed
                pass
