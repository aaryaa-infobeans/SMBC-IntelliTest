import os

from playwright.sync_api import Page

from Utilities.ReportUtils.logger import get_logger
from Utilities.TestUtils.auto_healer import AutoHealer

logger = get_logger()


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.healer = AutoHealer(page)
        logger.info("AutoHealer initialized with OpenAI integration")

    def fill(self, selector: str, value: str, timeout: int = 5000, description: str = "input field"):
        try:
            logger.debug(f"Entering text:'{value}' to element '{selector}'")

            # Try with AutoHealer first
            element = self.healer.getElement(selector, description)
            if element:
                element.fill(value)
                logger.info(f"Successfully filled element '{selector}' using AutoHealer")
                return True

            # Fallback to original method if healer fails
            el = self.page.wait_for_selector(selector, timeout=timeout)
            assert el is not None, f"Element '{selector}' not found for fill."
            el.fill(value)
            logger.info(f"Successfully filled element '{selector}' using fallback")
            return True
        except Exception as e:
            logger.error(f"Fill action failed for '{selector}': {str(e)}")
            raise AssertionError(f"Fill action failed for '{selector}': {str(e)}") from e

    def click(self, selector: str, timeout: int = 5000, description: str = "clickable element"):
        try:
            logger.debug(f"Clicking element '{selector}'")

            # Try with AutoHealer first - it handles healing internally
            element = self.healer.getElement(selector, description)
            if element:
                element.click()
                logger.info(f"Successfully clicked element '{selector}' using AutoHealer")
                return True
            else:
                # If AutoHealer returns None, it means all healing attempts failed
                logger.error(
                    f"AutoHealer could not locate element '{description}' with locator '{selector}' after all healing attempts"
                )
                raise AssertionError(
                    f"Element '{description}' not found with locator '{selector}' even after AI healing attempts"
                )

        except Exception as e:
            logger.error(f"Click action failed for '{selector}': {str(e)}")
            raise AssertionError(f"Click action failed for '{selector}': {str(e)}") from e

    def text_content(self, selector: str, timeout: int = 5000, description: str = "text element") -> str:
        try:
            logger.debug(f"Getting text content from element '{selector}'")

            # Try with AutoHealer first
            element = self.healer.getElement(selector, description)
            if element:
                text = element.text_content()
                if text is not None:
                    logger.info(f"Successfully retrieved text content from element '{selector}' using AutoHealer")
                    return text

            # Fallback to original method if healer fails
            el = self.page.wait_for_selector(selector, timeout=timeout)
            assert el is not None, f"Element '{selector}' not found for text_content."
            text = el.text_content()
            assert text is not None, f"No text content found for selector'{selector}'."
            logger.info(f"Successfully retrieved text content from element '{selector}' using fallback")
            return text
        except Exception as e:
            logger.error(f"text_content action failed for '{selector}': {str(e)}")
            raise AssertionError(f"text_content action failed for '{selector}': {str(e)}") from e

    def set_value_from_dropdown(self, loc_dropdown: str, value_or_option_or_index, input_typ: str = "value"):
        try:
            logger.info(f"Selecting value '{value_or_option_or_index}' from dropdown '{loc_dropdown}'")
            el = self.page.wait_for_selector(loc_dropdown)
            assert el is not None, f"Element '{loc_dropdown}' not found for set_value_from_dropdown."
            el.click()
            if input_typ == "value":
                self.page.select_option(loc_dropdown, value=value_or_option_or_index)
            elif input_typ == "option":
                self.page.select_option(loc_dropdown, label=value_or_option_or_index)
            elif input_typ == "index":
                self.page.select_option(loc_dropdown, index=int(value_or_option_or_index))
            logger.info(f"Successfully selected value '{value_or_option_or_index}' from dropdown '{loc_dropdown}'")
        except Exception as e:
            logger.error(f"set_value_from_dropdown action failed for '{loc_dropdown}': {str(e)}")
            raise AssertionError(f"set_value_from_dropdown action failed for '{loc_dropdown}': {str(e)}") from e
