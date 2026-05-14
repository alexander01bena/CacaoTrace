from flask import Flask
from flask_login import LoginManager
from .config import Config
from .database import db
from .models import User
from .seed import crear_datos_iniciales

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta sección."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    """Crea y configura la aplicación Flask."""

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        crear_datos_iniciales()

    return app
