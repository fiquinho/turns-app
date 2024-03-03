import json

from pymongo import MongoClient

from tests.defaults import TEST_DATA_DB
from turns_app.defaults import CONFIGS_PATH
from turns_app.turns import turn_from_dict
from turns_app.utils.config_utils import load_app_config_from_json

TEST_CONFIG_FILE = CONFIGS_PATH / "app_config.test.json"
TEST_DATA_FILE = TEST_DATA_DB / "turns.json"


def main():

    test_config = load_app_config_from_json(TEST_CONFIG_FILE)
    mongo_config = test_config.mongo

    client = MongoClient(mongo_config.server, mongo_config.port)
    db = client[mongo_config.db]

    print("Deleting the test database...")
    db.drop_collection('turns')

    print('Setting up the test database...')

    with open(TEST_DATA_FILE, "r") as f:
        data = json.load(f)

    turns = [turn_from_dict(turn) for turn in data]

    db.turns.insert_many([turn.to_dict() for turn in turns])


if __name__ == '__main__':
    main()
