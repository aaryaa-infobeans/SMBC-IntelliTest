import os

import mysql.connector

from Utilities.ReportUtils.logger import get_logger

logger = get_logger()


class BaseDB:
    connection = None
    cursor = None

    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        logger.info("Database connection established successfully")
        self.cursor = self.connection.cursor()

    def close_connection(self):
        try:
            self.connection.close()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Failed to close database connection: {str(e)}")
            raise

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.cursor.commit()
            result = self.cursor.fetchall()
            logger.info("Query executed successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to execute query: {str(e)}")
            raise
