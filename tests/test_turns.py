import json
from typing import Any
from datetime import datetime

import pytest

from tests.defaults import TEST_DATA_DB
from turns_app.turns import turn_id_generator, Turn, turn_from_dict


TURNS_DATA_FILE = TEST_DATA_DB / 'turns.json'


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
    return turn_from_dict(turn_dict)


@pytest.fixture
def turns_list() -> list[Turn]:
    with open(TURNS_DATA_FILE, 'r') as file:
        turns = json.load(file)
    return [turn_from_dict(_turn) for _turn in turns]


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


def test_turn_from_dict(turn_dict):
    turn = turn_from_dict(turn_dict)
    assert turn.idx == 'TURN-26.02.2024-08.00-OFF_01'
    assert turn.start_time == datetime(2024, 2, 26, 8, 0)
    assert turn.end_time == datetime(2024, 2, 26, 10, 0)
    assert turn.user_id == 'USER_01'
    assert turn.office_id == 'OFF_01'
