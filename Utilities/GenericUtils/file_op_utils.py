# file_utils.py
import csv
import json
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml


def read_json(file_path: str) -> dict:
    """
    Read a JSON file and return its contents as a dictionary.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(file_path: str, data: dict):
    """
    Write a dictionary to a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def read_csv(file_path: str) -> list:
    """
    Read a CSV file and return its contents as a list of dictionaries.
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(file_path: str, data: list, fieldnames: list):
    """
    Write a list of dictionaries to a CSV file.
    """
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def read_excel(file_path: str, sheet: Optional[str] = None) -> pd.DataFrame:
    """
    Read an Excel file and return its contents as a pandas DataFrame.
    """
    return pd.read_excel(file_path, sheet_name=sheet)


def write_excel(file_path: str, df: pd.DataFrame, sheet: str = "Sheet1"):
    """
    Write a pandas DataFrame to an Excel file.
    """
    df.to_excel(file_path, sheet_name=sheet, index=False)


def read_text(file_path: str) -> str:
    """
    Read a text file and return its contents as a string.
    """
    return Path(file_path).read_text(encoding="utf-8")


def write_text(file_path: str, content: str):
    """
    Write a string to a text file.
    """
    Path(file_path).write_text(content, encoding="utf-8")


def read_yaml(file_path: str) -> dict:
    """
    Read a YAML file and return its contents as a dictionary.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(file_path: str, data: dict):
    """
    Write a dictionary to a YAML file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, indent=2)
