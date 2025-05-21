from datetime import datetime
from app import db

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Integer)  # en secondes
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Détails des réponses
    correct_answers = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    
    # Relations
    user = db.relationship('User', backref=db.backref('scores', lazy=True))
    quiz = db.relationship('Quiz', backref=db.backref('scores', lazy=True))
    
    def __init__(self, user_id, quiz_id, score, max_score, correct_answers, total_questions, time_taken=None):
        self.user_id = user_id
        self.quiz_id = quiz_id
        self.score = score
        self.max_score = max_score
        self.percentage = (score / max_score) * 100
        self.correct_answers = correct_answers
        self.total_questions = total_questions
        self.time_taken = time_taken
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'score': self.score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'correct_answers': self.correct_answers,
            'total_questions': self.total_questions,
            'time_taken': self.time_taken,
            'date_attempted': self.date_attempted.isoformat()
        }

    def __repr__(self):
        return f'<Score {self.id}: {self.percentage}%>' 