from flask import Flask

from app.models.users import Users
from app.models.scope import Scope
from app.models.state import State
from app.models.valid import Valid

from app.extensions import db
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    create_app(config_class=Config).run()
