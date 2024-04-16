from datetime import datetime

from turns_app.utils.time_utils import get_week_by_day, days_in_range


def test_get_week_by_day():
    week_start = datetime(2024, 2, 26)
    week_end = datetime(2024, 3, 4)

    day = datetime(2024, 2, 27)
    result = get_week_by_day(day)
    assert result.start_time == week_start
    assert result.end_time == week_end


def test_days_in_range():
    day = datetime(2024, 2, 27)
    week_range = get_week_by_day(day)
    result = days_in_range(week_range)

    assert len(result) == 7
    assert result[0] == "26.02.2024"
    assert result[1] == "27.02.2024"
    assert result[-1] == "03.03.2024"
