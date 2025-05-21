from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from ..utils.pdf_utils import extract_questions_from_pdf, extract_questions_from_text
from ..models.quiz import Quiz
from ..models.question import Question
from ..models.answer import Answer
from ..models.score import Score
from .. import db
import random

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    with db.get_connection() as conn:
        # Récupérer les quiz publics les plus récents
        recent_quizzes = conn.execute('''
            SELECT q.*, u.username as author_name, 
                   (SELECT COUNT(*) FROM questions WHERE quiz_id = q.id) as question_count
            FROM quizzes q
            JOIN users u ON q.user_id = u.id
            WHERE q.is_public = 1
            ORDER BY q.created_at DESC
            LIMIT 6
        ''').fetchall()
        
        # Récupérer les quiz les plus populaires (basé sur le nombre de tentatives)
        popular_quizzes = conn.execute('''
            SELECT q.*, u.username as author_name,
                   COUNT(s.id) as attempt_count,
                   (SELECT COUNT(*) FROM questions WHERE quiz_id = q.id) as question_count
            FROM quizzes q
            JOIN users u ON q.user_id = u.id
            LEFT JOIN scores s ON q.id = s.quiz_id
            WHERE q.is_public = 1
            GROUP BY q.id
            ORDER BY attempt_count DESC
            LIMIT 6
        ''').fetchall()
    
    return render_template('main/index.html',
                         recent_quizzes=recent_quizzes,
                         popular_quizzes=popular_quizzes)

@bp.route('/my-quizzes')
@login_required
def my_quizzes():
    quizzes = Quiz.get_by_user(current_user.id)
    return render_template('main/my_quizzes.html', quizzes=quizzes)

