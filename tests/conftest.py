import json
from pathlib import Path

import pytest

from tests.defaults import TEST_CONFIG_PATH, TEST_TURNS_FILE, TEST_USERS_FILE
from turns_app.model.turns import turn_from_source_dict
from turns_app.model.users import User
from turns_app.utils.config_utils import AppConfig, load_app_config_from_toml


@pytest.fixture
def app_config() -> AppConfig:
    AppConfig.delete_instance()  # type: ignore
    return load_app_config_from_toml(TEST_CONFIG_PATH)


def init_database(config: Path):
    test_config = load_app_config_from_toml(config)
    mongo_config = test_config.mongo

    print("Deleting the test databases...")
    mongo_config.db.drop_collection('turns')
    mongo_config.db.drop_collection('users')

    print('Setting up the test databases...')

    with open(TEST_TURNS_FILE, "r", encoding='utf-8') as f:
        data = json.load(f)
    turns = [turn_from_source_dict(turn) for turn in data]
    mongo_config.db.turns.insert_many([turn.to_dict() for turn in turns])

    with open(TEST_USERS_FILE, "r", encoding='utf-8') as f:
        data = json.load(f)
    users = [User.from_dict(user) for user in data]
    mongo_config.db.users.insert_many([user.to_dict() for user in users])


init_database(TEST_CONFIG_PATH)
