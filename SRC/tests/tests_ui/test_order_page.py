import allure
import pytest

from SRC.testbase import TestBase
from TestDataCommon.test_data import test_data
from Utilities.ReportUtils.logger import get_logger
from Utilities.TestUtils.test_metadata import annotate_test_metadata

logger = get_logger()


@allure.epic("Order Processing")
@pytest.mark.usefixtures("page")
class TestOrderPage(TestBase):
    page: None

    @pytest.fixture(autouse=True)
    def setup_method(self, page):
        """Set up the test environment."""
        super().setup_method(page)
        logger.info("Setting up OrderPage tests...")
        self.login_helper.login(
            test_data["login"]["valid_credentials"]["username"], test_data["login"]["valid_credentials"]["password"]
        )
        logger.info("Login attempted with valid credentials, navigating to all items page.")

    @annotate_test_metadata
    @pytest.mark.xray("MYS-13", defects=["MYS-55"])
    def test_order_creation(self):
        """Test that an order can be created successfully."""
        order_success = self.order_helper.create_order(
            test_data["order"]["product_name"], test_data["order"]["quantity"]
        )
        assert order_success, "Order creation failed."
