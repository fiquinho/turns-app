import json
from typing import Any
from datetime import datetime

import pytest

from tests.conftest import init_database
from tests.data_test_db.dev_db_init import day_modules
from turns_app.model.turns import turn_id_generator, Turn, turn_from_source_dict, MongoTurnsManager, make_week_dict, \
    TurnNotAvailableError
from turns_app.utils.time_utils import TimeRange, get_week_by_day, days_in_range

from tests.defaults import TEST_TURNS_FILE
from turns_app.utils.config_utils import BusinessConfig


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
    with open(TEST_TURNS_FILE, 'r') as file:
        turns = json.load(file)
    return [turn_from_source_dict(_turn) for _turn in turns]


def test_turn_id_generator():
    start_time = datetime(2024, 2, 26, 8, 0)
    result = turn_id_generator(start_time, 'office_id')
    assert result == 'TURN-26.02.2024-08.00-office_id'


def test_turn_generation():

    turn = Turn(
        idx='TURN-26.02.2024-08.00-OFF_01',
        start_time=datetime(2024, 2, 26, 8, 0),
        end_time=datetime(2024, 2, 26, 10, 0),
        user_id='USER_01',
        office_id='OFF_01'
    )
    assert turn.idx == 'TURN-26.02.2024-08.00-OFF_01'
    assert turn.start_time == datetime(2024, 2, 26, 8, 0)
    assert turn.end_time == datetime(2024, 2, 26, 10, 0)
    assert turn.user_id == 'USER_01'
    assert turn.office_id == 'OFF_01'


def test_turn_from_source_dict(turn_dict):
    turn = turn_from_source_dict(turn_dict)
    assert turn.idx == 'TURN-26.02.2024-08.00-OFF_01'
    assert turn.start_time == datetime(2024, 2, 26, 8, 0)
    assert turn.end_time == datetime(2024, 2, 26, 10, 0)
    assert turn.user_id == 'USER_01'
    assert turn.office_id == 'OFF_01'


def test_turns_manager(test_config, turn):
    manger = MongoTurnsManager(test_config.mongo)

    result = manger.get_turn_by_id(turn.idx)
    assert result == turn


def test_turns_manager_range(test_config, turns_list):
    init_database(test_config)
    manger = MongoTurnsManager(test_config.mongo)

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


def test_turns_manager_insert(test_config):
    manger = MongoTurnsManager(test_config.mongo)
    turn = Turn(
        idx='TURN-26.02.2024-16.00-OFF_01',
        start_time=datetime(2024, 2, 26, 16, 0),
        end_time=datetime(2024, 2, 26, 19, 0),
        user_id='USER_01',
        office_id='OFF_01'
    )
    manger.insert_turn(turn)

    result = manger.get_turn_by_id(turn.idx)
    assert result == turn

    conflict_office_turn = Turn(
        idx='XXXX',
        start_time=datetime(2024, 2, 26, 18, 0),
        end_time=datetime(2024, 2, 26, 19, 0),
        user_id='OTHER_USER',
        office_id='OFF_01'
    )
    with pytest.raises(TurnNotAvailableError):
        manger.insert_turn(conflict_office_turn)

    conflict_user_turn = Turn(
        idx='XXXX',
        start_time=datetime(2024, 2, 26, 18, 0),
        end_time=datetime(2024, 2, 26, 19, 0),
        user_id='USER_01',
        office_id='OTHER_OFFICE'
    )
    with pytest.raises(TurnNotAvailableError):
        manger.insert_turn(conflict_user_turn)


def test_make_week_dict(turns_list):
    week_days = days_in_range(get_week_by_day(turns_list[0].start_time))

    result = make_week_dict(turns_list, week_days)
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


def test_day_modules(turns_list):
    bc = BusinessConfig(name='Test', start_time="08.00", end_time="18.00", min_module_time=30, offices=["OFF_01"])
    modules = day_modules("26.02.2024", bc)
    assert len(modules) == 20
    assert modules[0].start_time == datetime(2024, 2, 26, 8, 0)
    assert modules[0].end_time == datetime(2024, 2, 26, 8, 30)
    assert modules[-1].start_time == datetime(2024, 2, 26, 17, 30)
    assert modules[-1].end_time == datetime(2024, 2, 26, 18, 0)
    assert modules[10].start_time == datetime(2024, 2, 26, 13, 0)
    assert modules[10].end_time == datetime(2024, 2, 26, 13, 30)
    assert modules[19].start_time == datetime(2024, 2, 26, 17, 30)
    assert modules[19].end_time == datetime(2024, 2, 26, 18, 0)
