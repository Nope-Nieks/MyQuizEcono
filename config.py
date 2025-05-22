import os

# Détermine le répertoire de base du projet
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev') # Changez ceci en production!
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dossier d'upload temporaire
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'data', 'temp')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    @staticmethod
    def init_app(app):
        # Créer le dossier d'upload s'il n'existe pas
        # Utiliser app.config.get pour s'assurer que la config est chargée
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)

    # Configuration de la base de données
    # Utiliser DATABASE_URL de Render si disponible (pour PostgreSQL)
    # Sinon (local), utiliser un fichier SQLite app.db à la racine.
    database_url = os.environ.get('DATABASE_URL')
    print("                ")
    print('DATABASE_URL:', database_url)  # Debug: Afficher l'URL de la base de données
    print("                ")
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    if database_url and database_url.startswith("postgres://"):
        # Remplacer postgres:// par postgresql:// pour compatibilité avec SQLAlchemy 2+
        SQLALCHEMY_DATABASE_URI = database_url.replace("postgres://", "postgresql://", 1)
    elif database_url: # Pour d'autres types de DB via DATABASE_URL ou si déjà postgresql://
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Configuration SQLite locale par défaut
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db' 

# Configurations spécifiques par environnement (peuvent être étendues)
class DevelopmentConfig(Config):
    DEBUG = True
    # En développement, on force SQLite si DATABASE_URL n'est pas explicitement défini pour autre chose
    if not os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_app.db' 

class ProductionConfig(Config):
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI est déjà géré par la logique ci-dessus pour DATABASE_URL de Render
    # S'assurer que le SECRET_KEY est bien défini via les variables d'environnement en production
    if Config.SECRET_KEY == 'a_very_secret_key_that_should_be_changed':
        # Cela ne devrait jamais arriver si SECRET_KEY est bien configuré sur Render
        # Mais c'est une sécurité pour éviter d'utiliser la clé par défaut en production.
        raise ValueError("SECRET_KEY doit être défini à une valeur sécurisée en production.")

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig # 'default' pointera vers DevelopmentConfig
} 