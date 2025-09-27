import allure
import pytest

from SRC.testbase import TestBase
from TestDataCommon.test_data import test_data
from Utilities.ReportUtils.logger import get_logger
from Utilities.TestUtils.test_metadata import annotate_test_metadata

logger = get_logger()


@allure.epic("SwagLabs Features")
@pytest.mark.usefixtures("page")
class TestHomePage(TestBase):
    page: None

    @pytest.fixture(autouse=True)
    def set_page(self, page):
        """Set the page instance for the test."""
        self.page = page

    @pytest.fixture(autouse=True)
    def setup_method(self, page):
        """Set up the test environment."""
        super().setup_method(self.page)
        logger.info("Setting up HomePage tests...")
        self.login_helper.login(
            test_data["login"]["valid_credentials"]["username"], test_data["login"]["valid_credentials"]["password"]
        )
        logger.info("Login attempted with valid credentials.")

    @annotate_test_metadata
    @pytest.mark.smoke
    @pytest.mark.xray("MYS-2")
    @allure.label("owner", "swapnil")
    @pytest.mark.dependency(depends=["test_sorting_options"])
    def test_products_displayed(self):
        """Test that products are displayed on the home page."""
        assert self.home_helper.verify_products_displayed(), "No products displayed on the home page."

    @annotate_test_metadata
    @pytest.mark.xray("MYS-3")
    def test_sorting_options(self):
        """Test that sorting options are available on the home page."""
        assert self.home_helper.verify_sorting_options_available(), "Sorting options are not available or insufficient."

    @annotate_test_metadata
    @pytest.mark.xray("MYS-4")
    def test_social_media_links(self):
        """Test that social media links are present on the home page."""
        assert self.home_helper.verify_social_media_links(), "Social media links are not present on the home page."

    @annotate_test_metadata
    @pytest.mark.xray("MYS-5")
    def test_displayed_menu(self):
        """Test that the menu navigation works correctly."""
        # Assuming the HomePageHelper has a method to verify menu navigation
        assert self.home_helper.verify_menus(), "Menu navigation is not functioning as expected."

    @annotate_test_metadata
    @pytest.mark.xray("MYS-6")
    def test_product_details(self):
        """Test that the product details are displayed correctly."""
        assert self.home_helper.verify_product_details(), "Product details are not displayed correctly."
