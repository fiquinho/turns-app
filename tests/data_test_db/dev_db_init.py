import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from tests.defaults import TEST_USERS_FILE
from turns_app.defaults import CONFIGS_PATH
from turns_app.model.turns import Turn, turn_id_generator, MongoTurnsManager, TurnNotAvailableError
from turns_app.utils.time_utils import TimeRange, Day, DATETIME_FORMAT, get_week_by_day, days_in_range
from turns_app.model.users import User
from turns_app.utils.config_utils import load_app_config_from_toml, AppConfig, BusinessConfig

DEV_CONFIG_FILE = CONFIGS_PATH / "app_config.dev.toml"


def day_modules(day: Day, bc: BusinessConfig) -> list[TimeRange]:
    """Get the time ranges for each module in a day"""
    modules = []
    current_time = datetime.strptime(f"{day}_{bc.start_time}", DATETIME_FORMAT)
    day_end_time = datetime.strptime(f"{day}_{bc.end_time}", DATETIME_FORMAT)
    while current_time < day_end_time:
        end_time = current_time + timedelta(minutes=bc.min_module_time)
        modules.append(TimeRange(current_time, end_time))
        current_time = end_time
    return modules


def random_turn_time(bc: BusinessConfig, day: Day) -> TimeRange:
    modules = day_modules(day, bc)
    start_module = random.randint(0, len(modules) - 1)
    length = random.randint(0, 4)
    end_module = start_module + length
    if end_module >= len(modules):
        end_module = len(modules) - 1

    start_time = modules[start_module].start_time
    end_time = modules[end_module].end_time
    return TimeRange(start_time, end_time)


def init_database(config: Path):
    dev_config: AppConfig = load_app_config_from_toml(config)
    mongo_config = dev_config.mongo
    business_config = dev_config.business

    print("Deleting the dev database...")
    mongo_config.db.drop_collection('turns')
    mongo_config.db.drop_collection('users')

    print('Setting up the users dev database...')
    with open(TEST_USERS_FILE, "r", encoding='utf-8') as f:
        data = json.load(f)
    users = [User.from_dict(user) for user in data]
    mongo_config.db.users.insert_many([user.to_dict() for user in users])
    users_ids = [user.id for user in users]

    print('Setting up the turns dev database...')
    turns_manager = MongoTurnsManager(mongo_config)

    now = datetime.now()
    week_range = get_week_by_day(now)
    week_days = days_in_range(week_range)

    # Generate random turns for the week.
    total = 40
    generated = 0
    while generated < total:
        day = random.choice(week_days)
        time_range = random_turn_time(business_config, day)
        user = random.choice(users_ids)
        office = random.choice(business_config.offices)

        turn = Turn(idx=turn_id_generator(time_range.start_time, office),
                    user_id=user,
                    office_id=office,
                    start_time=time_range.start_time,
                    end_time=time_range.end_time)

        try:
            turns_manager.insert_turn(turn)
            generated += 1
        except TurnNotAvailableError:
            continue


def main():
    parser = argparse.ArgumentParser(description="Setup a test or dev database")
    parser.add_argument(
        "--config",
        type=str,
        default=DEV_CONFIG_FILE,
        help="The path to the configuration file"
    )
    args = parser.parse_args()

    config = Path(args.config)

    init_database(config)


if __name__ == '__main__':
    main()
