from app import db

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

    question = db.relationship('Question', back_populates='answers')

    @staticmethod
    def get_by_id(answer_id):
        return Answer.query.get(answer_id)

    def __repr__(self):
        return f"<Answer {self.id}: {self.text[:30]} {'(correct)' if self.is_correct else ''}>"
