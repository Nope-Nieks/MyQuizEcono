from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import sqlite3
from contextlib import contextmanager
import os
from .models.user import User
from .models.quiz import Quiz
from .models.question import Question
from .models.answer import Answer
from .models.score import Score

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.ensure_db_directory()

    def ensure_db_directory(self):
        db_dir = os.path.dirname(self.db_file)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS quizzes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_public BOOLEAN DEFAULT 1,
                    category TEXT,
                    difficulty TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );

                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quiz_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    order_num INTEGER NOT NULL,
                    points INTEGER DEFAULT 1,
                    FOREIGN KEY (quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    order_num INTEGER NOT NULL,
                    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    quiz_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    max_score INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    correct_answers INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    time_taken INTEGER,
                    date_attempted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
                );

                CREATE TRIGGER IF NOT EXISTS update_quiz_timestamp 
                AFTER UPDATE ON quizzes
                BEGIN
                    UPDATE quizzes SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.id;
                END;
            ''')

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

    # Import des modèles ici, après l'init de db
    from app.models import user, quiz, question, answer, score

    # Import et enregistrement des blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    # ... (autres blueprints si besoin)

    with app.app_context():
        db.create_all()

    return app 