# Swagger API with Flask
import json

from flask import Flask, jsonify
from flask_cors import CORS


from turns_app.api.turns import turns_api_blueprint as turns_api
from turns_app.defaults import CONFIGS_PATH
from turns_app.turns import MongoTurnsManager, Turn
from turns_app.utils.config_utils import load_app_config_from_json
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


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({'status': 'ok',
                    'message': 'The service is running'})


app.register_blueprint(turns_api)


def main():
    app_config = load_app_config_from_json(CONFIGS_PATH / 'app_config.dev.json')
    api_config = ApiState(MongoTurnsManager(app_config.mongo))
    app.config["api_config"] = api_config
    app.run(debug=True)


if __name__ == '__main__':
    main()
