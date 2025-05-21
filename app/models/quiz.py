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
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy='dynamic')

    def __repr__(self):
        return f'<Quiz {self.title}>' 