from copy import deepcopy
from datetime import datetime
from dataclasses import dataclass
from typing import Any, TypedDict

from turns_app.utils.config_utils import MongoConfig
from turns_app.utils.dataclass_utils import BaseDataclass
from turns_app.utils.mongo_utils import turns_in_range_query
from turns_app.utils.time_utils import TimeRange, Day, TIME_FORMAT, DATETIME_FORMAT, DATE_FORMAT, get_week_by_day, \
    days_in_range


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
    init_dict["start_time"] = datetime.strptime(values["start_date"], DATETIME_FORMAT)
    init_dict["end_time"] = datetime.strptime(values["end_date"], DATETIME_FORMAT)
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


class TurnNotAvailableError(Exception):
    pass


class MongoTurnsManager:

    def __init__(self, mongo_config: MongoConfig):
        self.mongo_config = mongo_config
        self.collection = self.mongo_config.db.turns

    def get_turn_by_id(self, turn_id: str) -> Turn:
        turn_dict = self.collection.find_one({"idx": turn_id})
        return Turn.from_dict(turn_dict)

    def conflict_turn(self, turn: Turn) -> Turn | None:
        query = {"$or": [
            {"$and": [turns_in_range_query(turn.duration),
                      {"user_id": turn.user_id}]},
            {"$and": [turns_in_range_query(turn.duration),
                      {"office_id": turn.office_id}]}
        ]}
        conflict = self.collection.find_one(query)
        if conflict:
            return Turn.from_dict(conflict)
        return None

    # TODO: Are exceptions the best way to handle this?
    def insert_turn(self, turn: Turn) -> None:
        conflict = self.conflict_turn(turn)
        if conflict:
            if conflict.user_id == turn.user_id:
                raise TurnNotAvailableError(f"User {turn.user_id} has a turn at the same time.")
            if conflict.office_id == turn.office_id:
                raise TurnNotAvailableError(f"Office {turn.office_id} has a turn at the same time.")

        self.collection.insert_one(turn.to_dict())

    def get_turns_in_range(self, time_range: TimeRange) -> list[Turn]:
        query = turns_in_range_query(time_range)

        turns = self.collection.find(query)
        return [Turn.from_dict(turn) for turn in turns]


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
