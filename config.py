import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    # Render fournit DATABASE_URL, mais Flask-SQLAlchemy attend SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dossier d'upload temporaire (adapte si besoin)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'data', 'temp')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Pour Flask, tu peux utiliser la config de base comme ceci :
config = {
    'default': Config,
    'development': Config,
    'production': Config,
} 