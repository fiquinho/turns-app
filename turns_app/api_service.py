# Swagger API with Flask
import json

from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
from flask_restx import Api, fields, Resource

from turns_app.api.turns import turns_api_blueprint as turns_api
from turns_app.api.users import users_api_blueprint as users_api
from turns_app.defaults import CONFIGS_PATH
from turns_app.model.turns import Turn
from turns_app.utils.config_utils import load_app_config_from_toml, AppConfig
from utils.flask_utils import update_werkzeug_reloader, ApiState

update_werkzeug_reloader()
app = Flask(__name__)
CORS(app)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Turn):
            return obj.to_str_dict()
        return json.JSONEncoder.default(self, obj)


# Override default JSON encoder
json.JSONEncoder = CustomJSONEncoder


api_blueprint = Blueprint('turns_app_api', __name__)
api_extension = Api(
    api_blueprint,
    title='Turns APP API',
    version='0.1',
    description='Turns PP API for general services',
    doc='/doc'
)


heartbeat_model = api_extension.model('Heartbeat', {
    "status": fields.String(required=True, description="Service status"),
    "message": fields.String(required=True, description="Service message")
})


business_info_model = api_extension.model('BusinessInfo', {
    "name": fields.String(required=True, description="Business name"),
    "start_time": fields.String(required=True, description="Business address"),
    "end_time": fields.String(required=True, description="Business phone"),
    "min_module_time": fields.Integer(required=True, description="Business minimum module time in minutes"),
    "offices": fields.List(fields.String, required=True, description="List of office names")
})


@api_extension.route('/heartbeat', methods=['GET'])
class Heartbeat(Resource):

    @api_extension.marshal_with(heartbeat_model)
    def get(self):
        return jsonify({'status': 'ok',
                        'message': 'The service is running'})


@api_extension.route('/business_info', methods=['GET'])
class BusinessInfo(Resource):

    @api_extension.marshal_with(business_info_model)
    def get(self):
        app_config: AppConfig = AppConfig.get_instance()  # type: ignore
        bc = app_config.business
        return bc.to_dict()


app.register_blueprint(api_blueprint)
app.register_blueprint(turns_api)
app.register_blueprint(users_api)


def main():
    app_config = load_app_config_from_toml(CONFIGS_PATH / 'app_config.dev.toml')
    api_config = ApiState.from_app_config(app_config)
    app.config["api_config"] = api_config
    app.run(debug=True)


if __name__ == '__main__':
    main()
