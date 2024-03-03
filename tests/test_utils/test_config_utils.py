from dataclasses import dataclass

import pytest

from turns_app.utils.dataclass_utils import BaseDataclass
from turns_app.utils.config_utils import singleton, load_app_config_from_json, AppConfig, MongoConfig
from tests.defaults import TEST_CONFIG_PATH


@singleton
@dataclass
class TestConfig(BaseDataclass):
    arg_1: str
    arg_2: int
    arg_3: bool


def test_singleton():

    assert TestConfig.check_instance() is False  # type: ignore

    with pytest.raises(ValueError):
        TestConfig.get_instance()  # type: ignore

    config = TestConfig("test", 1, True)

    assert TestConfig.check_instance() is True  # type: ignore
    assert config.arg_1 == "test"
    assert config.arg_2 == 1
    assert config.arg_3 is True

    with pytest.raises(ValueError):
        TestConfig("other_test", 2, False)

    other_config = TestConfig.get_instance()  # type: ignore
    assert other_config is config
    assert other_config.arg_1 == "test"
    assert other_config.arg_2 == 1
    assert other_config.arg_3 is True

    other_config.arg_1 = "other_test"
    assert other_config.arg_1 == "other_test"
    assert config.arg_1 == "other_test"

    third_config = TestConfig.get_instance()  # type: ignore
    assert third_config is config
    assert third_config.arg_1 == "other_test"
    assert third_config.arg_2 == 1
    assert third_config.arg_3 is True


def test_app_config():
    assert AppConfig.check_instance() is False  # type: ignore

    app_config = load_app_config_from_json(TEST_CONFIG_PATH)
    assert isinstance(app_config.mongo, MongoConfig)
    assert app_config.mongo.server == "localhost"
    assert app_config.mongo.db == "turns_app-test"
    assert app_config.mongo.port == 27017

    with pytest.raises(ValueError):
        load_app_config_from_json(TEST_CONFIG_PATH)

    assert AppConfig.check_instance() is True  # type: ignore
    assert AppConfig.get_instance() == app_config  # type: ignore

    other_config = AppConfig.get_instance()  # type: ignore
    assert other_config == app_config

    app_config.mongo.server = "other_server"
    assert app_config.mongo.server == "other_server"
    assert other_config.mongo.server == "other_server"
