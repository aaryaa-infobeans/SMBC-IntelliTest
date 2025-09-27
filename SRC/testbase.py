import pytest

from SRC.helpers.home_helper import HomePageHelper
from SRC.helpers.login_helper import LoginHelper
from SRC.helpers.order_helper import OrderHelper
from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


@pytest.mark.usefixtures("page")
class TestBase:
    login_helper = None
    home_helper = None
    order_helper = None

    def setup_method(self, page):
        logger.debug("Setting up test base helpers")
        self.login_helper = LoginHelper(page)
        self.home_helper = HomePageHelper(page)
        self.order_helper = OrderHelper(page)
        logger.debug("Test base setup completed")
