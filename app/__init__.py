import logging
import os

import waitress
from flask import Flask, request

from app.api.util import add_entity_to_db, add_bultin_admin_user
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
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)

    @app.before_request
    def log_the_request():
        logging.info(
            '\t'.join([str(e) for e in [request.args, request.access_route, request.cookies.get('SessionCookie'),
                                        request.headers.get('User-Agent')]]))

    # @app.after_request
    # def log_the_response(response):
    #     return response

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
    return app


if __name__ == '__main__':
    waitress.serve(create_app(config_class=Config), host="127.0.0.1", port=int(os.getenv("SERVICE_PORT")))
    # create_app(config_class=Config).run()
