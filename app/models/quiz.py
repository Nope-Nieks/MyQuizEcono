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

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=1)
    
    # Relations
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Question {self.id}>'

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False)
    
    # Relations
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __repr__(self):
        return f'<Answer {self.id}>' 