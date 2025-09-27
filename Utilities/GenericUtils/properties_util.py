import ast
import configparser
from pathlib import Path

from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class PropertiesUtil:
    """
    PropertiesUtil class for reading properties from a properties file.
    """

    properties: dict
    properties_file: Path

    def __init__(self, properties_file):
        self.properties_file = Path(properties_file)

    def get_properties(self):
        """
        Read properties from a properties file.
        """
        logger.info(f"Reading properties from file: {self.properties_file}")
        parser = configparser.ConfigParser()
        # Trick: ConfigParser needs section headers
        with open(self.properties_file, "r", encoding="utf-8") as f:
            file_content = "[DEFAULT]\n" + f.read()
        parser.read_string(file_content)
        data = {k: ast.literal_eval(v) for k, v in parser["DEFAULT"].items()}
        logger.info(f"data fetched from {self.properties_file} is \n{data}")
        return data
