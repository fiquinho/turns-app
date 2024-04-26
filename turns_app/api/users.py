from flask import Blueprint, request, current_app, jsonify
from flask_restx import Resource, fields, Api


from turns_app.utils.flask_utils import ApiState


users_api_blueprint = Blueprint('users_api', __name__, url_prefix='/users')
users_api_extension = Api(
    users_api_blueprint,
    title='Users API',
    version='0.1',
    description='Turns API for the turns service',
    doc='/doc'
)

named_user_model = users_api_extension.model('NamedUser', {
    "id": fields.String(required=True, description="User unique identifier"),
    "name": fields.String(required=True, description="User name")
})

user_id_model = users_api_extension.model('UserId', {
    "id": fields.String(required=True, description="User unique identifier")
})

user_model = users_api_extension.model('User', {
    "id": fields.String(required=True, description="User unique identifier"),
    "name": fields.String(required=True, description="User name"),
    "email": fields.String(required=True, description="User email"),
    "phone": fields.String(required=True, description="User phone"),
    "activity": fields.String(required=True, description="User activity")
})

users_model = users_api_extension.model('Users', {
    "users": fields.List(fields.Nested(user_model), required=True, description="List of users")
})


@users_api_extension.route('/get_user', methods=['GET'])
class GetWeek(Resource):

    @users_api_extension.expect(user_id_model)
    @users_api_extension.marshal_with(user_model)
    def get(self):
        api_state: ApiState = current_app.config["api_config"]
        db_manager = api_state.users_manager

        # get request dict
        params = dict(request.args)
        idx: str = params.get('id')
        user = db_manager.get_by_id(idx)

        return user


@users_api_extension.route('/get_users', methods=['GET'])
class GetUsers(Resource):

    @users_api_extension.marshal_with(users_model)
    def get(self):
        api_state: ApiState = current_app.config["api_config"]
        db_manager = api_state.users_manager

        users = db_manager.get_users()

        return {"users": users}
