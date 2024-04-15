import json

import pytest

from tests.defaults import TEST_CONFIG_PATH, TEST_TURNS_FILE, TEST_USERS_FILE
from turns_app.model.turns import turn_from_source_dict
from turns_app.model.users import User
from turns_app.utils.config_utils import AppConfig, load_app_config_from_toml


def get_test_config() -> AppConfig:
    AppConfig.delete_instance()  # type: ignore
    return load_app_config_from_toml(TEST_CONFIG_PATH)


@pytest.fixture
def test_config() -> AppConfig:
    return get_test_config()


def init_database(config):
    mongo_config = config.mongo

    mongo_config.db.drop_collection('turns')
    mongo_config.db.drop_collection('users')

    with open(TEST_TURNS_FILE, "r", encoding='utf-8') as f:
        data = json.load(f)
    turns = [turn_from_source_dict(turn) for turn in data]
    mongo_config.db.turns.insert_many([turn.to_dict() for turn in turns])

    with open(TEST_USERS_FILE, "r", encoding='utf-8') as f:
        data = json.load(f)
    users = [User.from_dict(user) for user in data]
    mongo_config.db.users.insert_many([user.to_dict() for user in users])


init_database(get_test_config())
