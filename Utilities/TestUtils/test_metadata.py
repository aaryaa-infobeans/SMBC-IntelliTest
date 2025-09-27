import os

import allure
import pandas as pd
import pytest

from Utilities.ReportUtils.logger import get_logger

logger = get_logger()

file_abs_path = os.path.abspath(__file__)
logger.info(f"this is file path for test_metadata.py: {file_abs_path}")
root_dir = file_abs_path.replace(f"Utilities{os.sep}TestUtils{os.sep}test_metadata.py", "")
logger.info(f"this is projectPath dir: {root_dir}")


def get_xray_id(test_func):
    """Helper to extract Xray ID from test function's markers."""
    if hasattr(test_func, "pytestmark"):
        for marker in test_func.pytestmark:
            if marker.name == "xray" and marker.args:
                return marker.args[0]
    return None


def _apply_basic_metadata(test_func, test_metadata):
    """Apply basic Allure metadata to test function."""
    if "feature" in test_metadata and pd.notna(test_metadata["feature"]):
        test_func = allure.feature(test_metadata["feature"])(test_func)
    if "story" in test_metadata and pd.notna(test_metadata["story"]):
        test_func = allure.story(test_metadata["story"])(test_func)
    if "title" in test_metadata and pd.notna(test_metadata["title"]):
        test_func = allure.title(test_metadata["title"])(test_func)
    if "description" in test_metadata and pd.notna(test_metadata["description"]):
        test_func = allure.description(test_metadata["description"])(test_func)
    return test_func


def _apply_severity(test_func, test_metadata):
    """Apply severity metadata to test function."""
    if "severity" in test_metadata and pd.notna(test_metadata["severity"]):
        severity = getattr(allure.severity_level, test_metadata["severity"].upper(), None)
        if severity:
            test_func = allure.severity(severity)(test_func)
    return test_func


def _apply_labels(test_func, test_metadata):
    """Apply label metadata to test function."""
    if "owner" in test_metadata and pd.notna(test_metadata["owner"]):
        test_func = allure.label("owner", str(test_metadata["owner"]))(test_func)
    return test_func


def _apply_tags(test_func, test_metadata):
    """Apply tag metadata to test function."""
    if "tag" in test_metadata and pd.notna(test_metadata["tag"]):
        tags = [tag.strip() for tag in str(test_metadata["tag"]).split(",") if tag.strip()]
        for tag in tags:
            test_func = allure.tag(tag)(test_func)
            test_func = (
                getattr(pytest.mark, tag)(test_func)
                if hasattr(pytest.mark, tag)
                else pytest.mark.__getattr__(tag)(test_func)
            )
    return test_func


def _apply_links(test_func, test_metadata):
    """Apply link metadata to test function."""
    if "link" in test_metadata and pd.notna(test_metadata["link"]):
        link_name = "Jira " + test_metadata["link"].split("/")[-1]
        test_func = allure.link(test_metadata["link"], name=link_name)(test_func)
    return test_func


def _apply_skip_message(test_func, test_metadata):
    """Apply skip message metadata to test function."""
    if "skip_message" in test_metadata and pd.notna(test_metadata["skip_message"]):
        test_func = pytest.mark.skip(reason=test_metadata["skip_message"])(test_func)
    return test_func


def _apply_xfail_message(test_func, test_metadata):
    """Apply xfail message metadata to test function."""
    if "xfail_message" in test_metadata and pd.notna(test_metadata["xfail_message"]):
        test_func = pytest.mark.xfail(reason=test_metadata["xfail_message"])(test_func)
    return test_func


def _load_metadata_from_excel(xray_id):
    """Load test metadata from Excel file based on Xray ID."""
    metadata_path = f"{root_dir}TestDataCommon{os.sep}test_metadata.xlsx"
    logger.info(f"Searching metadata file: {metadata_path}")

    try:
        df = pd.read_excel(metadata_path, engine="openpyxl")
        logger.info("Metadata file read successfully")

        test_metadata = df[df["jira_id"] == xray_id].iloc[0].to_dict()
        logger.info(f"Found metadata for Xray ID {xray_id}")
        return test_metadata
    except Exception as e:
        logger.error(f"Error loading metadata for Xray ID {xray_id}: {str(e)}")
        raise


def annotate_test_metadata(test_func):
    """
    Decorator to apply test metadata from Excel file to test functions.
    The Excel file should be named 'test_metadata.xlsx' in the TestDataCommon directory.
    Looks up test metadata by Jira Xray ID (e.g., MYS-28).
    """
    xray_id = get_xray_id(test_func)
    if not xray_id:
        logger.warning(f"No @pytest.mark.xray('MYS-XXX') marker found for {test_func.__name__}")
        return test_func

    logger.info(f"Processing metadata for {test_func.__name__} with Xray ID: {xray_id}")

    try:
        test_metadata = _load_metadata_from_excel(xray_id)

        # Apply all metadata in sequence
        test_func = _apply_basic_metadata(test_func, test_metadata)
        test_func = _apply_severity(test_func, test_metadata)
        test_func = _apply_labels(test_func, test_metadata)
        test_func = _apply_tags(test_func, test_metadata)
        test_func = _apply_links(test_func, test_metadata)
        test_func = _apply_skip_message(test_func, test_metadata)
        test_func = _apply_xfail_message(test_func, test_metadata)  # Apply xfail message metadata to test function.

    except Exception as e:
        logger.warning(f"Could not load metadata for test {test_func.__name__}: {str(e)}")

    return test_func
