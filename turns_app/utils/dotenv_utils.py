from dataclasses import fields
from pathlib import Path
from typing import Type

from dotenv import dotenv_values

from turns_app.utils.dataclass_utils import BaseDataclass, BaseDataclassInstance


def config_from_env(file_path: Path, dataclass: Type[BaseDataclass]) -> BaseDataclassInstance:
    """Load configuration from .env file and return a dataclass instance"""
    env = dotenv_values(file_path)
    init_args = {}
    for field in fields(dataclass):
        value = env.get(field.name)

        # Special case for bool fields
        if field.type is bool:
            value = value.lower() in ['true', '1']
        init_args[field.name] = field.type(value)

    return dataclass.from_dict(init_args)
