import json
from datetime import datetime
from pathlib import Path


class TestdataUtil:
    """
    TestdataUtil class for reading test data from a test data file.
    """

    testdata: dict
    testdata_file: Path

    def __init__(self, testdata_file):
        self.testdata_file = Path(testdata_file)

    def get_testdata(self):
        """
        Read test data from a test data file.
        """
        with open(self.testdata_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_testdata_by_key(self, key):
        """
        Get test data by key.
        """
        return self.testdata.get(key)

    def get_testdata_by_keys(self, keys):
        """
        Get test data by keys.
        """
        return {key: self.testdata.get(key) for key in keys}

    def get_current_date(self):
        """
        Get current date.
        """
        return datetime.now().strftime("%Y-%m-%d")

    def get_current_time(self):
        """
        Get current time.
        """
        return datetime.now().strftime("%H:%M:%S")

    def get_current_datetime(self):
        """
        Get current date and time.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_time_data(self, date_time: str, time_format: str = "%Y-%m-%d %H:%M:%S"):
        """
        Get time data.
        """
        return datetime.strptime(date_time, time_format)

    def get_time_diff(self, start_time: str, end_time: str, format_: str = "%Y-%m-%d %H:%M:%S"):
        """
        Get time difference.
        """
        return (datetime.strptime(end_time, format_) - datetime.strptime(start_time, format_)).total_seconds()
