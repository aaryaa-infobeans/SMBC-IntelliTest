import json

import allure

from SRC.base.base_api import BaseApi
from Utilities.ReportUtils.logger import get_logger
from Utilities.TestUtils.faker_singleton import FAKER_SINGLETON

logger = get_logger()


@allure.epic("Weather API")
class TestBookersApi:
    booking_id: str = ""
    token: str = ""  # nosec - This is just a placeholder token for testing # nosec
    initial_booking_payload: dict = {}
    updated_booking_payload: dict = {}
    session = None
    base_url = ""
    base_api = None

    def setup_method(self):
        """Setup method for TestBookersApi."""
        self.base_url = "https://restful-booker.herokuapp.com"
        self.base_api = BaseApi(self.base_url)
        self.base_api.create_session()
        self.base_api.update_headers({"Content-Type": "application/json"})

    def teardown_method(self):
        """Teardown method for TestBookersApi."""
        self.base_api.close_session()

    # @pytest.mark.xray("MYS-84")
    # @allure.feature("Bookers API")
    # @pytest.mark.api
    # @pytest.mark.smoke
    # @allure.tag("smoke")
    # @allure.story("Verify Successful Authentication")
    # @allure.title("MYS-84: Verify that successful authentication with valid credentials works correctly.")
    # @allure.description("Verify that successful authentication with valid credentials works correctly.")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @allure.label("owner", "swapnil")
    # @allure.link("https://sauce1100.atlassian.net/browse/MYS-84", name="Jira MYS-84")
    def test_booker_api(self):
        """
        Test the authentication API.
        """
        self.base_api.create_session()  # Create session using BaseApi
        payload = json.dumps({"username": "admin", "password": "password123"})
        headers = {"Content-Type": "application/json"}
        # Use BaseApi's make_request method
        response = self.base_api.make_request("POST", "/auth", headers=headers, data=payload, timeout=30)
        TestBookersApi.token = response.json()["token"]
        # logger.info(self.token, "this is token")
        assert response.status_code == 200

        self.base_api.close_session()  # Close session properly

    # @pytest.mark.xray("MYS-85")
    # @allure.feature("Bookers API")
    # @pytest.mark.api
    # @pytest.mark.smoke
    # @pytest.mark.regression
    # @allure.tag("smoke")
    # @allure.story("Verify Successful Booking Creation")
    # @allure.title("MYS-85: Verify that successful booking creation works correctly.")
    # @allure.description("Verify that successful booking creation works correctly.")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @allure.label("owner", "swapnil")
    # @allure.link("https://sauce1100.atlassian.net/browse/MYS-85", name="Jira MYS-85")
    # @pytest.mark.dependency(name="TestBookersApi::test_create_booking")
    def test_create_booking(self):
        """
        Test the booking creation API.

        """
        self.initial_booking_payload = json.dumps(
            {
                "firstname": FAKER_SINGLETON.first_name(),
                "lastname": FAKER_SINGLETON.last_name(),
                "totalprice": FAKER_SINGLETON.random_int(),
                "depositpaid": FAKER_SINGLETON.boolean(),
                "bookingdates": {"checkin": FAKER_SINGLETON.date(), "checkout": FAKER_SINGLETON.date()},
                "additionalneeds": FAKER_SINGLETON.text(),
            }
        )

        # Use BaseApi's make_request method
        response = self.base_api.make_request("POST", "/booking", data=self.initial_booking_payload, timeout=30)
        print(response.text)
        TestBookersApi.booking_id = response.json()["bookingid"]
        logger.info(f"Booking ID: {TestBookersApi.booking_id}")
        assert TestBookersApi.booking_id is not None
        assert response.status_code == 200

    # @pytest.mark.xray("MYS-86")
    # @pytest.mark.skip("Skipping this test")
    # @allure.feature("Bookers API")
    # @pytest.mark.api
    # @pytest.mark.smoke
    # @pytest.mark.regression
    # @allure.tag("smoke", "regression")
    # @allure.story("Verify Successful Booking Retrieval")
    # @allure.title("MYS-86: Verify that successful booking retrieval works correctly.")
    # @allure.description("Verify that successful booking retrieval works correctly.")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @allure.label("owner", "swapnil")
    # @allure.link("https://sauce1100.atlassian.net/browse/MYS-86", name="Jira MYS-86")
    def test_get_booking(self):
        """
        Test the booking retrieval API.

        """
        # Use BaseApi's make_request method
        response = self.base_api.make_request("GET", "/booking", timeout=30)
        assert response.status_code == 200

    # @pytest.mark.dependency(depends=["TestBookersApi::test_create_booking"])
    # @pytest.mark.xray("MYS-87")
    # @pytest.mark.smoke
    # @pytest.mark.api
    # @pytest.mark.regression
    # @allure.feature("Bookers API")
    # @allure.tag("smoke", "regression")
    # @allure.story("Verify Successful Booking Update")
    # @allure.title("MYS-87: Verify that successful booking update works correctly.")
    # @allure.description("Verify that successful booking update works correctly.")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @allure.label("owner", "swapnil")
    # @allure.link("https://sauce1100.atlassian.net/browse/MYS-87", name="Jira MYS-87")
    def test_update_booking(self):
        """
        Test the booking update API.
        """
        self.updated_booking_payload = json.dumps(
            {
                "firstname": "James",
                "lastname": "Brown",
                "totalprice": 111,
                "depositpaid": True,
                "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
                "additionalneeds": "Breakfast",
            }
        )
        self.base_api.update_headers({"Cookie": f"token={TestBookersApi.token}", "Accept": "application/json"})
        # headers = {"Cookie": cookies, "Accept": "application/json", "Content-Type": "application/json"}
        logger.info(f"Updating the booking with Booking ID: {TestBookersApi.booking_id}")
        # Use BaseApi's make_request method
        response = self.base_api.make_request(
            "PUT", f"/booking/{TestBookersApi.booking_id}", timeout=30, data=self.updated_booking_payload
        )
        assert response.status_code == 200
        # verify updated booking total price
        assert response.json()["totalprice"] == 111