@bp.route('/create-quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        import_type = request.form.get('import_type', 'manual')
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        difficulty = request.form.get('difficulty')
        is_public = request.form.get('is_public') == 'on'

        # Créer le quiz
        quiz = Quiz(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            is_public=is_public,
            user_id=current_user.id
        )
        db.session.add(quiz)
        db.session.flush()  # Pour obtenir l'ID du quiz

        # Gérer l'import des questions selon le type
        if import_type == 'text':
            text_content = request.form.get('text_content')
            delimiter = request.form.get('text_delimiter', '\n')
            questions = extract_questions_from_text(text_content, delimiter)
            _add_questions_to_quiz(quiz.id, questions)

        elif import_type == 'pdf':
            if 'pdf_file' not in request.files:
                flash('Aucun fichier PDF sélectionné', 'error')
                return redirect(request.url)
            
            pdf_file = request.files['pdf_file']
            if pdf_file.filename == '':
                flash('Aucun fichier sélectionné', 'error')
                return redirect(request.url)

            if not pdf_file.filename.endswith('.pdf'):
                flash('Le fichier doit être au format PDF', 'error')
                return redirect(request.url)

            # Sauvegarder le fichier temporairement
            filename = secure_filename(pdf_file.filename)
            temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(temp_path)

            try:
                questions = extract_questions_from_pdf(temp_path)
                _add_questions_to_quiz(quiz.id, questions)
            finally:
                # Supprimer le fichier temporaire
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        db.session.commit()
        flash('Quiz créé avec succès ! Vous pouvez maintenant éditer les questions.', 'success')
        return redirect(url_for('main.edit_questions', quiz_id=quiz.id))

    return render_template('main/create_quiz.html')

def _add_questions_to_quiz(quiz_id, questions):
    """Ajoute les questions et réponses au quiz."""
    for q_data in questions:
        question = Question(
            quiz_id=quiz_id,
            text=q_data['question'],
            points=1  # Points par défaut
        )
        db.session.add(question)
        db.session.flush()

        for answer_text in q_data['answers']:
            answer = Answer(
                question_id=question.id,
                text=answer_text,
                is_correct=False  # À définir par l'utilisateur plus tard
            )
            db.session.add(answer)

@bp.route('/quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz:
        flash('Quiz non trouvé', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('main/view_quiz.html', quiz=quiz)

@bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        flash('Quiz non trouvé ou accès non autorisé', 'error')
        return redirect(url_for('main.my_quizzes'))

    if request.method == 'POST':
        quiz.title = request.form.get('title')
        quiz.description = request.form.get('description')
        quiz.category = request.form.get('category')
        quiz.difficulty = request.form.get('difficulty')
        quiz.is_public = request.form.get('is_public') == 'on'
        
        db.session.commit()
        flash('Quiz mis à jour avec succès !', 'success')
        return redirect(url_for('main.view_quiz', quiz_id=quiz.id))

    return render_template('main/edit_quiz.html', quiz=quiz)

@bp.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        flash('Quiz non trouvé ou accès non autorisé', 'error')
        return redirect(url_for('main.my_quizzes'))

    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz supprimé avec succès !', 'success')
    return redirect(url_for('main.my_quizzes'))

@bp.route('/quiz/<int:quiz_id>/edit-questions', methods=['GET', 'POST'])
@login_required
def edit_questions(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        flash('Quiz non trouvé ou accès non autorisé', 'error')
        return redirect(url_for('main.my_quizzes'))

    if request.method == 'POST':
        questions_data = request.form.to_dict()
        
        # Traiter les données du formulaire
        for question_id, data in questions_data.items():
            if question_id.startswith('questions[') and question_id.endswith('][text]'):
                # Extraire l'ID de la question
                q_id = question_id.split('[')[1].split(']')[0]
                
                # Mettre à jour ou créer la question
                if q_id.startswith('new_'):
                    question = Question(
                        quiz_id=quiz.id,
                        text=data,
                        points=1
                    )
                    db.session.add(question)
                    db.session.flush()
                else:
                    question = Question.get_by_id(int(q_id))
                    if question:
                        question.text = data

                # Mettre à jour les réponses
                answers_data = {k: v for k, v in questions_data.items() 
                              if k.startswith(f'questions[{q_id}][answers]')}
                correct_answer = questions_data.get(f'questions[{q_id}][correct_answer]')

                for answer_id, answer_text in answers_data.items():
                    a_id = answer_id.split('[')[-1].split(']')[0]
                    
                    if a_id.startswith('new_'):
                        answer = Answer(
                            question_id=question.id,
                            text=answer_text,
                            is_correct=(a_id == correct_answer)
                        )
                        db.session.add(answer)
                    else:
                        answer = Answer.get_by_id(int(a_id))
                        if answer:
                            answer.text = answer_text
                            answer.is_correct = (a_id == correct_answer)

        # Supprimer les questions et réponses qui ne sont plus présentes
        existing_questions = {str(q.id): q for q in quiz.questions}
        for q_id in list(existing_questions.keys()):
            if f'questions[{q_id}][text]' not in questions_data:
                db.session.delete(existing_questions[q_id])

        db.session.commit()
        flash('Questions mises à jour avec succès !', 'success')
        return redirect(url_for('main.view_quiz', quiz_id=quiz.id))

    return render_template('main/edit_questions.html', quiz=quiz)

@bp.route('/quiz/<int:quiz_id>/train', methods=['GET', 'POST'])
@login_required
def train_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz:
        flash('Quiz non trouvé', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        score = 0
        total_questions = len(quiz.questions)
        answers = request.form.to_dict()
        
        # Calculer le score
        for question in quiz.questions:
            answer_id = answers.get(f'question_{question.id}')
            if answer_id:
                answer = Answer.get_by_id(int(answer_id))
                if answer and answer.is_correct:
                    score += 1

        # Sauvegarder le score
        score_record = Score(
            user_id=current_user.id,
            quiz_id=quiz.id,
            score=score,
            total_questions=total_questions,
            mode='train'
        )
        db.session.add(score_record)
        db.session.commit()

        return render_template('main/train_results.html', 
                             quiz=quiz, 
                             score=score, 
                             total=total_questions,
                             answers=answers)

    # Mélanger les questions et réponses
    questions = list(quiz.questions)
    random.shuffle(questions)
    for question in questions:
        answers = list(question.answers)
        random.shuffle(answers)
        question.answers = answers

    return render_template('main/train_quiz.html', quiz=quiz, questions=questions) 