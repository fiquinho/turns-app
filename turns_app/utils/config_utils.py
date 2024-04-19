import toml
from pathlib import Path
from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.database import Database

from turns_app.utils.dataclass_utils import BaseDataclass


def singleton(cls):
    instances = {}

    def create_instance(*args, **kwargs) -> cls:
        if cls in instances:
            raise ValueError(f"The class {cls} has already been instantiated")

        instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    def from_dict(values: dict[str, any]) -> cls:
        if cls in instances:
            raise ValueError(f"The class {cls} has already been instantiated")

        instances[cls] = cls.from_dict(values)
        return instances[cls]

    def get_instance() -> cls:
        if cls not in instances:
            raise ValueError(f"The class {cls} has not been instantiated")

        return instances[cls]

    def check_instance() -> bool:
        return cls in instances

    def delete_instance() -> None:
        if cls in instances:
            del instances[cls]

    create_instance.check_instance = check_instance
    create_instance.get_instance = get_instance
    create_instance.delete_instance = delete_instance
    create_instance.from_dict = from_dict

    return create_instance


@dataclass
class MongoConfig(BaseDataclass):
    server: str
    db_name: str
    port: int

    @property
    def client(self) -> MongoClient:
        return MongoClient(self.server, self.port)

    @property
    def db(self) -> Database:
        return self.client[self.db_name]


@dataclass
class BusinessConfig(BaseDataclass):
    name: str
    start_time: str         # Format: "HH.MM"
    end_time: str           # Format: "HH.MM"
    min_module_time: int    # In minutes
    offices: list[str]


@singleton
@dataclass
class AppConfig(BaseDataclass):
    mongo: MongoConfig
    business: BusinessConfig


def is_app_config_instantiated() -> bool:
    return AppConfig.check_instance()  # type: ignore


def load_app_config_from_toml(config_file: Path) -> AppConfig:

    if is_app_config_instantiated():
        raise ValueError("The AppConfig has already been instantiated")

    # Open toml file and load the configuration
    with open(config_file, "r") as f:
        config = toml.load(f)

    return AppConfig.from_dict(config)
