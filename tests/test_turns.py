import pytest
from turns_app.turns import turn_id_generator, Turn


def test_turn_id_generator():

    result = turn_id_generator('26.02.2024', '08.00', 'office_id')
    assert result == 'TURN-26.02.2024-08.00-office_id'


def test_turn_generation():

    turn = Turn(
        idx='TURN-26.02.2024-08.00-office_id',
        date='26.02.2024',
        time='08.00',
        day='Monday',
        duration=60,
        user_id='USER_01',
        office_id='OFF_01'
    )
    assert turn.idx == 'TURN-26.02.2024-08.00-office_id'
    assert turn.date == '26.02.2024'
    assert turn.time == '08.00'
    assert turn.day == 'Monday'
    assert turn.duration == 60
    assert turn.user_id == 'USER_01'
    assert turn.office_id == 'OFF_01'
