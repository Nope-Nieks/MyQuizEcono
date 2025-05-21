from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    # Import des modèles ICI, après l'init de db
    from app.models.user import User
    from app.models.quiz import Quiz
    from app.models.question import Question
    from app.models.answer import Answer
    from app.models.score import Score

    # Import et enregistrement des blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    with app.app_context():
        db.create_all()

    return app 