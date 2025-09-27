import os

from SRC.pages.home_page import HomePage
from Utilities.GenericUtils.properties_util import PropertiesUtil
from Utilities.ReportUtils.alure_utils import step
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class HomePageHelper:
    def __init__(self, page):
        self.home_page = HomePage(page)

    @step("Verifying page title")
    def verify_page_title(self):
        """Verify the home page title is correct."""
        logger.debug("Verifying home page title")
        actual_title = self.home_page.get_title()
        expected_title = "Swag Labs"
        result = actual_title == expected_title
        status = "passed" if result else "failed"
        logger.info(f"Page title verification {status}: Expected '{expected_title}', Got '{actual_title}'")
        return result

    @step("Verifying page URL")
    def verify_page_url(self):
        """Verify the home page URL is correct."""
        logger.debug("Verifying home page URL")
        actual_url = self.home_page.get_current_url()
        expected_url = self.home_page.url
        result = actual_url == expected_url
        status = "passed" if result else "failed"
        logger.info(f"Page URL verification {status}: Expected '{expected_url}', Got '{actual_url}'")
        return result

    @step("Verifying products displayed")
    def verify_products_displayed(self):
        """Verify products are displayed on the home page."""
        logger.step("Verifying products displayed on the home page")
        products = self.home_page.get_products()
        logger.info(f"Number of products found: {len(products)}")
        return len(products) > 0

    @step("Verifying sorting options")
    def verify_sorting_options_available(self):
        """Verify sorting options are available on the home page."""
        logger.debug("Verifying sorting options availability")
        sort_dropdown = self.home_page.get_sort_dropdown()
        if not sort_dropdown:
            logger.info("Sorting options verification failed: No dropdown found")
            return False
        options = self.home_page.get_sort_options()
        result = len(options) > 1
        logger.info(f"Sorting options verification {'passed' if result else 'failed'}: Found {len(options)} options")
        return result

    @step("Verifying social media links")
    def verify_social_media_links(self):
        """Verify social media links are present on the home page."""
        logger.debug("Verifying social media links presence")
        social_links = self.home_page.page.query_selector_all('li[class*="social"]')
        result = len(social_links) > 0
        status = "passed" if result else "failed"
        logger.info(f"Social media links verification {status}: Found {len(social_links)} links")
        return result

    @step("Verifying menu navigation")
    def verify_menus(self):
        """Verify that the menu navigation works correctly."""
        logger.debug("Verifying menu navigation functionality")
        lhs_menus = ["All Items", "About", "Logout", "Reset App State"]
        self.home_page.open_hamburger_menu()
        menu_displayed = False
        for menu in lhs_menus:
            menu_displayed = self.home_page.verify_menu_item(menu)
        logger.info(f"Menu navigation verification {'passed' if menu_displayed else 'failed'}")
        return menu_displayed

    @step("Getting footer text")
    def get_footer_text(self):
        """Get the footer text from the home page."""
        logger.debug("Getting footer text from home page")
        footer = self.home_page.get_footer_text()
        if footer:
            footer_text = footer.inner_text()
            logger.info(f"Successfully retrieved footer text: {footer_text[:50]}...")
            return footer_text
        logger.warning("Footer text not found")
        return ""

    @step("Verifying product details")
    def verify_product_details(self):
        """
        Verify that the product details are displayed correctly.
        """
        logger.info("Verifying product details")
        properties_util = PropertiesUtil(f"TestDataCommon{os.sep}sauce_lab.properties")
        product_details = properties_util.get_properties()
        products_list = [*product_details["products_list"]]
        product_price_list = [*product_details["product_price_list"]]
        for product in products_list:
            self.home_page.verify_product_is_displayed(product)
        for product_price in product_price_list:
            self.home_page.verify_product_price_is_displayed(product_price)
        return True
