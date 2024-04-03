import datetime

from flask import Blueprint, request, current_app
from flask_restx import Resource, fields, Api

from turns_app.turns import DATE_FORMAT, get_week_turns
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

turn_model = turns_api_extension.model('Turn', {
    "idx": fields.String(required=True, description="Turn unique identifier"),
    "start_time": fields.String(required=True, description="Turn start time"),
    "end_time": fields.String(required=True, description="Turn end time"),
    "user_id": fields.String(required=True, description="User unique identifier"),
    "office_id": fields.String(required=True, description="Office unique identifier")
})
turns_list_model = turns_api_extension.model('TurnsList', {
    "turns": fields.List(fields.Nested(turn_model), required=True, description="List of turns"),
    "date": fields.String(required=True, description="Date as string. Format: 'DD.MM.YYYY'")
})
week_turns_model = turns_api_extension.model('WeekTurns', {
    # Dict with day name as key and turns_list_model as value
    "monday": fields.Nested(turns_list_model, required=True, description="Monday turns"),
    "tuesday": fields.Nested(turns_list_model, required=True, description="Tuesday turns"),
    "wednesday": fields.Nested(turns_list_model, required=True, description="Wednesday turns"),
    "thursday": fields.Nested(turns_list_model, required=True, description="Thursday turns"),
    "friday": fields.Nested(turns_list_model, required=True, description="Friday turns"),
    "saturday": fields.Nested(turns_list_model, required=True, description="Saturday turns"),
    "sunday": fields.Nested(turns_list_model, required=True, description="Sunday turns")
    })


@turns_api_extension.route('/get_week', methods=['GET'])
class GetWeek(Resource):

    @turns_api_extension.expect(day_model)
    @turns_api_extension.marshal_with(week_turns_model)
    def get(self):
        api_state: ApiState = current_app.config["api_config"]
        db_manager = api_state.db_manager

        # get request dict
        params = dict(request.args)

        day_str: str = params.get('day')
        formatted_day = datetime.datetime.strptime(day_str, DATE_FORMAT)

        week_turns = get_week_turns(formatted_day, db_manager)

        return week_turns
