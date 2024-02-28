from datetime import datetime
from dataclasses import dataclass

from turns_app.utils.dataclass_utils import BaseDataclass


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
