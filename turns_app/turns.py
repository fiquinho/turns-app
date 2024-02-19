from dataclasses import dataclass

from turns_app.utils.dataclass_utils import BaseDataclass


def turn_id_generator(date: str, time: str, office_id: str):
    """Generate unique IDs for turns"""
    prefix = 'TURN-'
    return f"{prefix}{date}-{time}-{office_id}"


@dataclass
class Turn(BaseDataclass):
    idx: str        # Unique identifier

    # TODO: Implement better date
    date: str       # DD.MM.YYYY
    time: str       # HH:MM
    day: str
    duration: int   # minutes

    user_id: str    # User unique identifier
    office_id: str  # Office unique identifier
