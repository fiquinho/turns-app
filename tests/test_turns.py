import json
from typing import Any
from datetime import datetime

import pytest

from turns_app.turns import turn_id_generator, Turn, turn_from_source_dict, MongoTurnsManager, get_week_by_day, \
    TimeRange, make_week_dict
from turns_app.utils.config_utils import AppConfig, load_app_config_from_json

from tests.data_test_db.test_db_init import TEST_CONFIG_FILE
from tests.defaults import TEST_DATA_DB


TURNS_DATA_FILE = TEST_DATA_DB / 'turns.json'


@pytest.fixture
def app_config() -> AppConfig:
    AppConfig.delete_instance()  # type: ignore
    return load_app_config_from_json(TEST_CONFIG_FILE)


@pytest.fixture
def turn_dict() -> dict[str, Any]:
    return {
        "idx": "TURN-26.02.2024-08.00-OFF_01",
        "start_date": "26.02.2024_08.00",
        "end_date": "26.02.2024_10.00",
        "user_id": "USER_01",
        "office_id": "OFF_01"
    }


@pytest.fixture
def turn(turn_dict) -> Turn:
    return turn_from_source_dict(turn_dict)


@pytest.fixture
def turns_list() -> list[Turn]:
    with open(TURNS_DATA_FILE, 'r') as file:
        turns = json.load(file)
    return [turn_from_source_dict(_turn) for _turn in turns]


def test_turn_id_generator():
    start_time = datetime(2024, 2, 26, 8, 0)
    result = turn_id_generator(start_time, 'office_id')
    assert result == 'TURN-26.02.2024-08.00-office_id'


def test_turn_generation():

    turn = Turn(
        idx='TURN-26.02.2024-08.00-office_id',
        start_time=datetime(2024, 2, 26, 8, 0),
        end_time=datetime(2024, 2, 26, 10, 00),
        user_id='USER_01',
        office_id='OFF_01'
    )
    assert turn.idx == 'TURN-26.02.2024-08.00-office_id'
    assert turn.start_time == datetime(2024, 2, 26, 8, 0)
    assert turn.end_time == datetime(2024, 2, 26, 10, 00)
    assert turn.user_id == 'USER_01'
    assert turn.office_id == 'OFF_01'


def test_turn_from_source_dict(turn_dict):
    turn = turn_from_source_dict(turn_dict)
    assert turn.idx == 'TURN-26.02.2024-08.00-OFF_01'
    assert turn.start_time == datetime(2024, 2, 26, 8, 0)
    assert turn.end_time == datetime(2024, 2, 26, 10, 0)
    assert turn.user_id == 'USER_01'
    assert turn.office_id == 'OFF_01'


def test_turns_manager(app_config, turn):
    manger = MongoTurnsManager(app_config.mongo)

    result = manger.get_turn_by_id(turn.idx)
    assert result == turn


def test_turns_manager_range(app_config, turns_list):
    manger = MongoTurnsManager(app_config.mongo)

    start_time = datetime(2024, 2, 26, 8, 0)
    end_time = datetime(2024, 2, 27, 14, 0)
    time_range = TimeRange(start_time, end_time)

    result = manger.get_turns_in_range(time_range)
    assert result == turns_list

    start_time = datetime(2024, 2, 26, 9, 0)
    end_time = datetime(2024, 2, 27, 13, 30)
    time_range = TimeRange(start_time, end_time)

    result = manger.get_turns_in_range(time_range)
    assert result == turns_list

    start_time = datetime(2024, 2, 26, 9, 0)
    end_time = datetime(2024, 2, 26, 9, 30)
    time_range = TimeRange(start_time, end_time)

    result = manger.get_turns_in_range(time_range)
    assert result == [result[0]]


def test_get_week_by_day():
    week_start = datetime(2024, 2, 26)
    week_end = datetime(2024, 3, 4)

    day = datetime(2024, 2, 27)
    result = get_week_by_day(day)
    assert result.start_time == week_start
    assert result.end_time == week_end


def test_make_week_dict(turns_list):
    result = make_week_dict(turns_list)
    assert len(result) == 7
    assert 'monday' in result
    assert 'tuesday' in result
    assert 'wednesday' in result
    assert 'thursday' in result
    assert 'friday' in result
    assert 'saturday' in result
    assert 'sunday' in result
    assert 'turns' in result['monday']
    assert 'date' in result['monday']
    assert len(result['monday']['turns']) == 3
    assert result['monday']['date'] == '26.02.2024'
    assert len(result['tuesday']['turns']) == 2

    assert isinstance(result['tuesday']['turns'][0], Turn)
