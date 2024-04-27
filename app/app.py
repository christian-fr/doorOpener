import logging
import os

import waitress
from flask import Flask, request

from app.api.func import add_entity_to_db, add_bultin_admin_user, add_bultin_maintenance_user
from app.models.user import User, Role
from app.models.scope import Scope
from app.models.state import State
from app.models.valid import Valid
from app.models.usage import Usage

from app.extensions import db
from app.util.util import generate_api_key
from config import Config

logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.INFO)


def create_app(config_class=Config):
    assert config_class.SECRET_KEY is not None, "SECRET_KEY env variable not set"

    app = Flask(__name__, template_folder='templates')

    assert config_class.SECRET_KEY != "<SECRET_KEY>", ('secret key not set, default value in '
                                                       '/etc/doorOpener/.env_server found!')

    app.config.from_object(config_class)

    @app.before_request
    def log_the_request():
        logging.info(
            '\t'.join([str(e) for e in [request.args, request.access_route, request.cookies.get('SessionCookie'),
                                        request.headers.get('User-Agent')]]))

    # Initialize Flask extensions here
    db.init_app(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        add_bultin_admin_user()
        add_bultin_maintenance_user()
    return app


def main():
    print("waitress")
    waitress.serve(create_app(config_class=Config), host="127.0.0.1",
                   port=int(os.getenv("SERVICE_PORT")) if os.getenv("SERVICE_PORT") is not None else 5050)


if __name__ == '__main__':
    main()
