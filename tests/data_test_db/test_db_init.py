import argparse
import json
from pathlib import Path

from pymongo import MongoClient

from tests.defaults import TEST_CONFIG_PATH, TEST_TURNS_FILE
from turns_app.model.turns import turn_from_source_dict
from turns_app.utils.config_utils import load_app_config_from_toml


def init_database(config: Path, data_file: Path):
    test_config = load_app_config_from_toml(config)
    mongo_config = test_config.mongo

    client = MongoClient(mongo_config.server, mongo_config.port)
    db = client[mongo_config.db]

    print("Deleting the test database...")
    db.drop_collection('turns')

    print('Setting up the test database...')

    with open(data_file, "r") as f:
        data = json.load(f)

    turns = [turn_from_source_dict(turn) for turn in data]

    db.turns.insert_many([turn.to_dict() for turn in turns])


def main():
    parser = argparse.ArgumentParser(description="Setup a test or dev database")
    parser.add_argument(
        "--config",
        type=str,
        default=TEST_CONFIG_PATH,
        help="The path to the configuration file"
    )
    parser.add_argument(
        "--data",
        type=str,
        default=TEST_TURNS_FILE,
        help="The path to the data file"
    )
    args = parser.parse_args()

    config = Path(args.config)
    data = Path(args.data)

    init_database(config, data)


if __name__ == '__main__':
    main()
