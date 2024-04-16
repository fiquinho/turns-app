from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class TimeRange:
    start_time: datetime
    end_time: datetime


Day = str  # Format: "DD.MM.YYYY"
TIME_FORMAT = "%H.%M"
DATE_FORMAT = "%d.%m.%Y"
DATETIME_FORMAT = f"{DATE_FORMAT}_{TIME_FORMAT}"


def get_week_by_day(day: datetime) -> TimeRange:
    """Get the week of the given day, starting from Monday"""
    start_of_week = day - timedelta(days=day.weekday())
    end_of_week = start_of_week + timedelta(days=7)
    return TimeRange(start_of_week, end_of_week)


def days_in_range(time_range: TimeRange) -> list[Day]:
    """Get all the days in the given time range"""
    days = []
    current_day = time_range.start_time
    while current_day < time_range.end_time:
        days.append(current_day.strftime(DATE_FORMAT))
        current_day += timedelta(days=1)
    return days
