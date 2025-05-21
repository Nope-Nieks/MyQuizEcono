from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

def create_initial_user(app, username, email, password):
    with app.app_context():
        from app.models.user import User
        if User.query.filter_by(username=username).first() is None:
            print(f"Création de l'utilisateur initial : {username}")
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Utilisateur {username} (ID: {user.id}) créé.")
        else:
            print(f"L'utilisateur initial '{username}' existe déjà.")

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
        if os.environ.get('RENDER_INSTANCE_ID') and config_name != 'production':
            config_name = 'production' 
        elif config_name not in ['development', 'production']:
            config_name = 'development'

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    if hasattr(config[config_name], 'init_app'):
        config[config_name].init_app(app)

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
        if app.config.get('ENV') == 'production' or config_name == 'production':
            create_initial_user(app, 'Nieks', 'nicolas.vanherpen@gmail.com', 'Vanherpen1')

    # Enregistrement conditionnel des commandes CLI
    # if os.environ.get('FLASK_ENV') != 'production': 
        from manage import register_commands
        register_commands(app)

    return app 