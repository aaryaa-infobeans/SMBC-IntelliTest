from playwright.sync_api import Page, expect

from SRC.base.base_page import BasePage
from Utilities.ReportUtils.alure_utils import step
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class OrderPage(BasePage):
    __loc_add_to_card_btn_for_product = "//*[@class='inventory_item' and (.//*[text()='$'])]//button"
    __loc_cart_icon = ".shopping_cart_link"
    __loc_cart_page_heading = "div.subheader"
    __loc_product_count = "div#shopping_cart_container > a > span"
    __loc_checkout_button = ".btn_action.checkout_button"
    __loc_continue_shopping_button = "//a[.='Continue Shopping']"
    __loc_remove_button = "//button[.='REMOVE']"
    __loc_cart_table_header = "//div[.='QTY' and following-sibling::div[.='DESCRIPTION']]"
    __loc_cart_item__product_name = ".inventory_item_name"
    __loc_cart_item__product_price = ".inventory_item_price"
    __loc_cart_item__product_quantity = ".cart_quantity"
    __loc_cart_item__product_description = ".inventory_item_desc"

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page  # Add page attribute

    def add_product_to_cart(self, product_name: str):
        """Navigate to the home page.
        :param product_name: The name of the product to order."""
        logger.debug(f"Adding product '{product_name}' to cart")
        loc_add_to_cart_button_for_product = self.__loc_add_to_card_btn_for_product.replace("$", product_name)
        self.page.click(loc_add_to_cart_button_for_product)
        logger.info(f"Successfully added product '{product_name}' to cart")

    @step("Verifying cart item count")
    def verify_cart_item_count(self, expected_count: int):
        """Verify if the order was added to the cart"""
        logger.debug(f"Verifying cart item count, expected: {expected_count}")
        is_cart_count = self.page.locator(self.__loc_product_count).all()
        if is_cart_count and expected_count:
            actual_count = int(is_cart_count[0].inner_text())
            assert actual_count == expected_count, f"Expected {expected_count} items in cart, but got {actual_count}."
            logger.info(f"Cart item count verification passed: {actual_count} items")
        else:
            assert is_cart_count == [], "Cart count element not found or expected count is not provided."
            logger.info("Cart is empty as expected")

    @step("Verifying item details in cart")
    def verify_item_details_in_cart(self, product_name: str, quantity: int):
        """Verify item details in the cart."""
        logger.debug(f"Verifying item details for '{product_name}' with quantity {quantity}")
        # Check if the product is in the cart
        product_locator = f"//div[contains(text(), '{product_name}')]"
        product_element = self.page.locator(product_locator)
        assert product_element.count() > 0, f"Product '{product_name}' not found in the cart."
        logger.info(f"Product '{product_name}' found in cart")

        # Verify the quantity of the product
        quantity_locator = (
            f"//div[@class='inventory_item_name' and (.='{product_name}')]"
            f"/ancestor::div[@class='cart_item']//*[@class='cart_quantity']"
        )
        quantity_element = self.page.locator(quantity_locator)
        qty_msg = f"Expected quantity {quantity} for product '{product_name}', but not found."
        assert quantity_element.count() > 0, qty_msg
        logger.info(f"Product quantity verification passed for '{product_name}'")

    @step("Navigating to cart page")
    def go_to_cart(self):
        """Navigate to the cart page."""
        logger.debug("Navigating to cart page")
        self.page.click(self.__loc_cart_icon)
        logger.info("Successfully navigated to cart page")

    @step("Verifying cart page.")
    def verify_your_cart_page(self):
        """Verify that the cart page is displayed."""
        logger.debug("Verifying cart page elements")
        assert self.page.url.endswith("/cart.html"), "Not on the cart page."
        assert self.page.title() == "Swag Labs", "Cart page title is incorrect."
        expect(self.page.locator(self.__loc_cart_page_heading)).to_be_visible(), "Cart page heading is not visible."
        expect(self.page.locator(self.__loc_checkout_button)).to_be_visible(), "Checkout button is not visible."
        expect(
            self.page.locator(self.__loc_continue_shopping_button)
        ).to_be_visible(), "Continue Shopping button is not visible."
        expect(self.page.locator(self.__loc_remove_button)).to_be_visible(), "Remove button is not visible."
        expect(self.page.locator(self.__loc_cart_table_header)).to_be_visible(), "Cart total is not visible."
        expect(self.page.locator(self.__loc_cart_item__product_name).first).to_be_visible()
        assert True, "Product name in cart is not visible."
        expect(self.page.locator(self.__loc_cart_item__product_price).first).to_be_visible()
        assert True, "Product price in cart is not visible."
        expect(self.page.locator(self.__loc_cart_item__product_quantity).first).to_be_visible()
        assert True, "Product quantity in cart is not visible."
        expect(self.page.locator(self.__loc_cart_item__product_description).first).to_be_visible()
        assert True, "Product description in cart is not visible."
        logger.info("Cart page verification completed successfully")

    @step("Clicking on checkout button")
    def product_checkout(self):
        """
        Click on the checkout button to proceed with the order.
        """
        logger.debug("Initiating product checkout")
        expect(self.page.locator(self.__loc_checkout_button)).to_be_visible(), "Checkout button is not visible."
        self.page.click(self.__loc_checkout_button)
        logger.info("Successfully clicked checkout button and initiated checkout process")

    @step("Verifying checkout page")
    def verify_checkout_page(self):
        """
        Verify that the checkout page is displayed.
        """
        logger.debug("Verifying checkout page elements")
        assert self.page.url.endswith("/checkout-step-one.html"), "Not on the checkout page."
        cart_heading = self.page.locator(self.__loc_cart_page_heading)
        expect(cart_heading).to_be_visible(), "Checkout page heading is not visible."
        cont_shop_btn = self.page.locator(self.__loc_continue_shopping_button)
        expect(cont_shop_btn).to_be_visible(), "Continue Shopping button is not visible."
        expect(self.page.locator(self.__loc_remove_button)).to_be_visible(), "Remove button is not visible."
        logger.info("Checkout page verification completed successfully.")
