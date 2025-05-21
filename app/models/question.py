from app import db

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, default=1)
    # Relation avec les réponses
    answers = db.relationship('Answer', back_populates='question', cascade="all, delete-orphan", lazy=True)
    quiz = db.relationship('Quiz', back_populates='questions')

    @staticmethod
    def get_by_id(question_id):
        return Question.query.get(question_id)

    def __repr__(self):
        return f"<Question {self.id}: {self.text[:30]}>"
