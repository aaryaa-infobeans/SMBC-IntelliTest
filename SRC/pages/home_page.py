import os

from playwright.sync_api import Page, expect

from SRC.base.base_page import BasePage
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class HomePage(BasePage):

    __loc_products_container = ".inventory_list"
    __loc_product_items = ".inventory_item"
    __loc_sort_dropdown = ".product_sort_container"
    __loc_sort_options = "option"
    __loc_hamburger_menu = ".bm-burger-button"
    __loc_footer_copy = ".footer_copy"
    __loc_add_to_cart_buttons = "//*[@class='inventory_item' and (.//*[text()='$'])]//button"

    def __init__(self, page: Page):
        super().__init__(page)
        self.url = os.getenv("BASE_URL")

    def navigate(self):
        """Navigate to the home page."""
        logger.debug(f"Navigating to home page: {self.url}")
        self.page.goto(self.url)
        logger.info(f"Successfully navigated to home page: {self.url}")

    def get_title(self):
        """Get the page title."""
        logger.debug("Getting page title")
        title = self.page.title()
        logger.info(f"Retrieved page title: {title}")
        return title

    def get_current_url(self):
        """Get the current URL."""
        logger.debug("Getting current URL")
        url = self.page.url
        logger.info(f"Current URL: {url}")
        return url

    def get_products(self):
        """Get all product elements."""
        logger.debug("Getting all product elements")
        products = self.page.query_selector_all(self.__loc_product_items)
        logger.info(f"Found {len(products)} product elements")
        return products

    def get_sort_dropdown(self):
        """Get the sort dropdown element."""
        logger.debug("Getting sort dropdown element")
        dropdown = self.page.query_selector(self.__loc_sort_dropdown)
        if dropdown:
            logger.info("Sort dropdown element found")
        else:
            logger.warning("Sort dropdown element not found")
        return dropdown

    def get_sort_options(self):
        """Get all sort option elements."""
        logger.debug("Getting sort option elements")
        dropdown = self.get_sort_dropdown()
        options = dropdown.query_selector_all(self.__loc_sort_options) if dropdown else []
        logger.info(f"Found {len(options)} sort options")
        return options

    def open_hamburger_menu(self):
        logger.debug("Opening hamburger menu")
        self.page.click(self.__loc_hamburger_menu)
        logger.info("Successfully opened hamburger menu")

    def verify_menu_item(self, menu):
        """verify a menu item from the hamburger menu."""
        logger.debug(f"Verifying menu item: {menu}")
        menu_element = len(self.page.locator(f'//a[text()="{menu}"]').all())
        logger.debug(f"Menu found with count: {menu_element}")
        result = menu_element > 0
        logger.info(f"Menu item '{menu}' verification {'passed' if result else 'failed'}")
        return result

    def get_footer_text(self):
        """Get the footer text."""
        logger.debug("Retrieving footer text")
        footer = self.page.locator(self.__loc_footer_copy)
        logger.debug(f"Footer element found: {footer.count()}")
        if footer:
            logger.info("Successfully retrieved footer element")
        else:
            logger.warning("Footer element not found")
        return footer if footer else None

    def add_to_card_item(self, product, qty):
        """Add a specified quantity of a product to the cart."""
        logger.step(f"Adding {qty} of {product} to the cart")
        add_to_cart_buttons = self.page.locator(self.__loc_add_to_cart_buttons)
        try:
            add_to_cart_buttons.click()
            logger.info(f"Successfully clicked add to cart button for {product}")
            return True
        except (TimeoutError, RuntimeError) as e:
            logger.error(f"Failed to add {product} to cart: {str(e)}")
            logger.warning(f"Product {product} not found")
            return False

    def verify_product_is_displayed(self, product):
        """Verify that a product is displayed on the home page."""
        logger.debug(f"Verifying product: {product}")
        product_element = self.page.locator(".inventory_item_name").filter(has_text=product)
        try:
            expect(product_element).to_be_visible()
            logger.info(f"Product '{product}' is displayed")
            return True
        except Exception as e:
            logger.error(f"Failed to verify product '{product}': {str(e)}")
            logger.warning(f"Product '{product}' is not displayed")
        return False

    def verify_product_price_is_displayed(self, price):
        logger.info(f"Verifying product price: {price}")
        price_element = self.page.locator(
            "//div[./div/a/div[text()='Sauce Labs Backpack']]//div[@cla ss='inventory_item_price']"
        ).filter(has_text=price)
        try:
            expect(price_element).to_be_visible()
            logger.info(f"Product price '{price}' is displayed")
            return True
        except Exception as e:
            logger.error(f"Failed to verify product price '{price}': {str(e)}")
            logger.warning(f"Product price '{price}' is not displayed")
        return False
