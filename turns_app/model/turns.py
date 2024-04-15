from copy import deepcopy
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any, TypedDict

from turns_app.utils.config_utils import MongoConfig
from turns_app.utils.dataclass_utils import BaseDataclass


DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H.%M"
DATETIME_FORMAT = f"{DATE_FORMAT}_{TIME_FORMAT}"


Day = str  # Format: "DD.MM.YYYY"


@dataclass
class TimeRange:
    start_time: datetime
    end_time: datetime


def turn_id_generator(start_time: datetime, office_id: str) -> str:
    """Generate unique IDs for turns"""
    date = start_time.date().strftime(DATE_FORMAT)
    time = start_time.time().strftime(TIME_FORMAT)
    return f"TURN-{date}-{time}-{office_id}"


@dataclass
class Turn(BaseDataclass):
    idx: str              # Unique identifier

    start_time: datetime  # Turn start time
    end_time: datetime    # Turn end time

    user_id: str          # User unique identifier
    office_id: str        # Office unique identifier

    def to_str_dict(self) -> dict[str, Any]:
        return {
            "idx": self.idx,
            "start_time": self.start_time.strftime(DATETIME_FORMAT),
            "end_time": self.end_time.strftime(DATETIME_FORMAT),
            "user_id": self.user_id,
            "office_id": self.office_id
        }

    @property
    def duration(self) -> TimeRange:
        return TimeRange(self.start_time, self.end_time)


def turn_from_source_dict(values: dict[str, Any]) -> Turn:
    init_dict = deepcopy(values)
    init_dict["start_time"] = datetime.strptime(values["start_date"], "%d.%m.%Y_%H.%M")
    init_dict["end_time"] = datetime.strptime(values["end_date"], "%d.%m.%Y_%H.%M")
    return Turn.from_dict(init_dict)


class DayTurns(TypedDict):
    turns: list[Turn]
    date: Day


class WeekTurns(TypedDict):
    monday: DayTurns
    tuesday: DayTurns
    wednesday: DayTurns
    thursday: DayTurns
    friday: DayTurns
    saturday: DayTurns
    sunday: DayTurns


class TimeNotAvailableError(Exception):
    pass


class MongoTurnsManager:

    def __init__(self, mongo_config: MongoConfig):
        self.mongo_config = mongo_config
        self.collection = self.mongo_config.db.turns

    def get_turn_by_id(self, turn_id: str) -> Turn:
        turn_dict = self.collection.find_one({"idx": turn_id})
        return Turn.from_dict(turn_dict)

    def insert_turn(self, turn: Turn) -> None:
        if self.collection.find_one({"idx": turn.idx}):
            raise ValueError(f"Turn with ID {turn.idx} already exists.")
        if self.get_turns_in_range(turn.duration):
            raise TimeNotAvailableError(f"Turn time is already taken.")
        self.collection.insert_one(turn.to_dict())

    def get_turns_in_range(self, time_range: TimeRange) -> list[Turn]:
        query = {"$or": [
            # End time between the range
            {"$and": [
                {"end_time": {"$gt": time_range.start_time}},
                {"end_time": {"$lte": time_range.end_time}}
            ]},

            # Start time between the range
            {"$and": [
                {"start_time": {"$gte": time_range.start_time}},
                {"start_time": {"$lt": time_range.end_time}}
            ]},

            # Starts before and ends after the range
            {"$and": [
                {"start_time": {"$lt": time_range.start_time}},
                {"end_time": {"$gt": time_range.end_time}}
            ]}
        ]}

        turns = self.collection.find(query)
        return [Turn.from_dict(turn) for turn in turns]


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


def make_week_dict(turns: list[Turn], week_days: list[Day]) -> WeekTurns:
    week_days_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    week_dict = {day: {"turns": [], "date": date} for day, date in zip(week_days_names, week_days)}
    for turn in turns:

        day = turn.start_time.strftime("%A").lower()
        date = turn.start_time.strftime(DATE_FORMAT)

        if week_dict[day]["date"] != date:
            raise ValueError(f"There are turns from two different weeks in the list. "
                             f"Turns must be from the same week.")

        week_dict[day]["turns"].append(turn)

    return week_dict


def get_week_turns(manager: MongoTurnsManager, day: datetime) -> WeekTurns:
    week = get_week_by_day(day)
    week_days = days_in_range(week)
    turns = manager.get_turns_in_range(week)
    return make_week_dict(turns, week_days)
