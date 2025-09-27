# add script to fetch and return environment variables
import os
from typing import Optional


def get_env_variable(var_name: str) -> Optional[str]:
    return os.getenv(var_name)


def set_env_variable(var_name: str, var_value: str) -> None:
    os.environ[var_name] = var_value


def delete_env_variable(var_name: str) -> None:
    del os.environ[var_name]
