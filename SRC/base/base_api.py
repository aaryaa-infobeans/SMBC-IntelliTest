import os
import time

import requests

from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class BaseApi:
    session: requests.Session

    @staticmethod
    def request_time_tracker(func):
        """
        Decorator to track the time taken by a request.
        """

        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            logger.info(f"Request time taken by {func.__name__}: {end_time - start_time}")
            return result

        return wrapper

    def __init__(self, url: str = ""):
        """
        Initialize the BaseApi class.
        """
        if not url:
            self.base_url = os.getenv("BASE_URL")
        else:
            self.base_url = url

    def create_session(self):
        """
        Create a session for the API.
        """
        self.session = requests.Session()
        logger.info("Session created successfully")
        return self.session

    def update_headers(self, headers: dict):
        """
        Update the headers for the session.
        """
        self.session.headers.update(headers)

    def make_request(self, method, endpoint, **kwargs):
        """
        Make a request to the API.
        """
        request_dict = {
            "GET": self.__get_request,
            "POST": self.__post_request,
            "PUT": self.__put_request,
            "PATCH": self.__patch_request,
            "DELETE": self.__delete_request,
        }
        try:
            logger.info(f"Making {method} request to {endpoint}, with kwargs: {kwargs}")
            request_func = request_dict.get(method.upper())
            if not request_func:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response = request_func(endpoint, **kwargs)
            if response.status_code >= 400:
                logger.error(f"Request failed with status code {response.status_code} and error {response.text}")
            else:
                logger.info(f"Request made successfully: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Failed to make request: {str(e)}")
            raise

    @request_time_tracker
    def __get_request(self, endpoint, **kwargs):
        try:
            response = self.session.get(f"{self.base_url}{endpoint}", **kwargs)
            logger.info(f"GET request made successfully: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Failed to make GET request: {str(e)}")
            raise

    @request_time_tracker
    def __post_request(self, endpoint, **kwargs):
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", **kwargs)
            logger.info(f"POST request made successfully: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Failed to make POST request: {str(e)}")
            raise

    @request_time_tracker
    def __patch_request(self, endpoint, **kwargs):
        try:
            response = self.session.patch(f"{self.base_url}{endpoint}", **kwargs)
            logger.info(f"PATCH request made successfully: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Failed to make PATCH request: {str(e)}")
            raise

    @request_time_tracker
    def __delete_request(self, endpoint, **kwargs):
        try:
            response = self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
            logger.info(f"DELETE request made successfully: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Failed to make DELETE request: {str(e)}")
            raise

    @request_time_tracker
    def __put_request(self, endpoint, **kwargs):
        try:
            response = self.session.put(f"{self.base_url}{endpoint}", **kwargs)
            logger.info(f"PUT request made successfully: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Failed to make PUT request: {str(e)}")
            raise

    @request_time_tracker
    def close_session(self):
        try:
            self.session.close()
            logger.info("Session closed successfully")
        except Exception as e:
            logger.error(f"Failed to close session: {str(e)}")
            raise
