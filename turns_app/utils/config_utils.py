import json
from pathlib import Path
from dataclasses import dataclass

from turns_app.utils.dataclass_utils import BaseDataclass


def singleton(cls):
    instances = {}

    def create_instance(*args, **kwargs) -> cls:
        if cls in instances:
            raise ValueError(f"The class {cls} has already been instantiated")

        instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    def get_instance() -> cls:
        if cls not in instances:
            raise ValueError(f"The class {cls} has not been instantiated")

        return instances[cls]

    def check_instance() -> bool:
        return cls in instances

    create_instance.check_instance = check_instance
    create_instance.get_instance = get_instance

    return create_instance


@dataclass
class MongoConfig(BaseDataclass):
    server: str
    db: str
    port: int


@singleton
@dataclass
class AppConfig(BaseDataclass):
    mongo: MongoConfig


def is_app_config_instantiated() -> bool:
    return AppConfig.check_instance()  # type: ignore


def load_app_config_from_json(config_file: Path) -> AppConfig:

    if is_app_config_instantiated():
        raise ValueError("The AppConfig has already been instantiated")

    with open(config_file, "r") as f:
        config = json.load(f)

    init_args = {"mongo": MongoConfig.from_dict(config["mongo_config"])}
    return AppConfig(**init_args)
