from copy import deepcopy
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Any

from pymongo import MongoClient

from turns_app.utils.config_utils import MongoConfig
from turns_app.utils.dataclass_utils import BaseDataclass


@dataclass
class TimeRange:
    start_time: datetime
    end_time: datetime


def turn_id_generator(start_time: datetime, office_id: str):
    """Generate unique IDs for turns"""
    date = start_time.date().strftime("%d.%m.%Y")
    time = start_time.time().strftime("%H.%M")
    return f"TURN-{date}-{time}-{office_id}"


@dataclass
class Turn(BaseDataclass):
    idx: str              # Unique identifier

    start_time: datetime  # Turn start time
    end_time: datetime    # Turn end time

    user_id: str          # User unique identifier
    office_id: str        # Office unique identifier


def turn_from_source_dict(values: dict[str, Any]) -> Turn:
    init_dict = deepcopy(values)
    init_dict["start_time"] = datetime.strptime(values["start_date"], "%d.%m.%Y_%H.%M")
    init_dict["end_time"] = datetime.strptime(values["end_date"], "%d.%m.%Y_%H.%M")
    return Turn.from_dict(init_dict)


class MongoTurnsManager:

    def __init__(self, mongo_config: MongoConfig):
        self.mongo_config = mongo_config
        self.client = MongoClient(mongo_config.server, mongo_config.port)
        self.db = self.client[mongo_config.db]
        self.collection = self.db.turns

    def get_turn_by_id(self, turn_id: str) -> Turn:
        turn_dict = self.collection.find_one({"idx": turn_id})
        return Turn.from_dict(turn_dict)

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
    """Get the week of the day given, starting from Monday"""
    start_of_week = day - timedelta(days=day.weekday())
    end_of_week = start_of_week + timedelta(days=7)
    return TimeRange(start_of_week, end_of_week)
