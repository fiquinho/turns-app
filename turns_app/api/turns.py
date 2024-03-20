import datetime

from flask import Blueprint, request, current_app
from flask_restx import Resource, fields, Api

from turns_app.turns import get_week_by_day, DATE_FORMAT, order_by_day
from turns_app.utils.flask_utils import ApiState


turns_api_blueprint = Blueprint('turns_api', __name__, url_prefix='/turns')
turns_api_extension = Api(
    turns_api_blueprint,
    title='Turns API',
    version='0.1',
    description='Turns API for the turns service',
    doc='/doc'
)

day_model = turns_api_extension.model('Day', {
    "day": fields.String(required=True, description="Day as string. Format: 'DD.MM.YYYY'")
})
week_turns_model = turns_api_extension.model('WeekTurns', {
    "start_day": fields.String(required=True, description="Start day of the week as string. Format: 'DD.MM.YYYY'"),
    "end_day": fields.String(required=True, description="End day of the week as string. Format: 'DD.MM.YYYY'"),
    # Dictionary of turns by day
    "turns": fields.Raw(required=True, description="Dictionary of turns by day")
})


@turns_api_extension.route('/get_week', methods=['GET'])
class GetWeek(Resource):

    @turns_api_extension.expect(day_model)
    @turns_api_extension.marshal_with(week_turns_model)
    def get(self):
        api_state: ApiState = current_app.config["api_config"]
        db_manager = api_state.db_manager

        request_data = request.get_json()
        day_str: str = request_data.get('day')
        formatted_day = datetime.datetime.strptime(day_str, DATE_FORMAT)

        week = get_week_by_day(formatted_day)
        end_day = week.end_time - datetime.timedelta(days=1)
        turns = db_manager.get_turns_in_range(week)
        week_turns = order_by_day(turns)

        return {'start_day': week.start_time.strftime(DATE_FORMAT),
                'end_day': end_day.strftime(DATE_FORMAT),
                'turns': week_turns}
