import pytest
from datetime import datetime
from turns_app.turns import turn_id_generator, Turn


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
