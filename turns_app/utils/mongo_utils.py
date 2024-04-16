from turns_app.utils.time_utils import TimeRange


def turns_in_range_query(time_range: TimeRange) -> dict:
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
    return query
