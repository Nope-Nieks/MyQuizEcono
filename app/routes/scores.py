from flask import Blueprint, jsonify, request
from app.models.score import Score
from app import db
from flask_login import login_required, current_user

scores_bp = Blueprint('scores', __name__)

@scores_bp.route('/scores', methods=['POST'])
@login_required
def save_score():
    data = request.get_json()
    score = Score(
        user_id=current_user.id,
        quiz_id=data['quiz_id'],
        score=data['score'],
        max_score=data['max_score']
    )
    db.session.add(score)
    db.session.commit()
    return jsonify(score.to_dict()), 201

@scores_bp.route('/scores/user', methods=['GET'])
@login_required
def get_user_scores():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    return jsonify([score.to_dict() for score in scores])

@scores_bp.route('/scores/quiz/<int:quiz_id>', methods=['GET'])
@login_required
def get_quiz_scores(quiz_id):
    scores = Score.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([score.to_dict() for score in scores])

@scores_bp.route('/scores/best', methods=['GET'])
@login_required
def get_best_scores():
    # Récupère le meilleur score pour chaque quiz
    best_scores = db.session.query(
        Score.quiz_id,
        db.func.max(Score.percentage).label('best_percentage')
    ).filter_by(user_id=current_user.id).group_by(Score.quiz_id).all()
    
    return jsonify([{
        'quiz_id': score.quiz_id,
        'best_percentage': score.best_percentage
    } for score in best_scores]) 