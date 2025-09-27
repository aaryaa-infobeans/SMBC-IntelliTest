from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class CommandHandler:

    def __init__(self):
        self.page = None
        self.COMMAND_DISPATCHER = {
            "playwright_fill": self.handle_fill,
            "playwright_click": self.handle_click,
            "playwright_press": self.handle_press,
            "playwright_select_option": self.handle_select_option,
            "playwright_check": self.handle_check,
            "playwright_uncheck": self.handle_uncheck,
            "playwright_press_sequence": self.handle_press_sequence,
        }

    def handle_fill(self, selector: str, value: str):
        """Fills an input field identified by a selector with a given value."""
        logger.info(f"Filling input field with selector '{selector}' and value '{value}'")
        self.page.locator(selector).fill(value)

    def handle_click(self, selector: str):
        """Clicks an element identified by a selector."""
        logger.info(f"Clicking element with selector '{selector}'")
        self.page.locator(selector).click()

    def handle_press(self, selector: str, key: str):
        """Presses a key on an element identified by a selector (e.g., 'Enter')."""
        logger.info(f"Pressing key '{key}' on element with selector '{selector}'")
        self.page.locator(selector).press(key)

    def handle_select_option(self, selector: str, value: str):
        """Selects an option in a dropdown by its value."""
        logger.info(f"Selecting option '{value}' in dropdown with selector '{selector}'")
        self.page.locator(selector).select_option(value)

    def handle_check(self, selector: str):
        """Checks a checkbox."""
        logger.info(f"Checking checkbox with selector '{selector}'")
        self.page.locator(selector).check()

    def handle_uncheck(self, selector: str):
        """Unchecks a checkbox."""
        logger.info(f"Unchecking checkbox with selector '{selector}'")
        self.page.locator(selector).uncheck()

    def handle_press_sequence(self, selector: str, keys: list[str]):
        """Presses a sequence of keys on an element identified by a selector."""
        logger.info(f"Pressing sequence of keys '{keys}' on element with selector '{selector}'")
        self.page.locator(selector).press_sequentially(keys)
