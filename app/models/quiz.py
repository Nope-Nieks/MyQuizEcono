from datetime import datetime
from app import db

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))  # 'easy', 'medium', 'hard'
    
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', back_populates='quizzes')
    questions = db.relationship('Question', back_populates='quiz', lazy='dynamic', cascade='all, delete-orphan')
    scores = db.relationship('Score', back_populates='quiz', lazy='dynamic')

    @staticmethod
    def get_by_id(quiz_id):
        return Quiz.query.get(quiz_id)

    @staticmethod
    def get_by_user(user_id):
        return Quiz.query.filter_by(user_id=user_id).all()

    def __repr__(self):
        return f'<Quiz {self.title}>'

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def attempt_count(self):
        return self.scores.count() 