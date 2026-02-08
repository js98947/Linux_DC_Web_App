from flask import Flask
from flask_login import LoginManager

from config.settings import Config, DevelopmentConfig, ProductionConfig

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name == "development":
        app.config.from_object(DevelopmentConfig())
    elif config_name == "production":
        app.config.from_object(ProductionConfig())
    else:
        app.config.from_object(Config())

    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.groups import groups_bp
    from app.routes.computers import computers_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(groups_bp, url_prefix="/groups")
    app.register_blueprint(computers_bp, url_prefix="/computers")

    return app
